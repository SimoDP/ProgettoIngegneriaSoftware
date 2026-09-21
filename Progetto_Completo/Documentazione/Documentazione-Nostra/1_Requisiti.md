	
Ci sono 4 fasi del Requirement Engineering:
elicitation -> analisi dei requisiti -> definizione e specifica -> validazione

---
## 1. Elicitation

### 1.1 Identificazione degli Stakeholder (Attori)
Dall'analisi del dominio, sono stati identificati i seguenti attori principali che interagiranno o avranno interesse nel sistema:
*   **Paziente Diabetico (Tipo 2):** Utente finale che necessita di monitorare costantemente i propri valori e aderire alla terapia.
*   **Medico Diabetologo:** Specialista che ha in cura uno o più pazienti, definisce le terapie e monitora l'andamento clinico.
*   **Amministratore del Servizio (Responsabile):** Utente con privilegi amministrativi incaricato del setup iniziale e dell'inserimento delle anagrafiche per l'autenticazione.

### 1.2 Glossario del Dominio (Data Dictionary)
Per evitare ambiguità e per completezza scriviamo la definizione delle parole principali.
*   **Glicemia:** Concentrazione di glucosio nel sangue. I valori normali di riferimento per il sistema sono considerati tra 80 e 130 mg/dL (prima dei pasti) e inferiori a 180 mg/dL (due ore dopo i pasti).
*   **Terapia:** Insieme di prescrizioni mediche. Comprende il nome del farmaco, il numero di assunzioni giornaliere, la quantità per assunzione e le indicazioni temporali (es. dopo i pasti).
*   **Rilevazione:** Inserimento giornaliero da parte del paziente del proprio valore glicemico, contestualizzato al momento della giornata (es. prima/dopo pasto).
*   **Comorbilità:** Patologie preesistenti o concomitanti del paziente (es. ipertensione).
*   **Fattori di Rischio:** Abitudini o condizioni che aggravano lo stato di salute (es. fumatore, ex-fumatore, dipendenza da alcol/stupefacenti, obesità).
*   **Sintomo:** Manifestazione clinica avvertita dal paziente (es. spossatezza, nausea, mal di testa).

### 1.3 Bisogni degli Utenti (User Needs / User Stories)
*Estrazione dei bisogni in linguaggio naturale formattato dal punto di vista dell'utente.*

**Lato Paziente:**
*   *Come Paziente*, voglio potermi autenticare in modo sicuro per accedere ai miei dati sanitari.
*   *Come Paziente*, voglio poter inserire quotidianamente i miei valori di glicemia (prima e dopo i pasti).
*   *Come Paziente*, voglio poter registrare l'assunzione di farmaci (insuline o antidiabetici orali) specificando data, ora, farmaco e quantità, affinché il sistema possa verificare la coerenza con la terapia prescritta.
*   *Come Paziente*, voglio poter segnalare eventuali sintomi anomali, patologie e/o terapie concomitanti, associandoli al periodo di riferimento.
*   _Come Paziente_, voglio ricevere un "alert" se mi dimentico di inserire a sistema l'avvenuta assunzione dei miei farmaci.
*   *Come Paziente*, voglio poter inviare un'email al mio medico curante direttamente tramite il sistema per richieste o domande.

**Lato Medico:**
*   *Come Medico*, voglio autenticarmi per accedere alla lista di tutti i pazienti presenti a sistema, in modo da poter visualizzare e aggiornare i loro dati clinici.
*   *Come Medico*, voglio poter creare, modificare o visualizzare la terapia per ogni mio paziente, specificando farmaco, numero di assunzioni giornaliere, quantità per assunzione ed eventuali indicazioni (es. dopo/lontano dai pasti).
*   *Come Medico*, voglio aggiornare la "breve sezione" di informazioni cliniche del paziente (fattori di rischio, pregresse patologie e comorbilità).
*   *Come Medico*, voglio visualizzare i dati glicemici dei pazienti in modo sintetico (andamento settimanale o mensile) per valutare l'evoluzione della malattia.
*   *Come Medico*, voglio ricevere degli "alert" se uno dei miei pazienti registra glicemie oltre le soglie di pericolo, con diverse modalità di notifica in base alla gravità.
*   *Come Medico*, voglio che il sistema tracci (audit log) ogni mia operazione di modifica sui dati dei pazienti, per questioni medico-legali.
*  _Come Medico_, voglio ricevere un "alert" se un mio paziente non registra l'assunzione dei farmaci prescritti per più di 3 giorni consecutivi, in modo da poter intervenire tempestivamente e verificare la sua aderenza alla terapia.

