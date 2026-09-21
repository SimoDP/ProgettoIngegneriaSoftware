per compilare i codici dei UC1,2,3,4 -> www.planttext.com
### Sequence Diagram

[[UC1.png]]
[[UC2.png]]
[[UC3.png]]
[[UC4.png]]
[[SchemaER.png]]
[[ActivityDiagram.png]]
[[ClassDiagramDelSoftware.png]]

#### UC1
```
@startuml
skinparam maxMessageSize 150
skinparam monochrome true
skinparam shadowing false

title Sequence Diagram: UC1 - Registrazione Rilevazione Glicemica

actor Paziente
boundary "Browser (View)" as View
control "Flask Route\n(MeasurementController)" as Route
entity "MeasurementService\n(Business Logic)" as Service
database "SQLite DB" as DB

== Flusso di Inserimento ==
Paziente -> View: Compila e invia form\n(valore, data, ora, pasto)
activate View
View -> Route: POST /measurement/add
activate Route

Route -> Service: record_measurement(data)
activate Service

Service -> Service: validate_data(data)

alt Dati Non Validi (Flusso Alt. 1.1)
    Service --> Route: Dati non validi (Exception)
    Route --> View: Redirect al form con "Flash Message" di Errore
    View --> Paziente: Mostra form con errori
    
else Dati Validi (Main Flow)
    == Salvataggio Misurazione ==
    Service -> DB: insert_measurement(data)
    activate DB
    DB --> Service: OK (ID generato)
    deactivate DB
    
    == Controllo Soglie (Extension Point 1.2) ==
    Service -> Service: check_thresholds(valore, contesto_pasto)
    
    opt Valori Fuori Soglia (UC: InviaNotificaAllarmeGlicemia)
        Service -> Service: calcola_gravita(valore)
        note right of Service: Es: Gravità MEDIA se leggermente fuori,\nALTA se ipoglicemia
        Service -> DB: create_alert(id_medico, id_paziente, gravita, messaggio)
        activate DB
        DB --> Service: Alert salvato
        deactivate DB
    end
    
    Service --> Route: OK
    deactivate Service
    
    Route --> View: Redirect alla Dashboard con "Flash Message" di Successo
    deactivate Route
    View --> Paziente: Mostra conferma registrazione
    deactivate View
end

@enduml
```



#### UC2
```
@startuml
skinparam maxMessageSize 150
skinparam monochrome true
skinparam shadowing false

title Sequence Diagram: UC2 - Gestione Terapia (con Audit Log)

actor Medico
boundary "Browser (View)" as View
control "Flask Route\n(TherapyController)" as Route
entity "TherapyService\n(Business Logic)" as Service
entity "AuditService\n(Tracciabilità)" as Audit
database "SQLite DB" as DB

== Annullamento (Flusso Alt. 2.2) ==
Medico -> View: Clicca "Annulla"
View -> Route: GET /patient/<id>/dossier
Route -> View: Renderizza pagina fascicolo (nessuna modifica)

== Flusso di Inserimento/Modifica (Main Flow) ==
Medico -> View: Compila e invia form\n(farmaco, dosaggio, frequenza, note)
activate View
View -> Route: POST /therapy/save
activate Route

Route -> Service: save_therapy(data, id_medico, id_paziente)
activate Service

Service -> Service: validate_therapy_data(data)

alt Dati Obbligatori Mancanti (Flusso Alt. 2.1)
    Service --> Route: Validation Error (Campi mancanti)
    Route --> View: Redirect al form con "Flash Message" di Errore
    View --> Medico: Mostra form evidenziando gli errori
    
else Dati Validi (Main Flow)
    == Salvataggio Terapia ==
    Service -> DB: upsert_therapy(data, id_paziente)
    activate DB
    DB --> Service: OK (Terapia aggiornata)
    deactivate DB
    
    == Include: Registra Audit Log (FR12 / NFR2) ==
    Service -> Audit: log_operation(id_medico, "UPDATE_THERAPY", id_paziente)
    activate Audit
    Audit -> DB: insert_audit_record(timestamp, id_medico, action)
    activate DB
    note right of DB: Tabella append-only per\ngarantire l'integrità medico-legale
    DB --> Audit: OK
    deactivate DB
    Audit --> Service: OK
    deactivate Audit
    
    Service --> Route: Successo
    deactivate Service
    
    Route --> View: Redirect al Fascicolo con "Flash Message" di Successo
    deactivate Route
    View --> Medico: Mostra conferma salvataggio terapia
    deactivate View
end

@enduml
```

