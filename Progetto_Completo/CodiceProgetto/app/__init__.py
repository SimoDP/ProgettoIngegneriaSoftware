import os
from flask import Flask, redirect, url_for, session
from app.database.DatabaseManager import DatabaseManager
from app.controllers import auth_bp, patient_bp, doctor_bp, admin_bp

def create_app(test_config=None) -> Flask:
    """
    Application Factory for the Telemedicine Flask App.
    Initializes database, registers blueprints, and sets up session management.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Application Configuration
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'telemedicina-diabetes-secret-key-2026'),
        DATABASE_PATH=os.path.join(base_dir, 'database', 'telemedicine.db')
    )

    if test_config:
        app.config.update(test_config)

    # Initialize Database Schema if not already created
    db_manager = DatabaseManager(app.config['DATABASE_PATH'])
    db_manager.init_db()

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(admin_bp)

    # Root route redirect based on authentication and role
    @app.route('/')
    def index():
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        role = session.get('role')
        if role == 0:
            return redirect(url_for('patient.dashboard'))
        elif role == 1:
            return redirect(url_for('doctor.dashboard'))
        elif role == 2:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('auth.login'))

    # Teardown connection per request thread
    @app.teardown_appcontext
    def close_db_connection(exception=None):
        db_manager.close_connection()

    # CLI command to initialize database schema
    @app.cli.command('init-db')
    def init_db_command():
        """CLI command: flask init-db"""
        db_manager.init_db()
        print("Database schema inizializzato con successo.")

    # CLI command to seed default users and sample data
    @app.cli.command('seed-db')
    def seed_db_command():
        """CLI command: flask seed-db"""
        from seed_db import seed_database
        seed_database(app.config['DATABASE_PATH'])

    return app