**Lato Amministratore:**
*   *Come Amministratore*, voglio poter inserire nel sistema i dati iniziali di medici e pazienti per permettere loro l'autenticazione, e associare ogni paziente al proprio medico di riferimento.

---
## 2. Analisi dei Requisiti

### 2.1 Requisiti Funzionali (FR - Functional Requirements)
In questa sezione descriveremo le funzionalità e i servizi che saranno forniti dal sistema prendendo dagli user needs/wish fatti prima.

*   **FR1 - Autenticazione e Gestione Utenze:** Il sistema deve permettere l'accesso differenziato tramite credenziali (Paziente, Medico, Admin).
*   **FR2 - Configurazione Iniziale:** Il sistema deve permettere all'Amministratore di creare i profili di medici e pazienti e di associare un paziente a un medico specifico.
-    **FR3.1 - Inserimento Rilevazioni Glicemiche:** Il sistema deve permettere al paziente di registrare le proprie rilevazioni glicemiche, specificando per ognuna il valore, la data, l'ora e il momento rispetto al pasto (prima o dopo).
-    **FR3.2 - Segnalazione Sintomi, Patologie e Terapie Concomitanti:** Il sistema deve consentire al paziente di segnalare l'insorgenza di eventuali sintomi, patologie e/o l'assunzione di terapie concomitanti, indicandone la descrizione e il periodo di validità/occorrenza.
*   **FR4 - Diario Paziente (Assunzione Farmaci):** Il sistema deve permettere al paziente di registrare l'assunzione di farmaci, indicando nome del farmaco, data, ora e quantità.
*   **FR5 - Gestione Terapia:** Il sistema deve permettere al medico di definire e aggiornare la terapia (farmaco, frequenza, dosaggio, note/indicazioni temporali).
*   **FR6 - Verifica Coerenza Terapia (Controllo):** Il sistema deve verificare che le assunzioni di farmaci inserite dal paziente (FR4) siano coerenti con la terapia prescritta dal medico (FR5).
*   **FR7 - Fascicolo Paziente:** Il sistema deve permettere al medico di gestire una scheda paziente contenente fattori di rischio (fumatore, alcol, ecc.) e patologie pregresse/comorbilità.
*   **FR8 - Visualizzazione Dati e Reportistica:** Il sistema deve fornire al medico visualizzazioni di sintesi (es. tabelle o grafici) dell'andamento glicemico settimanale e mensile del paziente.
*   **FR9 - Sistema di Allertamento verso Paziente**: Il sistema deve generare un avviso verso il paziente nel caso si dimenticasse di inserire l'avvenuta assunzione di farmaci.
*   **FR10 - Sistema di Allertamento (Alert Medico):** Il sistema deve segnalare al medico (tramite diverse modalità/gravità) se un paziente registra valori glicemici che superano le soglie critiche.
*   **FR11 - Comunicazione Esterna:** Il sistema deve permettere al paziente di inviare comunicazioni via e-mail al proprio medico di riferimento.
*   **FR12 - Tracciabilità Operazioni Medico (Audit Trail):** Il sistema deve tenere traccia, in un apposito registro, di tutti gli aggiornamenti, le letture e le modifiche ai dati effettuate da un medico.
*   **FR13 - Sistema di Allertamento verso Medico:** Il sistema deve segnalare al medico (tramite diverse modalità/gravità) se un paziente non segua per più di 3 giorni le prescrizioni.