#### UC3
```
@startuml
skinparam maxMessageSize 150
skinparam monochrome true
skinparam shadowing false

title Sequence Diagram: UC3 - Registrazione Assunzione Farmaco

actor Paziente
boundary "Browser (View)" as View
control "Flask Route\n(IntakeController)" as Route
entity "IntakeService\n(Business Logic)" as Service
entity "TherapyService\n(Verifica)" as TherapySvc
database "SQLite DB" as DB

== Flusso di Registrazione ==
Paziente -> View: Compila e invia form\n(nome farmaco, quantità, data, ora)
activate View
View -> Route: POST /intake/add
activate Route

Route -> Service: record_intake(data)
activate Service

Service -> Service: validate_data(data)

alt Dati Mancanti o Non Validi (Flusso Alt. 3.1)
    Service --> Route: Validation Error (Valori nulli o negativi)
    Route --> View: Redirect al form con "Flash Message" di Errore
    View --> Paziente: Mostra form con errori
    
else Dati Validi (Main Flow)
    == Salvataggio Assunzione ==
    Service -> DB: insert_intake(data)
    activate DB
    DB --> Service: OK
    deactivate DB
    
    note right of Service: L'inserimento azzera implicitamente\nil timer di mancata aderenza\nper questo farmaco (FR13)
    
    == Verifica Coerenza Terapia (Extension Point 3.2) ==
    Service -> TherapySvc: get_active_therapy(id_paziente, nome_farmaco)
    activate TherapySvc
    TherapySvc -> DB: SELECT active_therapy
    activate DB
    DB --> TherapySvc: therapy_details (dose prescritta)
    deactivate DB
    TherapySvc --> Service: therapy_details
    deactivate TherapySvc
    
    Service -> Service: check_consistency(quantità_assunta, dose_prescritta)
    
    opt Incongruenza Terapia (MostraAvvisoIncoerenza)
        note right of Service: Il sistema NON blocca il salvataggio,\nma genera un avviso (FR6)
        Service -> DB: create_alert(id_medico, id_paziente, "WARNING", "Incoerenza dose")
        activate DB
        DB --> Service: Alert salvato
        deactivate DB
        Service --> Route: Tuple (Success=True, Warning=True)
    else Terapia Coerente
        Service --> Route: Tuple (Success=True, Warning=False)
    end
    deactivate Service
    
    alt Incoerenza rilevata
        Route --> View: Redirect al Diario con "Flash Message" (Warning Giallo)
    else Assunzione perfetta
        Route --> View: Redirect al Diario con "Flash Message" (Successo Verde)
    end
    
    deactivate Route
    View --> Paziente: Mostra UI aggiornata
    deactivate View
end

@enduml
```
#### UC4
```
@startuml
skinparam maxMessageSize 150
skinparam monochrome true
skinparam shadowing false

title Sequence Diagram: UC4 - Autenticazione al sistema (Login)

actor Utente
boundary "Browser (View)" as View
control "Flask Route\n(AuthController)" as Route
entity "AuthService\n(Security)" as Service
database "SQLite DB" as DB

Utente -> View: Inserisce email e password
activate View
View -> Route: POST /login
activate Route

Route -> Service: authenticate(email, password_in_chiaro)
activate Service

Service -> DB: SELECT * FROM users WHERE email = ?
activate DB
DB --> Service: Dati Utente (incluso password_hash, role)
deactivate DB

alt Utente non trovato (Flusso Alt. 4.1)
    Service --> Route: Utente inesistente
    Route --> View: Redirect con errore "Credenziali non valide"
else Utente trovato
    Service -> Service: check_hash(password_in_chiaro, password_hash)
    
    alt Password Errata (Flusso Alt. 4.2)
        Service --> Route: Password errata
        Route --> View: Redirect con errore "Credenziali non valide"
        note right of Route: Errore generico per\nevitare User Enumeration
    else Password Corretta (Main Flow)
        Service --> Route: Oggetto User autenticato
        
        Route -> Route: Inizializza Sessione (Flask Session)\nImposta Cookie Sicuro
        
        alt role == 0 (Paziente)
            Route --> View: Redirect /patient/dashboard
        else role == 1 (Medico)
            Route --> View: Redirect /doctor/dashboard
        else role == 2 (Admin)
            Route --> View: Redirect /admin/dashboard
        end
        
    end
end
deactivate Service
deactivate Route
View --> Utente: Mostra Area Riservata
deactivate View

@enduml
```



