# Sistema di Telemedicina per la Gestione del Diabete di Tipo 2

Progetto software accademico per l'esame di **Ingegneria del Software (A.A. 2024-2025)**.  
Il sistema consente il monitoraggio clinico a distanza di pazienti affetti da Diabete di Tipo 2, la prescrizione personalizzata delle terapie, la verifica dinamica della coerenza delle dosi assunte e dell'aderenza terapeutica, la gestione intelligente degli allarmi clinici differenziati per gravità e il tracciamento inalterabile (Audit Trail) di tutte le operazioni mediche.

---

## Indice
1. [Dominio Clinico e Obiettivi del Sistema](#1-dominio-clinico-e-obiettivi-del-sistema)
2. [Stack Tecnologico e Vincoli Architetturali](#2-stack-tecnologico-e-vincoli-architetturali)
3. [Design Pattern Implementati](#3-design-pattern-implementati)
4. [Struttura Completa del Progetto](#4-struttura-completa-del-progetto)
5. [Guida Rapida all'Installazione e Setup](#5-guida-rapida-allinstallazione-e-setup)
6. [Credenziali Predefinite per il Test](#6-credenziali-predefinite-per-il-test)
7. [Guida Operativa ai Flussi Utente (Come Usare il Sistema)](#7-guida-operativa-ai-flussi-utente-come-usare-il-sistema)
   - [7.1 Flusso Amministratore](#71-flusso-amministratore-fr2-uc5)
   - [7.2 Flusso Paziente](#72-flusso-paziente-fr31-fr32-fr4-fr6-fr9-fr11-uc1-uc3-uc6-uc9)
   - [7.3 Flusso Medico Diabetologo](#73-flusso-medico-diabetologo-fr5-fr7-fr8-fr10-fr12-fr13-uc2-uc7-uc8)
8. [Regole di Business e Logica Clinica Core](#8-regole-di-business-e-logica-clinica-core)
9. [Integrità Medico-Legale: Audit Log Append-Only](#9-integrità-medico-legale-audit-log-append-only)
10. [Test Automatici e Matrice di Tracciabilità](#10-test-automatici-e-matrice-di-tracciabilità)

---

## 1. Dominio Clinico e Obiettivi del Sistema

Il Diabete di Tipo 2 è una malattia cronica caratterizzata da iperglicemia dovuta a un'insufficiente secrezione o azione dell'insulina. La gestione ottimale richiede:
- Monitoraggio costante della glicemia (prima e dopo i pasti).
- Rigorosa aderenza alle prescrizioni farmacologiche (ipoglicemizzanti orali come Metformina o insuline).
- Tempestiva identificazione delle crisi ipoglicemiche (gravi) e iperglicemiche.
- Comunicazione continua e tracciata tra paziente e diabetologo curante.

---

## 2. Stack Tecnologico e Vincoli Architetturali

Il software è stato sviluppato rispettando in maniera tassativa le specifiche didattiche e i vincoli del corso:
- **Linguaggio**: Python 3.11 (Orientato agli Oggetti puro).
- **Framework Web**: Flask (architettura scalabile basata su **Flask Blueprints**).
- **Database**: SQLite3 nativo (`sqlite3`).
  - **DIVIETO DI ORM RISPETTATO**: Non è stato usato SQLAlchemy o altro ORM. Ogni interazione con il database avviene tramite **SQL raw sicuro e parametrizzato** all'interno del pattern DAO.
- **Frontend & Accessibilità (NFR3)**: Template HTML con Jinja2 e Bootstrap 5. L'interfaccia utente è interamente in **italiano**, progettata con font ad alta leggibilità, contrasti nitidi e pulsanti ampi pensati per pazienti anziani.
- **Convenzione linguistica**: Codice, classi, metodi, variabili e tabelle del database in **Inglese**; interfaccia grafica, messaggi flash e label in **Italiano**.

---

## 3. Design Pattern Implementati

1. **Layered Architecture (MVC)**:
   - **Presentation Layer** (`app/controllers/` e `app/templates/`): Gestione richieste HTTP, sessioni utente, decoratori di sicurezza e rendering delle pagine.
   - **Business Logic Layer** (`app/services/`): Contiene il 100% delle regole cliniche, controlli di soglia, calcolo coerenza e gestione allerte. Nessuna logica clinica risiede nelle rotte.
   - **Data Access Layer** (`app/daos/`): Query SQL raw incapsulate, isolamento del motore database.
   - **Model Layer** (`app/models/`): Data classes pure rappresentative delle entità di dominio.
2. **Singleton Pattern** (`app/database/DatabaseManager.py`):
   - Garantisce un unico punto di gestione della connessione a SQLite.
   - Implementa connessioni *thread-local* per prevenire problemi di concorrenza su file SQLite e abilita automaticamente l'integrità referenziale (`PRAGMA foreign_keys = ON;`).
3. **Data Access Object (DAO)**:
   - Un DAO per ciascuna tabella/aggregato (`UserDAO`, `PatientDAO`, `TherapyDAO`, `MeasurementDAO`, `MedicationIntakeDAO`, `AlertDAO`, `MedicalRecordDAO`, `ClinicalEventDAO`, `MessageDAO`, `AuditLogDAO`).
4. **Service Layer (Facade)**:
   - I controller dialogano esclusivamente con i Service (`AuthService`, `MeasurementService`, `TherapyService`, `MedicalRecordService`, `AlertService`, `MessageService`, `AuditService`, `PatientService`), che coordinano DAOs e logiche di notifica.
5. **Strictly Append-Only Pattern (NFR2)**:
   - `AuditLogDAO` include unicamente il metodo `insert_log` e metodi di lettura. Non esistono metodi `update` o `delete`, impedendo a livello di architettura qualsiasi manomissione del registro medico-legale.

---

## 4. Struttura Completa del Progetto

```text
CodiceProgetto/
├── README.md                      # Questa guida completa
├── requirements.txt               # Dipendenze minime (Flask, Werkzeug)
├── app.py                         # Application Factory ed entry-point di Flask
├── seed_db.py                     # Script di setup e popolamento iniziale del DB
├── tests/                         # Suite di Unit & Integration Test
│   └── test_system.py             # Test esaustivi sui Test Case (TC01 - TC20)
└── app/
    ├── __init__.py                # Inizializzazione applicazione e comandi CLI
    ├── database/
    │   ├── DatabaseManager.py     # Singleton per connessione e query SQLite
    │   ├── schema.sql             # Script DDL di creazione tabelle (ERD conforme)
    │   └── telemedicine.db        # File di database SQLite creato all'avvio
    ├── models/                    # Data Classes di Dominio
    │   ├── User.py                # Utente e ruoli (Paziente=0, Medico=1, Admin=2)
    │   ├── Patient.py             # Dati anagrafici e associazione con Medico curante
    │   ├── MedicalRecord.py       # Fattori di rischio e comorbilità croniche (FR7)
    │   ├── ClinicalEvent.py       # Sintomi, patologie e terapie concomitanti (FR3.2)
    │   ├── Therapy.py             # Prescrizioni del diabetologo (FR5)
    │   ├── Measurement.py         # Rilevazioni glicemiche (FR3.1)
    │   ├── MedicationIntake.py    # Diario assunzioni e flag di coerenza (FR4, FR6)
    │   ├── Alert.py               # Allarmi clinici (WARNING e CRITICAL) (FR10, FR13)
    │   ├── Message.py             # Comunicazioni interne paziente-medico (FR11)
    │   └── AuditLog.py            # Log immutabile delle operazioni del medico (FR12)
    ├── daos/                      # Data Access Objects (SQL Raw incapsulato)
    │   ├── UserDAO.py
    │   ├── PatientDAO.py
    │   ├── MedicalRecordDAO.py
    │   ├── ClinicalEventDAO.py
    │   ├── TherapyDAO.py
    │   ├── MeasurementDAO.py
    │   ├── MedicationIntakeDAO.py
    │   ├── AlertDAO.py
    │   ├── MessageDAO.py
    │   └── AuditLogDAO.py         # Append-only (nessun update/delete)
    ├── services/                  # Business Logic Layer (Regole di dominio)
    │   ├── AuthService.py         # Hashing password (scrypt/pbkdf2) e login
    │   ├── MeasurementService.py  # Soglie glicemiche, severità e avvisi d'urgenza
    │   ├── TherapyService.py      # Controllo coerenza dosi e check aderenza 3gg
    │   ├── MedicalRecordService.py# Aggiornamento fattori di rischio con audit
    │   ├── AlertService.py        # Presa in carico e risoluzione allarmi
    │   ├── MessageService.py      # Simulazione invio email paziente-medico
    │   ├── AuditService.py        # Scrittura audit trail medico-legale
    │   └── PatientService.py      # Registrazione e associazione pazienti
    ├── controllers/               # Presentation Layer (Flask Blueprints)
    │   ├── auth_decorators.py     # Decoratori per controllo accessi e ruoli
    │   ├── AuthController.py      # Rotte /login e /logout
    │   ├── PatientController.py   # Rotte paziente: rilevazioni, farmaci, sintomi
    │   ├── DoctorController.py    # Rotte medico: dashboard, dossier, terapie, trend
    │   └── AdminController.py     # Rotte admin: gestione utenze e audit log
    └── templates/                 # Viste Jinja2 (HTML accessibile in Italiano)
        ├── base.html              # Layout principale, navbar dinamica e messaggi Flash
        ├── auth/login.html        # Form di accesso
        ├── patient/               # Pagine dedicate al Paziente
        │   ├── dashboard.html
        │   ├── add_measurement.html
        │   ├── add_intake.html
        │   ├── clinical_events.html
        │   └── messages.html
        ├── doctor/                # Pagine dedicate al Medico
        │   ├── dashboard.html
        │   ├── patient_dossier.html
        │   ├── patient_trends.html
        │   ├── manage_therapy.html
        │   ├── messages.html
        │   └── audit_logs.html
        └── admin/                 # Pagine dedicate all'Amministratore
            ├── dashboard.html
            ├── create_doctor.html
            ├── create_patient.html
            └── audit_logs.html
```

---

## 5. Guida Rapida all'Installazione e Setup

### Prerequisiti
- Python 3.10 o superiore installato sul sistema.
- Modulo `pip`.

### Step 1: Posizionarsi nella cartella del progetto
```bash
cd Progetto/CodiceProgetto
```

### Step 2: Installare le dipendenze
```bash
pip install -r requirements.txt
```
*(Se utilizzi un ambiente virtuale: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`)*

### Step 3: Inizializzare e Popolare il Database
Esegui lo script di popolamento per creare lo schema SQLite e inserire gli account iniziali:
```bash
python3 seed_db.py
```
*(In alternativa è possibile utilizzare i comandi CLI di Flask: `flask init-db` e `flask seed-db`).*

### Step 4: Avviare il Server Web
```bash
python3 app.py
```
Il server si avvierà in modalità di sviluppo all'indirizzo:  
👉 **`http://127.0.0.1:5000`**

---

## 6. Credenziali Predefinite per il Test

Al primo avvio, `seed_db.py` crea 3 profili dimostrativi completi per testare ogni funzionalità:

| Ruolo | Email | Password | Nome Utente | Descrizione |
|---|---|---|---|---|
| 👑 **Amministratore** | `admin@telemedicina.it` | `admin123` | Resp. Amministratore | Setup iniziale del sistema, creazione medici e registrazione pazienti con assegnazione. |
| 🩺 **Medico Diabetologo** | `dott.mario.rossi@ospedale.it` | `dottore123` | Dr. Mario Rossi | Monitoraggio clinico, ricezione allarmi, prescrizione terapie, consultazione trend e audit. |
| 👤 **Paziente Diabetico** | `giuseppe.verdi@email.it` | `paziente123` | Giuseppe Verdi | Paziente assegnato al Dr. Rossi con terapia attiva (Metformina), diario glicemico e comunicazioni. |

---

## 7. Guida Operativa ai Flussi Utente (Come Usare il Sistema)

### 7.1 Flusso Amministratore (FR2, UC5)
1. Accedi da `/login` con le credenziali `admin@telemedicina.it` / `admin123`.
2. Verrai reindirizzato su `/admin/dashboard`.
3. **Creare un nuovo Medico**: Clicca su `+ Medico`, compila nome, email e password temporanea.
4. **Registrare un Paziente**: Clicca su `+ Paziente`. Inserisci i dati anagrafici e **seleziona obbligatoriamente il Medico curante** dal menu a tendina.
5. **Ispezione Audit Trail**: Dal menu superiore clicca su `Audit Log Globale` per visualizzare in sola lettura l'elenco inalterabile di tutte le operazioni cliniche eseguite nel sistema.

---

### 7.2 Flusso Paziente (FR3.1, FR3.2, FR4, FR6, FR9, FR11, UC1, UC3, UC6, UC9)
1. Accedi con `giuseppe.verdi@email.it` / `paziente123`.
2. **Dashboard Paziente**:
   - Se per la giornata odierna non hai ancora registrato l'assunzione dei farmaci prescritti, un **banner di promemoria (FR9)** ti avviserà visivamente.
   - Visualizzi le terapie attive prescritte dal tuo medico, le ultime glicemie e le assunzioni recenti.
3. **Registrare una Glicemia (UC1 / FR3.1)**:
   - Clicca sul pulsante grande `Nuova Rilevazione`.
   - Inserisci il valore in mg/dL, seleziona il contesto (*Prima del pasto* o *Dopo il pasto*) e data/ora.
   - *Se il valore è nei limiti (80-130 prima, <180 dopo)*: riceverai un messaggio verde di conferma.
   - *Se il valore è fuori soglia (es. 150 prima del pasto)*: il sistema lo salva e genera un avviso `WARNING` per il medico.
   - *Se il valore è critico (es. 40 mg/dL ipoglicemia o >250 mg/dL iperglicemia)*: il sistema mostra un allarme rosso prioritario e invia una notifica d'emergenza via email al medico.
4. **Registrare l'Assunzione di un Farmaco (UC3 / FR4 / FR6)**:
   - Clicca su `Registra Farmaco`.
   - Puoi cliccare su uno dei bottoni di **selezione rapida** per pre-compilare il farmaco e la dose dalla tua terapia attiva.
   - Se inserisci una dose diversa o un farmaco non prescritto: il sistema **non blocca l'inserimento** (nel caso il paziente abbia realmente sbagliato dose), ma mostra un **messaggio giallo di avviso** e notifica il medico curante dell'incongruenza.
5. **Segnalare Sintomi o Altri Farmaci (UC6 / FR3.2)**:
   - Clicca su `Segnala Evento`, scegli la tipologia (Sintomo, Patologia, Altro Farmaco), descrivi il problema e imposta le date di inizio/fine.
6. **Contattare il Medico Curante (UC9 / FR11)**:
   - Clicca su `Contatta Medico` per inviare una richiesta o domanda direttamente al Dr. Rossi. L'invio simula la spedizione di un'email clinica e popola la conversazione interna.

---

### 7.3 Flusso Medico Diabetologo (FR5, FR7, FR8, FR10, FR12, FR13, UC2, UC7, UC8)
1. Accedi con `dott.mario.rossi@ospedale.it` / `dottore123`.
2. **Dashboard Medico**:
   - **Check Dinamico Aderenza (FR13)**: Ad ogni caricamento della dashboard, il sistema verifica in tempo reale se qualche paziente con terapie attive non registra assunzioni da più di 3 giorni consecutivi. In caso positivo, genera un allarme di mancata aderenza.
   - **Box Allarmi Clinici Aperti**: Mostra gli avvisi urgenti (Glicemie critiche o fuori soglia, incoerenze nelle dosi, mancata aderenza). Il medico può cliccare su `Risolvi` per chiudere l'allarme (l'azione viene salvata nell'Audit Log).
   - **Elenco Pazienti Assegnati**: Tabella riassuntiva di tutti i pazienti in carico.
3. **Fascicolo Clinico Completo (UC7 / FR7)**:
   - Clicca su `Fascicolo Clinico` di un paziente.
   - **Fattori di Rischio e Comorbilità**: Il medico può aggiornare gli switch (Fumatore, Dipendenze da alcol, Ipertensione arteriosa, Obesità). Cliccando su `Salva e Traccia`, i dati vengono aggiornati e l'azione viene registrata nell'Audit Trail.
   - Consulta i sintomi e gli eventi segnalati dal paziente.
4. **Andamento Clinico e Reportistica (UC8 / FR8)**:
   - Clicca su `Andamento Glicemico`.
   - Puoi alternare la vista tra **Settimanale (7 giorni)** e **Mensile (30 giorni)**.
   - Il sistema calcola automaticamente: numero misurazioni, **media glicemica del periodo**, range minimo-massimo e **percentuale di misurazioni rientrate nel target clinico**.
5. **Prescrizione / Aggiornamento Terapia (UC2 / FR5 / FR12)**:
   - Clicca su `Gestione Terapia`.
   - Specifica nome del farmaco, frequenza giornaliera, quantità per assunzione, istruzioni e data inizio.
   - Conferma per salvare: la vecchia terapia per quel farmaco viene archiviata e la nuova resa attiva. **L'operazione genera un record inalterabile nell'Audit Log**.
   - Se il medico clicca su `Annulla`, l'operazione viene abortita senza salvare nulla e senza sporcare l'audit log (Flusso Alternativo 2.2).
6. **Mio Registro Audit (FR12 / NFR2)**:
   - Clicca su `Registro Operazioni` per visualizzare la traccia legale delle proprie modifiche a terapie, fascicoli e risoluzione allarmi.

---

## 8. Regole di Business e Logica Clinica Core

| Funzionalità | Regola / Condizione | Azione del Sistema |
|---|---|---|
| **Glicemia Pre-Pasto Normale** | 80 $\le$ Valore $\le$ 130 mg/dL | Salvataggio con conferma, nessun allarme. |
| **Glicemia Post-Pasto Normale** | Valore $\le$ 180 mg/dL (dopo 2h) | Salvataggio con conferma, nessun allarme. |
| **Fuori Soglia Lieve** | Pre-pasto > 130 o Post-pasto > 180 | Salvataggio, allarme visivo `WARNING` (badge giallo) nella dashboard del medico. |
| **Crisi Ipoglicemica Grave** | Valore < 60 mg/dL (es. 40 mg/dL) | Salvataggio, allarme prioritario `CRITICAL` (badge rosso) + **email automatica di emergenza al medico**. |
| **Crisi Iperglicemica Severa** | Valore $\ge$ 250 mg/dL | Salvataggio, allarme prioritario `CRITICAL` + email d'emergenza. |
| **Coerenza Terapia (FR6)** | Dose assunta $\ne$ Dose prescritta oppure farmaco non presente | Salvataggio non bloccato; warning a schermo per il paziente e alert `WARNING` al medico. |
| **Mancata Aderenza (FR13)** | Nessun farmaco assunto da > 3 giorni | Alert `WARNING` al medico generato dinamicamente al caricamento della dashboard. |
| **Promemoria Paziente (FR9)** | Nessuna assunzione registrata oggi | Banner di avviso nella home page del paziente. |

---

## 9. Integrità Medico-Legale: Audit Log Append-Only

In conformità con **NFR2** e **FR12**, la tabella `audit_logs` garantisce che ogni azione clinica del medico (prescrizione terapia, modifica comorbilità, consultazione fascicolo, risoluzione allarmi) sia tracciata con timestamp e non possa essere in alcun modo alterata:
1. **A livello architetturale**: `AuditLogDAO.py` espone **unicamente** il metodo `insert_log()` e metodi di lettura. Non esistono metodi di modifica o cancellazione (`update`, `delete`).
2. **A livello di sicurezza**: I log sono protetti e accessibili per sola consultazione solo agli utenti autenticati con privilegi (Medico per i propri log, Admin per l'audit complessivo).

---

## 10. Test Automatici e Matrice di Tracciabilità

I requisiti funzionali e non funzionali sono interamente coperti dalla suite automatizzata `tests/test_system.py`:

| ID Test | Requisito / Caso d'Uso | Descrizione Test | Esito |
|---|---|---|:---:|
| **TC01** | FR1, UC4, NFR4 | Login con credenziali corrette per Paziente, Medico e Admin con reindirizzamento corretto | ✅ Passato |
| **TC02** | FR1, UC4, NFR4 | Login con password errata e blocco accesso non autorizzato | ✅ Passato |
| **TC03** | FR2, UC5 | Creazione utente Medico e Paziente con associazione da parte dell'Admin | ✅ Passato |
| **TC04** | FR3.1, UC1 | Inserimento rilevazione glicemica normale (110 mg/dL prima del pasto) | ✅ Passato |
| **TC05** | FR3.1, FR10, UC1 | Inserimento valore fuori soglia (150 mg/dL) $\rightarrow$ generazione alert WARNING | ✅ Passato |
| **TC06** | FR3.1, FR10, UC1 | Inserimento ipoglicemia critica (40 mg/dL) $\rightarrow$ alert CRITICAL + invio email medico | ✅ Passato |
| **TC07** | FR3.1, UC1 (Alt 1.1) | Inserimento dati non validi (glicemia negativa) $\rightarrow$ rifiuto e messaggio d'errore | ✅ Passato |
| **TC08** | FR3.2, UC6 | Segnalazione di sintomo / patologia con date | ✅ Passato |
| **TC09** | FR4, FR6, UC3 | Assunzione farmaco perfettamente coerente con la terapia prescritta | ✅ Passato |
| **TC10** | FR4, FR6, UC3 (Alt 3.2)| Assunzione farmaco con dose incoerente $\rightarrow$ salvataggio consentito con warning | ✅ Passato |
| **TC12** | FR5, FR12, UC2 | Prescrizione terapia medica con tracciamento automatico nell'Audit Log | ✅ Passato |
| **TC13** | FR5, UC2 (Alt 2.1) | Prescrizione con campi obbligatori mancanti $\rightarrow$ rigetto e nessun audit creato | ✅ Passato |
| **TC15** | FR7, FR12, UC7 | Aggiornamento fattori di rischio e comorbilità con registrazione nell'Audit Log | ✅ Passato |
| **TC16** | FR8, UC8 | Report andamento clinico e aggregazioni statistiche settimanali/mensili | ✅ Passato |
| **TC19** | FR11, UC9 | Invio messaggi ed email simulate paziente $\leftrightarrow$ medico curante | ✅ Passato |
| **TC20** | FR12, NFR2 | Verifica conformità Append-Only (assenza assoluta di metodi update/delete nei log) | ✅ Passato |

### Comando per eseguire tutti i test:
```bash
python3 -m unittest discover -s tests
```
Tutti i **16 test di integrazione** vengono eseguiti in meno di 3 secondi garantendo la totale stabilità dell'applicazione.