### 2.2 Requisiti Non Funzionali (NFR - Non-Functional Requirements)
*   **NFR1 - Vincoli di Implementazione (Architettura):** Il software deve essere sviluppato in un linguaggio Orientato agli Oggetti (es. Java o Python), implementando una Interfaccia Grafica (GUI) e facendo uso di un Database relazionale (sqlite).
*   **NFR2 - Tracciabilità e Integrità (Security Audit):** I log delle operazioni effettuate dal medico (FR12) non devono essere alterabili (append-only) per garantire la responsabilità delle scelte mediche.
*   **NFR3 - Usabilità (Design UI):** Le interfacce grafiche devono essere progettate per essere accessibili anche da utenti (i pazienti) potenzialmente anziani o non esperti di tecnologia, fornendo feedback chiari e messaggi di errore intuitivi.
* **NFR4 - Sicurezza e Accesso:** Trattando dati medici sensibili, il sistema deve garantire l'accesso ai dati clinici dei pazienti _solo_ agli utenti (Medici e Pazienti) regolarmente autenticati tramite credenziali valide.

### 2.3 Analisi delle Ambiguità, Assunzioni e "Missing Requirements"

*   **Ambiguità 1 - Coerenza Terapie/Assunzioni:** La traccia dice "Il sistema deve verificare che le assunzioni di farmaci da parte dei pazienti siano coerenti con le terapie". *Problema:* Cosa succede se non lo sono? Il sistema deve bloccare l'inserimento?
    *   *Risoluzione (Assunzione):* Il sistema NON blocca l'inserimento (il paziente potrebbe aver effettivamente sbagliato dose nella realtà), ma genera un "Warning" visivo a schermo per il paziente e un flag di avviso nel cruscotto del medico.
*   **Ambiguità 2 - Allarmi per Gravità:** La traccia dice "segnala ai medici ... con diverse modalità a seconda della gravità". *Problema:* Quali sono queste modalità e le soglie?
    *   *Risoluzione (Assunzione):* Si definiscono due livelli di gravità. 
        * *Gravità Media* (es. glicemia leggermente fuori soglia): Notifica visiva (badge) nella dashboard del medico.
        * *Gravità Alta* (es. ipoglicemia grave o iperglicemia severa): Notifica nella dashboard + Invio automatico di una e-mail di allarme al medico.
*   **Ambiguità 3 - Log Audit (Tracciabilità Medico):** La traccia dice "provvederà a tenere traccia di quale medico ha effettuato le varie operazioni".
    *   *Risoluzione (Assunzione):* Si assume che ogni operazione di modifica (Create, Update, Delete) sui dati sensibili del paziente generi un record non modificabile nel database contenente: ID Medico, Timestamp, Tipo di Operazione.

### 2.4 Prioritizzazione dei Requisiti (Metodo MoSCoW)

abbiamo preso come must tutte le richieste che erano presenti nella consegna, siccome erano tutte cose che venivano richieste.

