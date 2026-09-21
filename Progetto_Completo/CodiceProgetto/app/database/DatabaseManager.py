import sqlite3
import os
import threading
from typing import Optional, List, Dict, Any, Tuple

class DatabaseManager:
    """
    Singleton DatabaseManager for SQLite connections.
    Thread-safe connection management using thread-local storage.
    Enforces foreign keys and returns dictionary-like rows.
    """
    _instance: Optional['DatabaseManager'] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls, db_path: Optional[str] = None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_path: Optional[str] = None):
          if db_path is not None and hasattr(self, 'db_path') and self.db_path != db_path:
              # Se viene passato un percorso diverso (es. ambiente di test), aggiorna e chiudi la vecchia connessione
              self.close_connection()
              self.db_path = db_path

          if self._initialized:
              return

          # Default database path
          if db_path is None:
              base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
              self.db_path = os.path.join(base_dir, 'database', 'telemedicine.db')
          else:
              self.db_path = db_path

          self._local = threading.local()
          self._initialized = True

    def get_connection(self) -> sqlite3.Connection:
        """
        Returns a thread-local SQLite connection.
        Enables foreign keys and sets row_factory to sqlite3.Row.
        """
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

            conn = sqlite3.connect(
                self.db_path,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                check_same_thread=False
            )
            # Enable Foreign Keys explicitly for every connection
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.row_factory = sqlite3.Row
            self._local.connection = conn

        return self._local.connection

    def close_connection(self):
        """Closes the connection for the current thread."""
        if hasattr(self._local, 'connection') and self._local.connection is not None:
            self._local.connection.close()
            self._local.connection = None

    def execute_query(self, query: str, params: Tuple = ()) -> int:
        """
        Executes an INSERT, UPDATE, or DELETE query and commits.
        Returns the lastrowid or rowcount.
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            last_id = cursor.lastrowid
            return last_id if last_id else cursor.rowcount
        except sqlite3.Error as e:
            conn.rollback()
            raise e

    def fetch_all(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """Executes a SELECT query and returns all matching rows."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Row]:
        """Executes a SELECT query and returns the first matching row or None."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

    def init_db(self, schema_path: Optional[str] = None):
        """Initializes database schema from schema.sql."""
        if schema_path is None:
            schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')

        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_script = f.read()

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.executescript(schema_script)
        conn.commit()