#### Schema ER/ERD
```
@startuml
skinparam monochrome true
skinparam shadowing false
hide circle

title ER Diagram: Database Modello Dati (SQLite / Python)

entity "users" {
  * id : INTEGER <<PK>>
  --
  * email : VARCHAR(100) <<UNIQUE>>
  * password_hash : VARCHAR(255)
  * first_name : VARCHAR(50)
  * last_name : VARCHAR(50)
  * role : INTEGER (0=Patient, 1=Doctor, 2=Admin)
  * is_active : BOOLEAN
}

entity "patients" {
  * user_id : INTEGER <<PK, FK>>
  --
  * doctor_id : INTEGER <<FK>>
  date_of_birth : DATE
  gender : CHAR(1)
}

entity "medical_records" {
  * patient_id : INTEGER <<PK, FK>>
  --
  is_smoker : BOOLEAN
  has_alcohol_issues : BOOLEAN
  has_hypertension : BOOLEAN
  has_obesity : BOOLEAN
}

entity "clinical_events" {
  * id : INTEGER <<PK>>
  --
  * patient_id : INTEGER <<FK>>
  * event_type : VARCHAR (SYMPTOM, PATHOLOGY, OTHER_DRUG)
  * description : TEXT
  start_date : DATE
  end_date : DATE
}

entity "therapies" {
  * id : INTEGER <<PK>>
  --
  * patient_id : INTEGER <<FK>>
  * doctor_id : INTEGER <<FK>>
  * drug_name : VARCHAR(100)
  * daily_doses : INTEGER
  * quantity_per_dose : REAL
  instructions : VARCHAR(255)
  * is_active : BOOLEAN
  start_date : DATE
}

entity "glycemic_readings" {
  * id : INTEGER <<PK>>
  --
  * patient_id : INTEGER <<FK>>
  * glucose_level : INTEGER
  * reading_datetime : DATETIME
  * meal_context : VARCHAR (BEFORE_MEAL, AFTER_MEAL)
}

entity "medication_intakes" {
  * id : INTEGER <<PK>>
  --
  * patient_id : INTEGER <<FK>>
  * therapy_id : INTEGER <<FK>>
  * intake_datetime : DATETIME
  * quantity_taken : REAL
}

entity "alerts" {
  * id : INTEGER <<PK>>
  --
  * doctor_id : INTEGER <<FK>>
  * patient_id : INTEGER <<FK>>
  * severity : VARCHAR (WARNING, CRITICAL)
  * message : TEXT
  * is_resolved : BOOLEAN
  * created_at : DATETIME
}

entity "messages" {
  * id : INTEGER <<PK>>
  --
  * sender_id : INTEGER <<FK>>
  * receiver_id : INTEGER <<FK>>
  * content : TEXT
  * sent_at : DATETIME
}

users ||--o| patients : "is a"
users ||--o{ patients : "doctor supervises"
patients ||--|| medical_records : "has"
patients ||--o{ clinical_events : "reports"
patients ||--o{ therapies : "follows"
patients ||--o{ glycemic_readings : "logs"
patients ||--o{ medication_intakes : "records"
therapies ||--o{ medication_intakes : "verified by"
users ||--o{ alerts : "doctor receives"
users ||--o{ messages : "sends/receives"

@enduml
```