*   **M - MUST (Requisiti Necessari - Da implementare assolutamente):**
    *   FR1: Autenticazione e Gestione Utenze (Paziente, Medico, Admin).
    *   FR2: Configurazione Iniziale.
    *   FR3.1: Inserimento rilevazioni glicemiche.
    *   FR4: Inserimento assunzione farmaci.
    *   FR5: Gestione terapia da parte del medico.
    *   FR8: Visualizzazione dati glicemici (sintesi/grafici) per il medico.
    *   FR9: Alert paziente non assunzione farmaci
    *   FR10: Alert al medico per valori oltre la soglia.
    *   NFR1: Database relazionale e linguaggio OO.
    *   NFR4: Sicurezza e accesso ai dati sensibili.
    *   FR13: Alert medico per paziente non segue prescizione da 3 giorni.
    *   FR3.2: Segnalazione Sintomi, Patologie e Terapie Concomitanti.
    *   FR6: Verifica di coerenza tra farmaco assunto e terapia prescritta.
    *   FR7: Gestione fascicolo paziente (Fattori di rischio, comorbilità).
    *   FR12: Log (Audit trail) delle operazioni dei medici.
    *   FR11: Comunicazione esterna (invio email per richieste o domande) tra paziente e medico (può essere simulata stampando l'output a console se il tempo è limitato).

*   **S - SHOULD (Requisiti Desiderabili - Importanti, ma il sistema base funziona anche senza)

*   **C - COULD (Requisiti Possibili - Da fare solo se ci sono tempo e risorse)**


## 3. Definizione e Specifica

per continuare con il RE (Requirements Engineering) svolgeremo la fase 3 nel seguente modo:
	1. Definiamo i vari Use Case principali e non, specificando quali requisiti funzionali soddisfano.
	2. Disegno lo Use Case Diagram globale, che modella visivamente tutte le interazioni possibili tra gli Attori e il sistema. Gli Use Case rappresentati derivano dal raggruppamento logico dei Requisiti Funzionali (FR) definiti nella Fase 2.
	3. Scriveremo i requisiti di sistema dei principali use case (UC1, UC2, UC3) tramite lo use case template (schede di specifica).
	4. Disegno il Class Diagram concettuale

#### Abbiamo scelto come Use Case Principali:
- **UC1: Registrazione Rilevazione Glicemica (Attore: Paziente)**
    - _Soddisfa i requisiti:_ **FR3.1** e **FR10**
        
    - _Perché è principale:_ Non è un semplice inserimento dati (FR3.1). Il sistema deve controllare se il valore sfora le soglie (80-130 pre-pasto, <180 post-pasto) e, in caso affermativo, scatenare la logica per avvisare il medico in base alla gravità (FR10).
        
- **UC2: Creazione/Gestione Terapia (Attore: Medico)**
    - _Soddisfa i requisiti:_ **FR5** e **FR12**
        
    - _Perché è principale:_ È il cuore delle operazioni cliniche lato medico (FR5). Implica specificare farmaco, quantità, frequenza e indicazioni, imponendo al sistema di scrivere un record inalterabile nell'audit log per la tracciabilità medico-legale (FR12).
        
- **UC3: Registrazione Assunzione Farmaco (Attore: Paziente)**
    - _Soddisfa i requisiti:_ **FR4**, **FR6** e **FR13**
        
    - _Perché è principale:_ È il caso d'uso più complesso in termini di validazione. Il sistema permette l'inserimento (FR4), ma deve verificare la coerenza tra ciò che il paziente assume e ciò che il medico ha prescritto (FR6), oltre a gestire indirettamente la logica degli alert in caso di mancata assunzione per 3 giorni consecutivi (FR13).

#### Gli altri Use Case sono:

- **UC4: Autenticazione al sistema (Attori: Paziente, Medico, Amministratore)**
    - _Soddisfa i requisiti:_ FR1 (e NFR4).
        
    - _Perché serve:_ L'autenticazione è esplicitamente richiesta dalla traccia per pazienti e medici. Ogni utente deve interagire con il sistema per accedere in maniera differenziata e sicura.
        
- **UC5: Configurazione Iniziale Utenze (Attore: Amministratore)**
    - _Soddisfa i requisiti:_ FR2.
        
    - _Perché serve:_ I responsabili del servizio devono inserire i dati iniziali dei medici e dei pazienti necessari per l'autenticazione. Serve inoltre per associare ogni paziente a uno specifico medico di riferimento.
        
- **UC6: Segnalazione Eventi Clinici Concomitanti (Attore: Paziente)**
    - _Soddisfa i requisiti:_ FR3.2.
        
    - _Perché serve:_ Questo caso d'uso permette al paziente di segnalare sintomi (come spossatezza, nausea), patologie e terapie concomitanti, indicandone i relativi periodi associati.
        
- **UC7: Aggiornamento Fascicolo del Paziente (Attore: Medico)**
    - _Soddisfa i requisiti:_ FR7 (e FR12 per la tracciabilità).
        
    - _Perché serve:_ Consente al medico di aggiornare una specifica e breve sezione contenente i fattori di rischio (come fumo, obesità, dipendenza da alcol) e le comorbidità presenti, ad esempio l'ipertensione.
        
- **UC8: Visualizzazione Andamento Clinico e Report (Attore: Medico)**
    - _Soddisfa i requisiti:_ FR8.
        
    - _Perché serve:_ Riguarda la funzionalità di visualizzazione dei dati in forma sintetica. Permette al medico di osservare l'andamento glicemico dei pazienti, mese per mese o settimana per settimana, valutandone l'evoluzione.
        
- **UC9: Invio Comunicazioni E-mail (Attore: Paziente)**
    - _Soddisfa i requisiti:_ FR11.
        
    - _Perché serve:_ Il paziente deve poter inviare un'email per domande e richieste varie al medico a cui è stato assegnato.
#### Disegno del Use Case Diagram
[[UseCaseDiagram.jpg]]



#### Schede di Specifica dei UC principali

##### Caso d'uso 1: RegistraRilevazioneGlicemica

**Id:** 1
**Breve descrizione:** Il paziente inserisce una nuova rilevazione giornaliera della glicemia. Il sistema ne salva i dati e verifica che i valori rientrino nei parametri di normalità, altrimenti innesca una procedura di allarme.
**Attori primari:** Paziente
**Attori secondari:** Nessuno
**Precondizioni:** Il Paziente è autenticato nel sistema.

**Sequenza degli eventi principale (Main Flow):**
1. Il paziente seleziona la funzionalità "aggiungi rilevazione".
2. Il sistema chiede al paziente di inserire il valore glicemico, la data, l'ora e il contesto rispetto al pasto (prima o dopo).
3. Il paziente inserisce i dati richiesti e conferma.
4. Il sistema valida i dati inseriti.
5. Il sistema salva la rilevazione nel database associandola al fascicolo del paziente.
6. Il sistema controlla se il valore glicemico rispetta le soglie (tra 80 e 130 mg/dL prima dei pasti, oppure inferiore a 180 mg/dL dopo i pasti).
   **Extension point: valoriFuoriSoglia** 
7. Il sistema mostra a schermo un messaggio di conferma di avvenuta registrazione.

**Postcondizioni:** La nuova rilevazione glicemica è registrata nel sistema ed è visibile al medico curante.

---

###### Sequenza degli eventi alternativa: DatiNonValidi
**Id:** 1.1
**Breve descrizione:** Il paziente inserisce dati formattati male o lascia campi vuoti (es. valore glicemico negativo o data mancante).
**Precondizioni:** Il paziente ha inserito dati non validi al passo 3.
**Sequenza degli eventi principale:**
1. La sequenza degli eventi alternativa inizia dopo il passo 4 della sequenza degli eventi principale.
2. Il sistema informa il paziente che i dati inseriti non sono validi o sono incompleti.
3. Il sistema chiede al paziente di ri-inserire i dati (il flusso ritorna al passo 3 della sequenza principale).
**Postcondizioni:** Nessuna rilevazione viene salvata.

###### Punti di estensione (relativo all' `<<extend>>` nel diagramma)
**Id:** 1.2
**Nome use case di estensione:** InviaNotificaAllarmeGlicemia
**Breve descrizione:** Il sistema rileva un valore anomalo ed estende il comportamento base generando un alert per il medico.
**Precondizioni:** Il valore glicemico analizzato al passo 6 non rispetta le soglie di normalità.
**Sequenza degli eventi principale:**
1. La sequenza inizia all'**Extension point: valoriFuoriSoglia** (dopo il passo 6 della sequenza principale).
2. Il sistema esegue i passi descritti nel caso d'uso `InviaNotificaAllarmeGlicemia` (valuta la gravità, invia notifica in dashboard e/o email al Medico).
3. Il flusso ritorna al passo 7 della sequenza principale (mostrando comunque la conferma di salvataggio al paziente).



##### Caso d'uso 2: GestioneTerapia

**Id:** 2
**Breve descrizione:** Il medico definisce, visualizza o aggiorna la terapia per un proprio paziente (farmaco, frequenza, dosaggio, indicazioni). Il sistema salva i dati e tiene traccia inalterabile dell'operazione.
**Attori primari:** Medico
**Attori secondari:** Nessuno
**Precondizioni:** Il medico è autenticato nel sistema e ha selezionato il fascicolo di un paziente a lui associato.

**Sequenza degli eventi principale (Main Flow):**
1. Il medico seleziona la funzionalità "gestione terapia".
2. Il sistema mostra l'attuale terapia (se presente) e chiede al medico di inserire o modificare i dettagli della prescrizione (nome farmaco, numero di assunzioni giornaliere, quantità e indicazioni temporali).
3. Il medico inserisce o modifica i dati della terapia e conferma.
4. Il sistema valida i dati inseriti.
5. Il sistema aggiorna la terapia nel database associandola al paziente.
6. `include(RegistraAuditLog)`
7. Il sistema mostra al medico un messaggio di conferma di avvenuto salvataggio.

**Postcondizioni:** La terapia del paziente è stata aggiornata con successo e l'operazione di modifica è stata tracciata permanentemente a fini medico-legali.

---
###### Sequenza degli eventi alternativa: DatiObbligatoriMancanti
**Id:** 2.1
**Breve descrizione:** Il medico dimentica di inserire uno o più campi obbligatori della terapia (es. omette il dosaggio).
**Attori primari:** Medico
**Attori secondari:** Nessuno
**Precondizioni:** Il medico ha tralasciato campi obbligatori al passo 3.
**Sequenza degli eventi principale:**
1. La sequenza degli eventi alternativa inizia dopo il passo 4 della sequenza degli eventi principale.
2. Il sistema informa il medico che i dati inseriti sono incompleti e segnala i campi mancanti.
3. Il sistema chiede al medico di ri-inserire/completare i dati (il flusso ritorna al passo 3 della sequenza principale).
**Postcondizioni:** Nessuna modifica alla terapia viene salvata e nessun log viene generato.

###### Sequenza degli eventi alternativa: Annulla
*(Esempio di "Attivazione in qualunque momento" mostrato alla **Slide 28**)*
**Id:** 2.2
**Breve descrizione:** Il medico annulla il processo di modifica della terapia.
**Attori primari:** Medico
**Attori secondari:** Nessuno
**Precondizioni:** Nessuna.
**Sequenza degli eventi principale:**
1. La sequenza degli eventi alternativa inizia in qualunque momento in cui l'utente deve compiere l'azione (ad esempio al passo 3 del Main Flow).
2. Il medico annulla l'operazione di gestione terapia.
3. Il sistema mostra la pagina principale del fascicolo del paziente, lasciando la terapia invariata.
**Postcondizioni:** Nessuna modifica alla terapia viene salvata e nessun log viene generato.

---

##### Caso d'uso 3: RegistraAssunzioneFarmaco

**Id:** 3
**Breve descrizione:** Il paziente registra nel proprio diario giornaliero l'assunzione di un farmaco. Il sistema salva l'informazione e verifica la coerenza tra quanto assunto e la terapia prescritta dal medico curante, segnalando eventuali discordanze.
**Attori primari:** Paziente
**Attori secondari:** Nessuno
**Precondizioni:** Il Paziente è autenticato nel sistema.

**Sequenza degli eventi principale (Main Flow):**
1. Il paziente seleziona la funzionalità "registra assunzione farmaco".
2. Il sistema chiede al paziente di inserire i dettagli dell'assunzione (nome del farmaco, data, ora e quantità assunta).
3. Il paziente inserisce i dati richiesti e conferma.
4. Il sistema valida i dati immessi (es. campi non vuoti, formattazione di data e ora).
5. Il sistema salva il record di assunzione associandolo al profilo del paziente.
6. Il sistema confronta i dati dell'assunzione (nome farmaco e quantità) con la terapia attualmente prescritta dal medico.
   **Extension point: incongruenzaTerapia**
7. Il sistema mostra a schermo un messaggio di conferma di avvenuta registrazione.

**Postcondizioni:** L'assunzione del farmaco è registrata a sistema. *(Nota di dominio: l'avvenuto inserimento azzera il conteggio dei 3 giorni per il controllo della mancata aderenza alla terapia).*