#### Codice SQL/DDL
```
-- Tabella Base per tutti gli utenti del sistema (Auth)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role INTEGER NOT NULL, -- 0: Paziente, 1: Medico, 2: Admin
    is_active BOOLEAN DEFAULT 1
);

-- Tabella specifica per i dettagli anagrafici dei Pazienti
CREATE TABLE patients (
    user_id INTEGER PRIMARY KEY,
    doctor_id INTEGER NOT NULL,
    date_of_birth DATE,
    gender CHAR(1),
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(doctor_id) REFERENCES users(id)
);

-- Fascicolo del Paziente (Fattori di rischio stabili)
CREATE TABLE medical_records (
    patient_id INTEGER PRIMARY KEY,
    is_smoker BOOLEAN DEFAULT 0,
    has_alcohol_issues BOOLEAN DEFAULT 0,
    has_hypertension BOOLEAN DEFAULT 0,
    has_obesity BOOLEAN DEFAULT 0,
    FOREIGN KEY(patient_id) REFERENCES patients(user_id)
);

-- FR3.2: Sintomi, Patologie Pregresse e Terapie Concomitanti
CREATE TABLE clinical_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    event_type VARCHAR(20) NOT NULL, -- 'SYMPTOM', 'PATHOLOGY', 'OTHER_DRUG'
    description TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    FOREIGN KEY(patient_id) REFERENCES patients(user_id)
);

-- Terapie prescritte dal Medico (FR5)
CREATE TABLE therapies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    drug_name VARCHAR(100) NOT NULL,
    daily_doses INTEGER NOT NULL,
    quantity_per_dose REAL NOT NULL,
    instructions VARCHAR(255),
    is_active BOOLEAN DEFAULT 1,
    start_date DATE NOT NULL,
    FOREIGN KEY(patient_id) REFERENCES patients(user_id),
    FOREIGN KEY(doctor_id) REFERENCES users(id)
);

-- Rilevazioni Glicemiche (FR3.1)
CREATE TABLE glycemic_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    glucose_level INTEGER NOT NULL,
    reading_datetime DATETIME NOT NULL,
    meal_context VARCHAR(20) NOT NULL, -- 'BEFORE_MEAL', 'AFTER_MEAL'
    FOREIGN KEY(patient_id) REFERENCES patients(user_id)
);

-- Assunzioni Farmaci da parte del Paziente (FR4 e controllo FR6)
CREATE TABLE medication_intakes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    therapy_id INTEGER NOT NULL,
    intake_datetime DATETIME NOT NULL,
    quantity_taken REAL NOT NULL,
    FOREIGN KEY(patient_id) REFERENCES patients(user_id),
    FOREIGN KEY(therapy_id) REFERENCES therapies(id)
);

-- Avvisi verso il Medico (FR10, FR13)
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    severity VARCHAR(20) NOT NULL, -- 'WARNING', 'CRITICAL'
    message TEXT NOT NULL,
    is_resolved BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(doctor_id) REFERENCES users(id),
    FOREIGN KEY(patient_id) REFERENCES patients(user_id)
);

-- Chat / Comunicazioni Medico-Paziente (FR11)
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(sender_id) REFERENCES users(id),
    FOREIGN KEY(receiver_id) REFERENCES users(id)
);
```

#### Activity Diagram
```
@startuml
skinparam monochrome true
skinparam shadowing false

title Activity Diagram: Interazione del Medico (Navigazione e Prescrizione)

start

:Medico effettua il Login;
:Il sistema reindirizza a /doctor/dashboard;
:Visualizza Dashboard Medico\n(Elenco Pazienti e Avvisi aperti);

if (Quale area seleziona?) then (Seleziona un Paziente)
  :Il sistema carica i dati base del paziente;
  :Visualizza Schermata "Dettaglio Paziente";
  
  fork
    :Clicca "Fascicolo Medico";
    :Consulta/Modifica fattori\ndi rischio e patologie;
  fork again
    :Clicca "Andamento Clinico";
    :Consulta grafici e storico\nrilevazioni glicemiche;
  fork again
    :Clicca "Prescrivi Terapia";
    repeat :Compila Form Prescrizione\n(Farmaco, Dosi, Note);
      :Invia i dati (POST /therapy/save);
      if (I dati sono validi?) then (Sì)
        :Salvataggio nel Database;
        :Generazione Audit Log;
        :Imposta "Flash Message" di Successo;
        break
      else (No - Campi mancanti)
        :Imposta "Flash Message" di Errore;
      endif
    repeat while (Ritorna al form pre-compilato)
  end fork
  
else (Seleziona un Avviso)
  :Visualizza dettagli Alert\n(es. Paziente con Glicemia Alta);
  :Segna l'Avviso come "Risolto/Preso in carico";
endif

:Ritorna al Dettaglio Paziente o Dashboard;

stop
@enduml
```