---

###### Sequenza degli eventi alternativa: DatiMancantiONonValidi
**Id:** 3.1
**Breve descrizione:** Il paziente omette dati obbligatori (es. la quantità di farmaco) o inserisce valori non coerenti (es. quantità negativa).
**Precondizioni:** Il paziente ha inserito dati non validi al passo 3.
**Sequenza degli eventi principale:**
1. La sequenza degli eventi alternativa inizia dopo il passo 4 della sequenza degli eventi principale.
2. Il sistema informa il paziente che i dati inseriti non sono validi.
3. Il sistema chiede al paziente di correggere i dati (il flusso ritorna al passo 3 della sequenza principale).
**Postcondizioni:** Nessuna assunzione viene salvata a sistema.

###### Punti di estensione (relativo all' `<<extend>>` nel diagramma)
*(Seguendo la **Slide 38**, specifichiamo come il sistema gestisce il controllo del requisito FR6)*
**Id:** 3.2
**Nome use case di estensione:** MostraAvvisoIncoerenza
**Breve descrizione:** Il sistema rileva che il farmaco assunto o la relativa dose non corrispondono a nessuna terapia attiva prescritta dal medico, ed estende il comportamento base generando un avviso.
**Precondizioni:** Il confronto effettuato al passo 6 rivela una mancata corrispondenza tra assunzione e terapia prescritta.
**Sequenza degli eventi principale:**
1. La sequenza inizia all'**Extension point: incongruenzaTerapia** (dopo il passo 6 della sequenza principale).
2. Il sistema esegue i passi descritti nel caso d'uso `MostraAvvisoIncoerenza` (registra la discordanza, genera un "Warning" visivo a schermo per il paziente e un flag di avviso nel cruscotto del medico).
3. Il flusso ritorna al passo 7 della sequenza principale (permettendo comunque la conclusione del salvataggio).