#### Class Diagram Del Software
```
@startuml
skinparam monochrome true
skinparam shadowing false
skinparam classAttributeIconSize 0

title Class Diagram: Architettura Software (Python / Flask)

package "Presentation Layer (Flask Blueprints/Routes)" {
    class AuthController <<Blueprint>> {
        + login()
        + logout()
    }
    class PatientController <<Blueprint>> {
        + patient_dashboard()
        + log_measurement()
        + log_intake()
    }
    class DoctorController <<Blueprint>> {
        + doctor_dashboard()
        + view_patient_dossier()
        + prescribe_therapy()
    }
}

package "Business Logic Layer (Services)" {
    class AuthService <<Service>> {
        + authenticate(email, pwd): User
        + check_password_hash()
    }
    class MeasurementService <<Service>> {
        + record_measurement(data): bool
        - check_thresholds(val, context)
        - calculate_severity(val): str
    }
    class TherapyService <<Service>> {
        + save_therapy(data): bool
        + get_active_therapy(patient_id, drug): Therapy
        + check_intake_consistency(intake, presc)
    }
    class AuditService <<Service>> {
        + log_operation(doc_id, action, pat_id)
    }
}

package "Data Access Layer (DAOs)" {
    class DatabaseManager <<Singleton>> {
        - conn: sqlite3.Connection
        + get_connection(): Connection
        + execute_query(query, params)
        + fetch_all(query, params)
    }
    class UserDAO <<DAO>> {
        + get_by_email(email): User
    }
    class MeasurementDAO <<DAO>> {
        + insert(data)
        + get_by_patient(patient_id): list
    }
    class TherapyDAO <<DAO>> {
        + upsert(data)
    }
    class AlertDAO <<DAO>> {
        + create_alert(data)
    }
}

package "Model Layer (Data Classes)" {
    class User {
        + id: int
        + email: str
        + role: int
    }
    class Measurement {
        + id: int
        + glucose_level: int
        + meal_context: str
    }
    class Therapy {
        + id: int
        + drug_name: str
        + daily_doses: int
    }
}

' Relazioni tra Controller e Service (Dependency Injection / Uso)
AuthController --> AuthService
PatientController --> MeasurementService
PatientController --> TherapyService
DoctorController --> TherapyService

' Relazioni tra Service e DAO
AuthService --> UserDAO
MeasurementService --> MeasurementDAO
MeasurementService --> AlertDAO
TherapyService --> TherapyDAO
TherapyService --> AuditService

' Relazioni tra DAO e DB Manager
UserDAO --> DatabaseManager
MeasurementDAO --> DatabaseManager
TherapyDAO --> DatabaseManager
AlertDAO --> DatabaseManager

' Relazioni DAO e Models
UserDAO ..> User : "Returns/Uses"
MeasurementDAO ..> Measurement
TherapyDAO ..> Therapy

@enduml
```






#### Testi di Architettura, Pattern e Test

E' un testo da inserire alla fine del file di design e riflette l'architettura che abbiamo scelto.
## 6. Architettura e Pattern Software

### 6.1 Stili Architetturali Adottati
Il sistema è stato progettato seguendo un'architettura **Client-Server** basata sul web, dove il client (un qualsiasi browser web) funge da *Thin Client*, demandando tutta l'elaborazione e la validazione dei dati al server centrale.

A livello applicativo, il codice backend (implementato in Python tramite il framework Flask) segue rigorosamente un'architettura **Layered (a livelli)** combinata con il pattern architetturale **MVC (Model-View-Controller)**:
*   **Presentation Layer (Controller & View):** Implementato tramite i *Blueprint* di Flask e i template *Jinja2*. Questo livello si occupa esclusivamente di intercettare le richieste HTTP (GET/POST), estrarre i parametri, richiamare i servizi sottostanti e restituire la pagina HTML aggiornata (o messaggi di "Flash" in caso di errore).
*   **Business Logic Layer (Service):** Costituisce il cuore dell'applicazione. Classi come `MeasurementService` o `TherapyService` contengono tutte le regole cliniche (es. calcolo soglie glicemiche, calcolo coerenza terapie, generazione degli alert). Questo garantisce che la logica di business sia totalmente slegata dall'interfaccia web e riutilizzabile.
*   **Data Access Layer (Data):** Si occupa della persistenza sul database relazionale (SQLite) tramite query SQL incapsulate, isolando il resto del sistema dai dettagli del database.