#### Class Diagram della Modellazione Concettuale
[[ClassDiagram_Concettuale.jpg]]



--- 

## 4. Validazione


#### 4.1 Casi di Test derivati dai Requisiti
Come previsto dalla teoria del Requirements Engineering (fase di Validazione), uno dei modi per valutare la qualità del documento dei requisiti è scrivere dei casi di test a partire dai requisiti stessi: se per ogni requisito riusciamo a scrivere un test che ne verifichi il comportamento, allora il requisito è inequivocabile e verificabile. Deriviamo quindi i casi di test dai requisiti funzionali (FR), dai requisiti non funzionali (NFR) e dai flussi (principali, alternativi ed extension) delle schede di specifica dei use case. Questi casi di test a livello di requisiti (black-box, il "cosa" deve succedere, non il "come") costituiscono la base che verrà poi raffinata nel file x_testing con unit test e system test dettagliati.

| ID | Riferimento (FR / UC) | Azioni / Input | Risultato Atteso |
|---|---|---|---|
| TC01 | FR1, UC4 (NFR4) | Login con credenziali valide come Paziente, come Medico e come Amministratore | Accesso consentito con interfaccia differenziata in base al ruolo; dati clinici accessibili solo dopo autenticazione |
| TC02 | FR1, UC4 (NFR4) | Login con password errata; tentativo di accesso ai dati clinici senza autenticazione | Accesso negato con messaggio di errore intuitivo; nessun dato clinico visualizzato |
| TC03 | FR2, UC5 | L'Admin crea un profilo Medico e un profilo Paziente e associa il paziente al medico | Utenze abilitate all'autenticazione; il paziente risulta "in cura" ed è visibile nella lista del medico |
| TC04 | FR3.1, UC1 | Il paziente inserisce una rilevazione: 110 mg/dL, data, ora, contesto "prima del pasto" | Dati validi: rilevazione salvata, messaggio di conferma, valore visibile al medico curante |
| TC05 | FR3.1, FR10, UC1 + extend InviaNotificaAllarmeGlicemia | Il paziente inserisce una rilevazione pre-pasto di 150 mg/dL (leggermente fuori soglia) | Rilevazione salvata; gravità media: notifica visiva (badge) nella dashboard del medico, nessuna email |
| TC06 | FR3.1, FR10, UC1 + extend InviaNotificaAllarmeGlicemia | Il paziente inserisce una rilevazione di 40 mg/dL (ipoglicemia grave) | Rilevazione salvata; gravità alta: badge nella dashboard + invio automatico di e-mail di allarme al medico |
| TC07 | FR3.1, UC1 (flusso alt. DatiNonValidi) | Il paziente inserisce un valore negativo o omette la data | Messaggio di dati non validi, richiesta di re-inserimento, nessuna rilevazione salvata |
| TC08 | FR3.2, UC6 | Il paziente segnala un sintomo (es. nausea) / patologia / terapia concomitante con periodo associato | Segnalazione salvata con dataInizio/dataFine e visibile nel fascicolo del paziente |
| TC09 | FR4, FR6, FR13, UC3 | Il paziente registra un'assunzione con farmaco e quantità identici alla terapia prescritta | Assunzione salvata senza avvisi; il conteggio dei 3 giorni consecutivi (aderenza) viene azzerato |
| TC10 | FR4, FR6, UC3 + extend MostraAvvisoIncoerenza | Il paziente registra un farmaco/dose non presente nella terapia prescritta | Il sistema NON blocca il salvataggio; "Warning" visivo a schermo per il paziente e flag di avviso nel cruscotto del medico |
| TC11 | FR4, UC3 (flusso alt. DatiMancantiONonValidi) | Il paziente registra un'assunzione omettendo la quantità | Messaggio di errore, richiesta di correzione, nessuna assunzione salvata |
| TC12 | FR5, FR12, UC2 (include RegistraAuditLog) | Il medico definisce la terapia: farmaco, 2 assunzioni/giorno, quantità 1, indicazione "dopo i pasti" | Terapia salvata con conferma; generato record inalterabile nell'audit log (ID medico, timestamp, tipo operazione) |
| TC13 | FR5, UC2 (flusso alt. DatiObbligatoriMancanti) | Il medico conferma la terapia omettendo il dosaggio | Campi mancanti segnalati, richiesta di completamento; nessuna modifica salvata e nessun log generato |
| TC14 | UC2 (flusso alt. Annulla) | Il medico annulla l'operazione di modifica della terapia | Ritorno al fascicolo del paziente; terapia invariata; nessun log generato |
| TC15 | FR7, FR12, UC7 | Il medico aggiorna fattori di rischio (es. fumatore) e comorbilità (es. ipertensione) | Fascicolo aggiornato; l'operazione di modifica è tracciata nell'audit log |
| TC16 | FR8, UC8 | Il medico richiede la sintesi dell'andamento glicemico settimanale e mensile di un paziente | Visualizzazione di tabelle/grafici con le rilevazioni aggregate correttamente per periodo |
| TC17 | FR9 | Il paziente non registra l'assunzione programmata di un farmaco | Il sistema genera un avviso/sollecito verso il paziente affinché completi gli inserimenti |
| TC18 | FR13 | Il paziente non registra assunzioni per più di 3 giorni consecutivi | Il medico riceve un alert di mancata aderenza alla terapia nella propria dashboard |
| TC19 | FR11, UC9 | Il paziente compone e invia un'email al proprio medico di riferimento | Comunicazione inviata (o simulata a console) e ricevuta dal medico associato |
| TC20 | FR12, NFR2 | Tentativo di modifica o cancellazione di un record dell'audit log | Operazione negata/impossibile: il log è append-only e garantisce l'integrità medico-legale |
| TC21 | NFR3 | Sessione di usabilità con utente "anziano/non esperto": compiti di inserimento rilevazione e assunzione | L'utente completa i compiti; feedback chiari e messaggi di errore intuitivi |
| TC22 | NFR1 | Ispezione dell'artefatto software | Linguaggio OO (Java o Python), interfaccia grafica (GUI) presente, database relazionale sqlite |