### 6.2 Design Pattern Utilizzati
Per garantire manutenibilità, basso accoppiamento e alta coesione del codice, sono stati adottati i seguenti Design Pattern:
1.  **DAO (Data Access Object):** Ogni entità principale ha il suo DAO dedicato (es. `UserDAO`, `TherapyDAO`). Il resto dell'applicazione non esegue mai query SQL dirette, ma chiama i metodi esposti dai DAO (es. `TherapyDAO.upsert(data)`). Questo permette di centralizzare la logica di accesso ai dati e prevenire attacchi di *SQL Injection*.
2.  **Singleton:** Utilizzato per la classe `DatabaseManager`. Essendo SQLite basato su un singolo file locale, il pattern Singleton garantisce che in tutta l'applicazione esista un solo "pool" o gestore della connessione al database, evitando lock concorrenziali sul file o memory leaks dovuti a connessioni rimaste aperte.
3.  **Service Layer Pattern:** L'introduzione di classi "Service" agisce da *Facade* per i Controller. Un Controller non deve sapere in quante tabelle va salvato un dato; chiama semplicemente `TherapyService.save_therapy()`, il quale orchestra internamente l'aggiornamento della terapia tramite `TherapyDAO` e la scrittura dell'audit tramite `AuditService`.
4.  **Observer (Implementazione semplificata per Audit/Alert):** L'innesco degli allarmi (es. per glicemia fuori soglia) non avviene sporcando il codice di base, ma estendendolo logicamente. Quando un servizio salva un dato anomalo, "notifica" immediatamente la generazione di un alert nel database senza interrompere il normale flusso lato utente.

---

## 7. Piano di Testing (Test Plan)

La fase di validazione e verifica del software (V&V) verrà condotta combinando tecniche di collaudo *White-Box* (a livello di codice) e *Black-Box* (a livello di requisiti e utente), al fine di garantire la totale aderenza alla Matrice di Tracciabilità definita nella sezione Requisiti.

### 7.1 Unit Testing
Gli Unit Test si concentreranno sull'isolamento e la verifica dei singoli componenti del **Business Logic Layer**. Utilizzando il framework nativo `unittest` (o `pytest`), verranno scritte suite di test per validare le regole core senza la necessità di interrogare il database reale (utilizzando oggetti *Mock*).
Esempi di Unit Test previsti:
*   **Test Calcolo Soglie Glicemiche:** Verificare che `MeasurementService` classifichi correttamente un valore di 150 mg/dL come "Normale" se *dopo i pasti*, e come "Warning" se *a digiuno*.
*   **Test Coerenza Terapie:** Verificare che passando al `TherapyService` un'assunzione di 20 unità rispetto a una prescrizione di 10 unità, il sistema generi il corretto flag di discordanza.
*   **Test Validazione Input:** Passaggio di stringhe vuote, valori negativi per la glicemia o formati data errati ai vari Service per assicurarsi che vengano sollevate le corrette eccezioni controllate (es. `ValueError`).

### 7.2 System & Integration Testing
I test di sistema mirano a verificare il comportamento globale dell'applicazione assemblando tutti i livelli (Database + Service + Route). Per farlo in modo automatizzato e ripetibile, verrà sfruttato il `test_client()` fornito da Flask, che permette di simulare richieste HTTP complete.
Esempi di Integration/System Test previsti:
*   **Test Accesso Negato:** Simulazione di una richiesta `GET /doctor/dashboard` senza cookie di sessione valido (o con ruolo Paziente). Si verifica che il sistema restituisca un HTTP 302 Redirect alla pagina di Login.
*   **Test Flusso Alert Medico:** Simulazione completa (`POST`) di un paziente che inserisce un valore di glicemia critico. Il test verificherà nel database di test che la riga in `glycemic_readings` sia stata creata correttamente E che contestualmente esista un nuovo record nella tabella `alerts` associato al medico curante.
*   **Test Integrità DB (Audit Log):** Verifica che, a seguito della simulazione di una modifica della terapia da parte del medico, la tabella degli eventi clinici si aggiorni correttamente e venga generato un record tracciabile associato all'ID del medico.

---