Corrispondenza Requisiti ↔ Casi di Test (da riportare nella colonna "Tests" della matrice di tracciabilità):
- FR1 → TC01, TC02
- FR2 → TC03
- FR3.1 → TC04, TC05, TC06, TC07
- FR3.2 → TC08
- FR4 → TC09, TC10, TC11
- FR5 → TC12, TC13, TC14
- FR6 → TC09, TC10
- FR7 → TC15
- FR8 → TC16
- FR9 → TC17
- FR10 → TC05, TC06
- FR11 → TC19
- FR12 → TC12, TC15, TC20
- FR13 → TC09, TC18
- NFR1 → TC22 | NFR2 → TC20 | NFR3 → TC21 | NFR4 → TC01, TC02




## 5. Requirements Management

#### 5.1 Matrice di Tracciabilità e Requirements Management

Come visto nella teoria, la gestione dei requisiti non si ferma alla loro stesura, ma continua per tutta la vita del progetto per gestire i cambiamenti (Impact Analysis) e tracciare lo stato di avanzamento.
Lo strumento fondamentale per questa fase è la Matrice di Tracciabilità.
Sebbene la stiamo compilando ora in fase di Validazione per verificare che ogni Requisito Funzionale (FR) sia coperto da almeno un Use Case e da un Caso di Test (verifica di completezza), questa matrice sarà il nostro riferimento vivo durante le fasi di Design, Coding e Testing.
Ogni volta che modificheremo un requisito, consulteremo questa matrice per capire quali classi, sequence diagram o test case dovranno essere aggiornati di conseguenza.

[[MatriceDiTracciabilita.jpg]]