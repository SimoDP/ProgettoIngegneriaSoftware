#!/usr/bin/env python3
"""
Script per la generazione della Documentazione di Progetto (PDF)
Progetto: TeleDiabete - Sistema di Telemedicina per la Gestione del Diabete di Tipo 2
Corso: Ingegneria del Software - Università degli Studi di Verona
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether, HRFlowable, Preformatted
)
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from PIL import Image as PILImage

class NumberedCanvas(canvas.Canvas):
    """
    Canvas a due passate per calcolare dinamicamente il numero totale di pagine
    e stampare intestazione e piè di pagina con numerazione 'Pagina X di Y'.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        # Non disegniamo header e footer sulla copertina (pagina 1)
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))

        # Intestazione superiore (Header)
        self.drawString(40, 810, "TeleDiabete — Ingegneria del Software (UniVR) — Progetto 2")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(40, 804, 555, 804)

        # Piè di pagina (Footer)
        self.line(40, 45, 555, 45)
        self.drawString(40, 32, "Documentazione di Analisi, Progettazione, Implementazione e Collaudo")
        page_str = f"Pagina {self._pageNumber} di {page_count}"
        self.drawRightString(555, 32, page_str)
        self.restoreState()


def get_scaled_image(img_path, max_width=510, max_height=420):
    """Ridimensiona proporzionalmente un'immagine per adattarsi alla pagina A4."""
    if not os.path.exists(img_path):
        return None
    try:
        with PILImage.open(img_path) as im:
            w, h = im.size

        ratio = min(max_width / w, max_height / h)
        if ratio < 1.0:
            final_w = w * ratio
            final_h = h * ratio
        else:
            final_w = w
            final_h = h
        return Image(img_path, width=final_w, height=final_h)
    except Exception as e:
        print(f"Errore caricamento immagine {img_path}: {e}")
        return None


def create_documentation_pdf(output_pdf_path, allegati_dir):
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=48,
        bottomMargin=48
    )

    styles = getSampleStyleSheet()

    # Palette colori accademico-professionale
    c_primary = colors.HexColor("#1A365D")     # Deep Navy
    c_secondary = colors.HexColor("#2B6CB0")   # Classic Blue
    c_accent = colors.HexColor("#2C7A7B")      # Teal Dark
    c_text = colors.HexColor("#2D3748")        # Dark Slate
    c_light = colors.HexColor("#F7FAFC")       # Off-white
    c_border = colors.HexColor("#E2E8F0")      # Light Border

    # Stili di testo personalizzati
    style_cover_title = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=c_primary,
        alignment=TA_CENTER
    )

    style_cover_sub = ParagraphStyle(
        'CoverSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=c_secondary,
        alignment=TA_CENTER
    )

    style_cover_meta = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=c_text,
        alignment=TA_CENTER
    )

    style_h1 = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=22,
        textColor=c_primary,
        spaceBefore=16,
        spaceAfter=10,
        keepWithNext=True
    )

    style_h2 = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=17,
        textColor=c_secondary,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    style_h3 = ParagraphStyle(
        'Header3',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=c_accent,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=c_text,
        alignment=TA_JUSTIFY,
        spaceAfter=6
    )

    style_body_bold = ParagraphStyle(
        'BodyBold',
        parent=style_body,
        fontName='Helvetica-Bold'
    )

    style_bullet = ParagraphStyle(
        'Bullet',
        parent=style_body,
        leftIndent=14,
        bulletIndent=4,
        spaceAfter=4
    )

    style_caption = ParagraphStyle(
        'Caption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#718096"),
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=8
    )

    style_code = ParagraphStyle(
        'CodeText',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1A202C")
    )

    style_table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=c_text
    )

    style_table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=c_primary
    )

    style_table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.white,
        alignment=TA_CENTER
    )

    story = []

    # =========================================================================
    # COPERTINA (Cover Page)
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("UNIVERSITÀ DEGLI STUDI DI VERONA", ParagraphStyle('UniHeader', parent=style_cover_sub, fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=c_primary)))
    story.append(Paragraph("Dipartimento di Informatica — Corso di Ingegneria del Software", style_cover_sub))
    story.append(Paragraph("Anno Accademico 2025 / 2026", style_cover_meta))
    story.append(Spacer(1, 30))

    story.append(HRFlowable(width="80%", thickness=2, color=c_primary, spaceBefore=5, spaceAfter=25))

    story.append(Paragraph("TeleDiabete", style_cover_title))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Sistema di Telemedicina di un Servizio Clinico per la Gestione e il Monitoraggio di Pazienti Diabetici (Diabete di Tipo 2)", ParagraphStyle('CoverSubBig', parent=style_cover_sub, fontSize=14, leading=20, textColor=c_secondary)))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Documentazione Ufficiale di Analisi, Progettazione Architetturale, Dettaglio Implementativo e Piano di Validazione / Testing", ParagraphStyle('CoverSub2', parent=style_cover_meta, fontSize=10.5, leading=15, textColor=colors.HexColor("#4A5568"))))

    story.append(HRFlowable(width="80%", thickness=1, color=c_secondary, spaceBefore=25, spaceAfter=30))

    story.append(Spacer(1, 50))

    # Box Autore e Specifiche
    info_data = [
        [Paragraph("<b>Autore / Candidato:</b>", style_table_cell), Paragraph("Simone Dal Prete, Pawanjot Singh, Davide Garbelli", style_table_cell_bold)],
        [Paragraph("<b>Traccia Assegnata:</b>", style_table_cell), Paragraph("Esercizio / Progetto 2 — Servizio Clinico per Diabete di Tipo 2", style_table_cell)],
        [Paragraph("<b>Curriculum / Indirizzo:</b>", style_table_cell), Paragraph("Sviluppo di Sistemi Software Orientato ai Dati (Bioinformatica)", style_table_cell)],
        [Paragraph("<b>Stack Implementativo:</b>", style_table_cell), Paragraph("Python 3.11, Flask 3.0, SQLite3 (Raw SQL / No ORM), Bootstrap 5", style_table_cell)],
        [Paragraph("<b>Requisiti Specifici:</b>", style_table_cell), Paragraph("Database Relazionale, Schemi ER, Audit Trail, Test di Consistenza Dati", style_table_cell)],
        [Paragraph("<b>Data Rilascio:</b>", style_table_cell), Paragraph("Settembre 2026", style_table_cell)]
    ]
    t_info = Table(info_data, colWidths=[150, 320])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t_info)

    story.append(PageBreak())

    # =========================================================================
    # SOMMARIO / INDICE GENERALE
    # =========================================================================
    story.append(Paragraph("Sommario dei Contenuti", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=4, spaceAfter=14))

    sommario_items = [
        ("1. Contesto del Sistema e Stack Tecnologico", "1.1 Descrizione del Progetto e Dominio Clinico | 1.2 Obiettivi del Sistema e Attori | 1.3 Stack Tecnologico Adottato"),
        ("2. Analisi dei Requisiti", "2.1 Elicitation e User Needs | 2.2 Requisiti Funzionali (FR1-FR13) | 2.3 Requisiti Non Funzionali (NFR1-NFR4) | 2.4 Ambiguità e Assunzioni | 2.5 Prioritizzazione MoSCoW"),
        ("3. Modellazione dei Requisiti e Use Case", "3.1 Schede Dettagliate degli Attori | 3.2 Use Case Diagram Globale | 3.3 Schede di Specifica UC Principali (UC1, UC2, UC3) | 3.4 Schede Altri Use Case (UC4-UC9) | 3.5 Class Diagram Concettuale | 3.6 Matrice di Tracciabilità Requisiti-Test"),
        ("4. Architettura del Sistema", "4.1 Stili Architetturali Adottati (Client-Server Thin-Client a 3 Livelli) | 4.2 Architettura Software Layered (Presentation, Service, Data, Model) | 4.3 Ciclo di Vita delle Richieste HTTP e Gestione Sessioni"),
        ("5. Database e Modello Dati", "5.1 Schema Entità-Relazione (ERD) | 5.2 Descrizione Dettagliata Entità e Relazioni | 5.3 Codice SQL/DDL per SQLite | 5.4 Test e Meccanismi di Consistenza dei Dati (Vincolo Bioinformatica)"),
        ("6. Progettazione del Software e Design Pattern", "6.1 Class Diagram del Software Progettato | 6.2 Struttura e Responsabilità delle Classi | 6.3 Discussione Approfondita dei Design Pattern (DAO, Singleton, Service Facade, Observer, Append-Only)"),
        ("7. Scenari di Interazione (Sequence & Activity Diagrams)", "7.1 Sequence Diagram UC1: Registrazione Rilevazione Glicemica | 7.2 Sequence Diagram UC2: Gestione Terapia con Audit Log | 7.3 Sequence Diagram UC3: Assunzione Farmaco e Controllo Coerenza | 7.4 Sequence Diagram UC4: Autenticazione | 7.5 Activity Diagram: Navigazione e Operatività Medico"),
        ("8. Package del Software e Struttura Modulare", "8.1 Organizzazione dell'Albero del Codice | 8.2 Modulo models | 8.3 Modulo daos | 8.4 Modulo services | 8.5 Modulo controllers | 8.6 Modulo templates e Accessibilità Anziani"),
        ("9. Piano di Testing e Validazione", "9.1 Obiettivo e Metodologia di Collaudo | 9.2 Ambiente di Esecuzione e Comandi di Test | 9.3 Output del Terminale di Esecuzione della Suite | 9.4 Tabella Completa dei 16 Test di Sistema Eseguiti")
    ]

    t_sommario_data = []
    for cap, desc in sommario_items:
        p_cap = Paragraph(f"<b>{cap}</b>", style_table_cell_bold)
        p_desc = Paragraph(desc, style_table_cell)
        t_sommario_data.append([p_cap, p_desc])

    t_sommario = Table(t_sommario_data, colWidths=[180, 330])
    t_sommario.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), c_light),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sommario)

    story.append(PageBreak())

    # =========================================================================
    # CAPITOLO 1: CONTESTO DEL SISTEMA E STACK TECNOLOGICO
    # =========================================================================
    story.append(Paragraph("1. Contesto del Sistema e Stack Tecnologico", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("1.1 Descrizione del Progetto e Dominio Clinico", style_h2))
    story.append(Paragraph(
        "Il presente progetto si colloca nell'ambito dei sistemi software medicali e della telemedicina applicata alla cura di patologie croniche ad altissima prevalenza epidemiologica. "
        "In particolare, l'obiettivo primario è la progettazione e l'implementazione del sistema informatico <b>TeleDiabete</b>, dedicato alla gestione assistita e al monitoraggio clinico continuo di pazienti affetti da <b>Diabete Mellito di Tipo 2</b>.",
        style_body
    ))
    story.append(Paragraph(
        "Il diabete mellito è una patologia metabolica cronica contraddistinta da livelli elevati di glucosio nel sangue (iperglicemia), determinati da un deficit parziale nella produzione di insulina da parte delle cellule beta-pancreatiche associato a un fenomeno di insulino-resistenza periferica. "
        "Nei paesi industrializzati e occidentali, l'invecchiamento demografico progressivo e l'adozione diffusa di abitudini alimentari scorrette e sedentarietà hanno provocato un incremento esponenziale della malattia, che coinvolge oltre 3,5 milioni di individui nella sola Italia e centinaia di milioni di persone a livello globale. "
        "Il Diabete di Tipo 2 rappresenta oltre il 90% della totalità delle diagnosi diabetiche.",
        style_body
    ))
    story.append(Paragraph(
        "Il trattamento efficace della patologia si fonda su tre cardini irrinunciabili: "
        "<b>(1)</b> l'automonitoraggio costante e puntuale dei valori glicemici prima e dopo i pasti principali (con intervalli ottimali tipicamente compresi tra 80 e 130 mg/dL a digiuno e inferiori a 180 mg/dL a due ore dal pasto); "
        "<b>(2)</b> la rigorosa e continuativa aderenza alla terapia farmacologica prescritta (ipoglicemizzanti orali, quali metformina o sulfoniluree, e/o somministrazioni sottocutanee di insulina esogena); "
        "<b>(3)</b> la supervisione clinica costante da parte dello specialista diabetologo, che deve poter intervenire prontamente rimodulando i dosaggi o gestendo tempestivamente emergenze ipoglicemiche o crisi iperglicemiche.",
        style_body
    ))

    story.append(Paragraph("1.2 Obiettivi del Sistema e Attori Coinvolti", style_h2))
    story.append(Paragraph(
        "Il sistema <i>TeleDiabete</i> risponde alla necessità di abbattere la distanza tra struttura sanitaria specialistica e domicilio del paziente, offrendo un canale informatico sicuro, strutturato e conforme ai requisiti normativi di tracciabilità. "
        "Gli attori che interagiscono con la piattaforma sono:",
        style_body
    ))
    story.append(Paragraph("• <b>Paziente Diabetico:</b> accede alla propria area personale per registrare le misurazioni glicemiche, annotare l'assunzione dei farmaci prescritti, segnalare sintomi anomali o patologie concomitanti, e comunicare via messaggio col medico.", style_bullet))
    story.append(Paragraph("• <b>Medico Diabetologo:</b> accede al cruscotto clinico per visualizzare l'elenco dei pazienti assegnati, consultare i fascicoli sanitari, prescrivere e rimodulare le terapie, analizzare graficamente i trend glicemici settimanali/mensili e gestire gli alert generati dal sistema.", style_bullet))
    story.append(Paragraph("• <b>Amministratore del Servizio:</b> responsabile del censimento iniziale delle anagrafiche, dell'abilitazione delle credenziali e dell'associazione biunivoca tra paziente e medico specialista di riferimento.", style_bullet))

    story.append(Paragraph("1.3 Stack Tecnologico Adottato", style_h2))
    story.append(Paragraph(
        "In conformità ai vincoli imposti dal corso di <i>Ingegneria del Software</i> (che prescrive l'utilizzo di un linguaggio orientato agli oggetti, una base di dati relazionale e un'interfaccia grafica accessibile), "
        "si è optato per un'architettura web-based interamente sviluppata in <b>Python</b> e <b>Flask</b>. Di seguito si riporta la tabella di sintesi delle tecnologie impiegate e delle relative motivazioni architetturali.",
        style_body
    ))

    tech_data = [
        [Paragraph("Livello", style_table_header), Paragraph("Tecnologia", style_table_header), Paragraph("Versione", style_table_header), Paragraph("Ruolo nel Sistema", style_table_header), Paragraph("Motivazione Architetturale", style_table_header)],
        [
            Paragraph("<b>Linguaggio</b>", style_table_cell),
            Paragraph("Python", style_table_cell),
            Paragraph("3.11+", style_table_cell),
            Paragraph("Sviluppo dell'intera logica di business, DAOs, modelli e suite di test", style_table_cell),
            Paragraph("Linguaggio OO moderno, fortemente tipizzabile, sintetico e privo del boilerplate tipico di Java.", style_table_cell)
        ],
        [
            Paragraph("<b>Web Framework</b>", style_table_cell),
            Paragraph("Flask", style_table_cell),
            Paragraph("3.0+", style_table_cell),
            Paragraph("Routing HTTP, gestione sessioni sicure e architettura a Blueprint", style_table_cell),
            Paragraph("Microframework minimale che consente il controllo totale su ogni livello MVC senza magia implicita.", style_table_cell)
        ],
        [
            Paragraph("<b>Base di Dati</b>", style_table_cell),
            Paragraph("SQLite3", style_table_cell),
            Paragraph("3.40+", style_table_cell),
            Paragraph("Persistenza dati relazionali e audit trail medico", style_table_cell),
            Paragraph("RDBMS relazionale ACID a file, conforme alle specifiche didattiche. Integrità referenziale garantita via <code>PRAGMA foreign_keys = ON</code>.", style_table_cell)
        ],
        [
            Paragraph("<b>Accesso Dati</b>", style_table_cell),
            Paragraph("SQL Raw (DAO)", style_table_cell),
            Paragraph("Standard ANSI", style_table_cell),
            Paragraph("Interrogazioni esplicite e parametrizzate per la persistenza", style_table_cell),
            Paragraph("<b>Rispetto tassativo del divieto di ORM</b> (No SQLAlchemy). Centralizzazione query nel pattern DAO e protezione totale da SQL Injection.", style_table_cell)
        ],
        [
            Paragraph("<b>Presentation</b>", style_table_cell),
            Paragraph("Jinja2 + Bootstrap", style_table_cell),
            Paragraph("5.3+", style_table_cell),
            Paragraph("Generazione viste HTML responsive e accessibili", style_table_cell),
            Paragraph("Design ottimizzato per utenza geriatrica: font ad alta leggibilità, contrasti nitidi, pulsanti ampi e feedback chiari.", style_table_cell)
        ],
        [
            Paragraph("<b>Testing</b>", style_table_cell),
            Paragraph("unittest (PyUnit)", style_table_cell),
            Paragraph("Standard lib", style_table_cell),
            Paragraph("Esecuzione automatizzata di Unit e System Test E2E", style_table_cell),
            Paragraph("Collaudo dell'intero stack applicativo (client HTTP Flask simulato + DB di test isolato in memoria/disco).", style_table_cell)
        ]
    ]
    t_tech = Table(tech_data, colWidths=[70, 75, 50, 150, 165])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_tech)

    story.append(PageBreak())

    # =========================================================================
    # CAPITOLO 2: ANALISI DEI REQUISITI
    # =========================================================================
    story.append(Paragraph("2. Analisi dei Requisiti", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("2.1 Elicitation e User Needs", style_h2))
    story.append(Paragraph(
        "Il processo di Requirements Engineering ha attraversato le 4 fasi canoniche dell'ingegneria del software: "
        "<i>Elicitation</i>, <i>Analisi</i>, <i>Definizione e Specifica</i>, e <i>Validazione</i>. "
        "Dall'analisi delle esigenze dei portatori di interesse (stakeholder) sono stati formalizzati i seguenti bisogni utente:",
        style_body
    ))
    story.append(Paragraph("• <b>Bisogni Paziente:</b> autenticazione protetta; inserimento giornaliero glicemie (prima/dopo pasti); registrazione puntuale farmaci assunti; segnalazione sintomi/comorbilità concomitanti; ricezione alert in caso di dimenticanze; messaggistica diretta col diabetologo.", style_bullet))
    story.append(Paragraph("• <b>Bisogni Medico:</b> autenticazione e accesso all'elenco pazienti; consultazione fascicolo sanitario (fattori di rischio e patologie); prescrizione/modifica terapie (farmaco, frequenza, dose, note); sintesi grafica glicemie (settimanale/mensile); ricezione allarmi per soglie superate o mancata aderenza (>3 giorni); tracciamento immutabile delle modifiche cliniche (Audit Trail).", style_bullet))
    story.append(Paragraph("• <b>Bisogni Amministratore:</b> censimento anagrafico iniziale dei profili (medici e pazienti) e creazione del legame di cura tra paziente e specialista.", style_bullet))

    story.append(Paragraph("2.2 Requisiti Funzionali (FR - Functional Requirements)", style_h2))
    story.append(Paragraph("I bisogni utente sono stati tradotti nei 13 Requisiti Funzionali cardine del sistema, riassunti nella seguente tabella:", style_body))

    rf_data = [
        [Paragraph("ID", style_table_header), Paragraph("Descrizione Sintetica del Requisito", style_table_header), Paragraph("Attore Coinvolto", style_table_header), Paragraph("Priorità", style_table_header)],
        [Paragraph("<b>FR1</b>", style_table_cell_bold), Paragraph("Autenticazione sicura tramite credenziali con indirizzamento dinamico all'interfaccia di competenza del ruolo.", style_table_cell), Paragraph("Tutti", style_table_cell), Paragraph("Alta (Must)", style_table_cell)],
        [Paragraph("<b>FR2</b>", style_table_cell_bold), Paragraph("Configurazione iniziale utenze: censimento anagrafico e associazione del paziente al medico curante.", style_table_cell), Paragraph("Amministratore", style_table_cell), Paragraph("Alta (Must)", style_table_cell)],
        [Paragraph("<b>FR3.1</b>", style_table_cell_bold), Paragraph("Registrazione delle rilevazioni glicemiche giornaliere (valore numerico in mg/dL, data, ora e contesto rispetto al pasto).", style_table_cell), Paragraph("Paziente", style_table_cell), Paragraph("Alta (Must)", style_table_cell)],
        [Paragraph("<b>FR3.2</b>", style_table_cell_bold), Paragraph("Segnalazione eventi clinici concomitanti: sintomi insorti, patologie intercorrenti e terapie farmacologiche parallele.", style_table_cell), Paragraph("Paziente", style_table_cell), Paragraph("Alta (Must)", style_table_cell)],
        [Paragraph("<b>FR4</b>", style_table_cell_bold), Paragraph("Diario assunzione farmaci: registrazione di nome farmaco, data, orario e quantità assunta.", style_table_cell), Paragraph("Paziente", style_table_cell), Paragraph("Alta (Must)", style_table_cell)],
        [Paragraph("<b>FR5</b>", style_table_cell_bold), Paragraph("Gestione Terapie: definizione, visualizzazione e aggiornamento della terapia (farmaco, frequenza, dose, indicazioni).", style_table_cell), Paragraph("Medico", style_table_cell), Paragraph("Alta (Must)", style_table_cell)],
        [Paragraph("<b>FR6</b>", style_table_cell_bold), Paragraph("Verifica coerenza assunzioni: validazione incrociata automatica tra dosi assunte dal paziente e prescrizione attiva.", style_table_cell), Paragraph("Sistema", style_table_cell), Paragraph("Alta (Must)", style_table_cell)],
        [Paragraph("<b>FR7</b>", style_table_cell_bold), Paragraph("Fascicolo clinico del paziente: consultazione e aggiornamento di fattori di rischio (fumo, alcol, obesità) e comorbilità.", style_table_cell), Paragraph("Medico", style_table_cell), Paragraph("Alta (Must)", style_table_cell)],
        [Paragraph("<b>FR8</b>", style_table_cell_bold), Paragraph("Visualizzazione andamento clinico: cruscotto di sintesi con grafici e statistiche aggregate settimanali e mensili.", style_table_cell), Paragraph("Medico", style_table_cell), Paragraph("Alta (Must)", style_table_cell)],
        [Paragraph("<b>FR9</b>", style_table_cell_bold), Paragraph("Alert al paziente: sollecito visivo in dashboard in caso di mancata registrazione dell'assunzione terapeutica.", style_table_cell), Paragraph("Sistema / Paziente", style_table_cell), Paragraph("Alta (Must)", style_table_cell)],
        [Paragraph("<b>FR10</b>", style_table_cell_bold), Paragraph("Alert al medico per soglie glicemiche: generazione avvisi differenziati (WARNING per sforamenti lievi, CRITICAL per ipoglicemie severe).", style_table_cell), Paragraph("Sistema / Medico", style_table_cell), Paragraph("Alta (Must)", style_table_cell)],
        [Paragraph("<b>FR11</b>", style_table_cell_bold), Paragraph("Comunicazione medico-paziente: modulo di messaggistica interna con simulazione di recapito email al medico curante.", style_table_cell), Paragraph("Paziente / Medico", style_table_cell), Paragraph("Media (Should)", style_table_cell)],
        [Paragraph("<b>FR12</b>", style_table_cell_bold), Paragraph("Audit Trail medico-legale: tracciamento inalterabile in modalità append-only di ogni operazione di aggiornamento clinico.", style_table_cell), Paragraph("Sistema / Medico", style_table_cell), Paragraph("Alta (Must)", style_table_cell)],
        [Paragraph("<b>FR13</b>", style_table_cell_bold), Paragraph("Alert aderenza terapeutica: rilevamento di mancata assunzione farmaci per oltre 3 giorni consecutivi con notifica al medico.", style_table_cell), Paragraph("Sistema / Medico", style_table_cell), Paragraph("Alta (Must)", style_table_cell)]
    ]
    t_rf = Table(rf_data, colWidths=[40, 260, 110, 100])
    t_rf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_rf)

    story.append(Spacer(1, 10))
    story.append(Paragraph("2.3 Requisiti Non Funzionali (NFR)", style_h2))
    story.append(Paragraph("• <b>NFR1 - Vincoli di Implementazione e Piattaforma:</b> software sviluppato in linguaggio Orientato agli Oggetti puro (Python 3.11), architettura web basata su Flask, con interfaccia grafica (GUI) e base di dati relazionale SQLite3 gestita senza ORM.", style_bullet))
    story.append(Paragraph("• <b>NFR2 - Integrità e Immutabilità (Security Audit):</b> il registro di audit (FR12) deve essere fisicamente inalterabile (pattern <i>append-only</i>). Nessun utente, neppure con privilegi amministrativi, può modificare o eliminare record storici di log clinico.", style_bullet))
    story.append(Paragraph("• <b>NFR3 - Usabilità e Accessibilità Geriatrica (UI Design):</b> l'interfaccia paziente è progettata con layout semplificato, pulsanti ad ampia area di clic, contrasti cromatici conformi e messaggi di errore intuitivi, per agevolare l'interazione da parte di pazienti anziani con scarse competenze informatiche.", style_bullet))
    story.append(Paragraph("• <b>NFR4 - Riservatezza e Controllo Accessi:</b> segregazione ferrea dei dati clinici basata sul principio del minimo privilegio: il paziente visualizza unicamente i propri dati sanitari; il medico accede solo ai pazienti registrati sotto la propria cura; l'amministratore gestisce account senza accesso ai diari sanitari.", style_bullet))

    story.append(Spacer(1, 10))
    story.append(Paragraph("2.4 Analisi delle Ambiguità, Assunzioni e Prioritizzazione MoSCoW", style_h2))
    story.append(Paragraph(
        "In fase di analisi dei requisiti sono state risolte tre ambiguità cardine della traccia didattica: "
        "<b>1) Incoerenza Farmaco/Terapia:</b> il sistema non deve bloccare il salvataggio (il paziente potrebbe aver realmente commesso un errore posologico), ma registra l'evento notificando un <i>Warning</i> visivo al paziente e aprendo un alert nel cruscotto del medico. "
        "<b>2) Allarmi per Gravità:</b> per valori glicemici lievemente fuori soglia (131-160 mg/dL a digiuno) viene generato un allarme di severità <i>WARNING</i> (badge visivo); per valori critici (<70 mg/dL o >250 mg/dL) scatta un allarme di severità <i>CRITICAL</i> con simulazione immediata di dispaccio email d'urgenza. "
        "<b>3) Check Aderenza 3 Giorni:</b> la verifica dei 3 giorni consecutivi di mancata assunzione viene calcolata dinamicamente all'accesso e ad ogni inserimento tramite query temporale rispetto alla prescrizione attiva.",
        style_body
    ))
    story.append(Paragraph(
        "Tutti i requisiti sopra descritti sono stati classificati con metodo <b>MoSCoW</b>: la quasi totalità delle funzionalità richieste dalla traccia d'esame è stata classificata come <b>MUST</b> (indispensabile), mentre la messaggistica interna simulata è stata catalogata come <b>SHOULD</b>.",
        style_body
    ))

    story.append(PageBreak())

    # =========================================================================
    # CAPITOLO 3: MODELLAZIONE DEI REQUISITI E USE CASE
    # =========================================================================
    story.append(Paragraph("3. Modellazione dei Requisiti e Use Case", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("3.1 Schede Dettagliate degli Attori", style_h2))
    story.append(Paragraph("In conformità ai canoni dell'ingegneria del software, gli attori del sistema sono stati formalizzati mediante schede di profilo dettagliate:", style_body))

    actors_data = [
        [
            Paragraph("<b>PAZIENTE DIABETICO</b>", style_table_header),
            Paragraph("<b>MEDICO DIABETOLOGO</b>", style_table_header),
            Paragraph("<b>AMMINISTRATORE DEL SERVIZIO</b>", style_table_header)
        ],
        [
            Paragraph(
                "<b>Definizione:</b> Persona affetta da diabete di tipo 2 in cura ambulatoriale.<br/>"
                "<b>Obiettivi:</b> Registrare quotidianamente glicemie e farmaci, segnalare sintomi, visualizzare lo stato della propria terapia.<br/>"
                "<b>Frequenza d'uso:</b> Più volte al giorno (prima/dopo pasti).<br/>"
                "<b>Competenze:</b> Uso base di un comune web browser.<br/>"
                "<b>Vincolo distintivo:</b> Associato a un solo medico curante.",
                style_table_cell
            ),
            Paragraph(
                "<b>Definizione:</b> Medico specialista in diabetologia e malattie metaboliche.<br/>"
                "<b>Obiettivi:</b> Supervisionare i pazienti, prescrivere terapie, consultare andamenti glicemici, gestire gli allarmi.<br/>"
                "<b>Frequenza d'uso:</b> Quotidiana / lavorativa.<br/>"
                "<b>Competenze:</b> Competenze cliniche e d'uso di software sanitario.<br/>"
                "<b>Vincolo distintivo:</b> Ha la responsabilità medico-legale tracciata su audit trail.",
                style_table_cell
            ),
            Paragraph(
                "<b>Definizione:</b> Responsabile del servizio clinico e dell'infrastruttura.<br/>"
                "<b>Obiettivi:</b> Censimento utenti, creazione credenziali e associazione paziente-medico.<br/>"
                "<b>Frequenza d'uso:</b> Saltuaria / Configurazione iniziale.<br/>"
                "<b>Competenze:</b> Competenze gestionali e amministrative.<br/>"
                "<b>Vincolo distintivo:</b> Non ha accesso ai dati clinici sensibili dei pazienti.",
                style_table_cell
            )
        ]
    ]
    t_actors = Table(actors_data, colWidths=[170, 170, 170])
    t_actors.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('BACKGROUND', (0,1), (-1,1), c_light),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_actors)

    story.append(Spacer(1, 10))
    story.append(Paragraph("3.2 Use Case Diagram Globale", style_h2))
    story.append(Paragraph("Il diagramma seguente modella visivamente tutte le interazioni tra gli attori e i casi d'uso offerti dalla piattaforma TeleDiabete:", style_body))

    img_uc_global = get_scaled_image(os.path.join(allegati_dir, "UseCaseDiagram.jpg"), max_height=260)
    if img_uc_global:
        story.append(KeepTogether([img_uc_global, Paragraph("Figura 3.1: Use Case Diagram Globale del Sistema TeleDiabete", style_caption)]))

    story.append(Spacer(1, 8))
    story.append(Paragraph("3.3 Schede di Specifica dei Casi d'Uso Principali", style_h2))

    # UC1
    story.append(Paragraph("<b>UC1: Registrazione Rilevazione Glicemica (Paziente) — Soddisfa FR3.1, FR10</b>", style_h3))
    story.append(Paragraph(
        "<b>Breve Descrizione:</b> Il paziente inserisce una nuova rilevazione giornaliera della glicemia (valore in mg/dL, data, ora e contesto pre/post prandiale). "
        "Il sistema valida i dati, registra la misurazione e valuta le soglie cliniche: se il valore è anomalo, innesca l'estensione <code>InviaNotificaAllarmeGlicemia</code>.<br/>"
        "<b>Precondizioni:</b> Paziente autenticato nel portale.<br/>"
        "<b>Flusso Principale:</b> 1. Il paziente seleziona 'Aggiungi Rilevazione'; 2. Il sistema mostra il form; 3. Il paziente inserisce valore, data, ora, contesto e conferma; "
        "4. Il sistema valida i dati; 5. Il sistema persiste la rilevazione nel DB; 6. Il sistema valuta le soglie (80-130 a digiuno, &lt;180 post-pasto) [Extension Point: valoriFuoriSoglia]; "
        "7. Mostra messaggio flash di conferma.<br/>"
        "<b>Flusso Alternativo 1.1 (Dati Non Validi):</b> In caso di campi vuoti o valore glicemico non positivo, il sistema rigetta l'inserimento e mostra gli errori evidenziati.<br/>"
        "<b>Punto di Estensione 1.2 (InviaNotificaAllarmeGlicemia):</b> Se il valore supera le soglie, calcola la severità (WARNING o CRITICAL), crea il record nella tabella alerts e, in caso critico, invia una email al medico curante.",
        style_body
    ))

    # UC2
    story.append(Paragraph("<b>UC2: Creazione / Gestione Terapia (Medico) — Soddisfa FR5, FR12</b>", style_h3))
    story.append(Paragraph(
        "<b>Breve Descrizione:</b> Il medico curante prescrive o aggiorna la terapia farmacologica per un paziente in cura (farmaco, frequenza giornaliera, dosaggio per assunzione, indicazioni temporali). "
        "Il sistema persiste la terapia e include obbligatoriamente il tracciamento inalterabile su Audit Trail.<br/>"
        "<b>Precondizioni:</b> Medico autenticato con paziente selezionato.<br/>"
        "<b>Flusso Principale:</b> 1. Il medico accede al form terapia; 2. Visualizza l'eventuale terapia attiva; 3. Compila farmaco, dosi e note; 4. Il sistema valida i dati; "
        "5. Salva la terapia nel DB; 6. <i>include(RegistraAuditLog)</i>: scrive il log immutabile con ID medico, ID paziente, azione 'UPDATE_THERAPY' e timestamp; 7. Mostra notifica di successo.<br/>"
        "<b>Flusso Alternativo 2.1 (Campi Mancanti):</b> Notifica di errore e riproposta del form.<br/>"
        "<b>Flusso Alternativo 2.2 (Annulla):</b> Il medico cancella l'operazione; nessun dato e nessun log vengono scritti.",
        style_body
    ))

    # UC3
    story.append(Paragraph("<b>UC3: Registrazione Assunzione Farmaco (Paziente) — Soddisfa FR4, FR6, FR13</b>", style_h3))
    story.append(Paragraph(
        "<b>Breve Descrizione:</b> Il paziente annota nel diario l'avvenuta assunzione di un farmaco. Il sistema memorizza l'evento e verifica la piena conformità con la prescrizione attiva redatta dal diabetologo.<br/>"
        "<b>Precondizioni:</b> Paziente autenticato nel portale.<br/>"
        "<b>Flusso Principale:</b> 1. Il paziente accede alla schermata diario farmaci; 2. Inserisce farmaco, dose, orario e conferma; 3. Il sistema convalida i formati; "
        "4. Salva il record in <code>medication_intakes</code> (azzerando contestualmente il contatore di mancata aderenza dei 3 giorni); 5. Confronta il farmaco e la dose con la prescrizione attiva "
        "[Extension Point: incongruenzaTerapia]; 6. Ritorna esito e redirect al diario.<br/>"
        "<b>Punto di Estensione 3.2 (MostraAvvisoIncoerenza):</b> Se il farmaco o la dose non corrispondono alla prescrizione, l'assunzione viene comunque salvata, ma il sistema genera un warning per il paziente e crea un alert di severità WARNING sul cruscotto del medico.",
        style_body
    ))

    story.append(Spacer(1, 6))
    story.append(Paragraph("3.4 Schede degli Altri Use Case di Sistema", style_h2))
    story.append(Paragraph("• <b>UC4 (Autenticazione al Sistema - Tutti):</b> verifica delle credenziali email/password hashate; inizializzazione sessione Flask sicura con discriminazione del ruolo (Paziente, Medico, Admin).", style_bullet))
    story.append(Paragraph("• <b>UC5 (Configurazione Iniziale Utenze - Admin):</b> registrazione anagrafica di nuovi medici e pazienti, con associazione del paziente al medico curante.", style_bullet))
    story.append(Paragraph("• <b>UC6 (Segnalazione Eventi Clinici - Paziente):</b> annotazione di sintomi insorti, comorbilità o farmaci concomitanti con date di inizio e fine periodo.", style_bullet))
    story.append(Paragraph("• <b>UC7 (Aggiornamento Fascicolo Paziente - Medico):</b> gestione dei fattori di rischio (fumo, obesità, alcol, ipertensione) con contestuale scrittura su Audit Log.", style_bullet))
    story.append(Paragraph("• <b>UC8 (Visualizzazione Andamento Clinico - Medico):</b> elaborazione statistica e rendering grafico dei valori glicemici settimanali e mensili per l'adeguamento terapeutico.", style_bullet))
    story.append(Paragraph("• <b>UC9 (Invio Comunicazioni E-mail - Paziente/Medico):</b> invio e consultazione messaggi diretti con simulazione a console del dispaccio email.", style_bullet))

    story.append(PageBreak())

    # =========================================================================
    # MODELLAZIONE CONCETTUALE E MATRICE DI TRACCIABILITÀ
    # =========================================================================
    story.append(Paragraph("3.5 Modellazione Concettuale del Dominio (Class Diagram Concettuale)", style_h2))
    story.append(Paragraph(
        "Il Class Diagram Concettuale modella le entità di dominio del problema in modo agnostico rispetto all'implementazione software e alla tecnologia di persistenza, "
        "evidenziando i vincoli di cardinalità e le relazioni semantiche che legano pazienti, medici, rilevazioni, terapie, assunzioni e avvisi:",
        style_body
    ))

    img_cd_conc = get_scaled_image(os.path.join(allegati_dir, "ClassDiagram_Concettuale.jpg"), max_width=510, max_height=360)
    if img_cd_conc:
        story.append(KeepTogether([img_cd_conc, Paragraph("Figura 3.2: Class Diagram della Modellazione Concettuale del Dominio", style_caption)]))

    story.append(PageBreak())

    story.append(Paragraph("3.6 Matrice di Tracciabilità Requisiti ↔ Use Case ↔ Test Case", style_h2))
    story.append(Paragraph(
        "La Matrice di Tracciabilità garantisce che ciascun requisito funzionale e non funzionale sia coperto da almeno un caso d'uso e verificato da una procedura di collaudo formalizzata:",
        style_body
    ))

    img_matrice = get_scaled_image(os.path.join(allegati_dir, "MatriceDiTracciabilita.jpg"), max_width=510, max_height=340)
    if img_matrice:
        story.append(KeepTogether([img_matrice, Paragraph("Figura 3.3: Matrice di Tracciabilità dei Requisiti di Sistema", style_caption)]))

    story.append(Spacer(1, 10))

    # Tabella di tracciabilità sintetica
    tracc_data = [
        [Paragraph("Requisito", style_table_header), Paragraph("Use Case Correlati", style_table_header), Paragraph("Casi di Test Associati", style_table_header), Paragraph("Copertura nel Software", style_table_header)],
        [Paragraph("<b>FR1, NFR4</b>", style_table_cell_bold), Paragraph("UC4 (Login)", style_table_cell), Paragraph("TC01, TC02", style_table_cell), Paragraph("AuthController, AuthService, UserDAO", style_table_cell)],
        [Paragraph("<b>FR2</b>", style_table_cell_bold), Paragraph("UC5 (Setup Utenze)", style_table_cell), Paragraph("TC03", style_table_cell), Paragraph("AdminController, PatientService, PatientDAO", style_table_cell)],
        [Paragraph("<b>FR3.1, FR10</b>", style_table_cell_bold), Paragraph("UC1 (Rilevazione Glicemica)", style_table_cell), Paragraph("TC04, TC05, TC06, TC07", style_table_cell), Paragraph("PatientController, MeasurementService, AlertDAO", style_table_cell)],
        [Paragraph("<b>FR3.2</b>", style_table_cell_bold), Paragraph("UC6 (Eventi Clinici)", style_table_cell), Paragraph("TC08", style_table_cell), Paragraph("PatientController, ClinicalEventDAO", style_table_cell)],
        [Paragraph("<b>FR4, FR6, FR13</b>", style_table_cell_bold), Paragraph("UC3 (Assunzione Farmaci)", style_table_cell), Paragraph("TC09, TC10, TC11, TC18", style_table_cell), Paragraph("PatientController, TherapyService, MedicationIntakeDAO", style_table_cell)],
        [Paragraph("<b>FR5, FR12, NFR2</b>", style_table_cell_bold), Paragraph("UC2 (Gestione Terapia)", style_table_cell), Paragraph("TC12, TC13, TC14, TC20", style_table_cell), Paragraph("DoctorController, TherapyService, AuditService, AuditLogDAO", style_table_cell)],
        [Paragraph("<b>FR7</b>", style_table_cell_bold), Paragraph("UC7 (Fascicolo Clinico)", style_table_cell), Paragraph("TC15", style_table_cell), Paragraph("DoctorController, MedicalRecordService, MedicalRecordDAO", style_table_cell)],
        [Paragraph("<b>FR8</b>", style_table_cell_bold), Paragraph("UC8 (Trend Clinici)", style_table_cell), Paragraph("TC16", style_table_cell), Paragraph("DoctorController, MeasurementService, MeasurementDAO", style_table_cell)],
        [Paragraph("<b>FR9</b>", style_table_cell_bold), Paragraph("Sistema (Alert Paziente)", style_table_cell), Paragraph("TC17", style_table_cell), Paragraph("TherapyService, AlertDAO, Patient dashboard", style_table_cell)],
        [Paragraph("<b>FR11</b>", style_table_cell_bold), Paragraph("UC9 (Messaggistica)", style_table_cell), Paragraph("TC19", style_table_cell), Paragraph("MessageService, MessageDAO, Controllers", style_table_cell)],
        [Paragraph("<b>NFR1, NFR3</b>", style_table_cell_bold), Paragraph("Architettura / GUI", style_table_cell), Paragraph("TC21, TC22", style_table_cell), Paragraph("DatabaseManager (SQLite), Bootstrap 5 Templates", style_table_cell)]
    ]
    t_tracc = Table(tracc_data, colWidths=[75, 120, 105, 210])
    t_tracc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_tracc)

    story.append(PageBreak())

    # =========================================================================
    # CAPITOLO 4: ARCHITETTURA DEL SISTEMA
    # =========================================================================
    story.append(Paragraph("4. Architettura del Sistema", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("4.1 Stili Architetturali Adottati", style_h2))
    story.append(Paragraph(
        "Il sistema TeleDiabete implementa un'architettura <b>Client-Server a tre livelli (Three-Tier)</b> su protocollo HTTP/HTTPS, "
        "in cui il client è configurato come <b>Thin Client</b> (un qualsiasi web browser moderno). "
        "L'intera logica di validazione, controllo degli accessi e persistenza risiede sul server, evitando l'esecuzione di codice non controllato sul dispositivo dell'utente.",
        style_body
    ))
    story.append(Paragraph(
        "A livello interno di backend, il sistema adotta rigorosamente il modello <b>Layered (Architettura a Strati)</b> "
        "coniugato al paradigma <b>Model-View-Controller (MVC)</b>. I quattro strati logici cooperano nel seguente modo:",
        style_body
    ))
    story.append(Paragraph("1. <b>Presentation Layer (Controller & View):</b> gestito tramite i Blueprints di Flask (`AuthController`, `PatientController`, `DoctorController`, `AdminController`) e i template Jinja2. Questo livello si limita ad autenticare la sessione, decodificare i payload HTTP, richiamare i Services di business e restituire le viste HTML con messaggi Flash contestualizzati.", style_bullet))
    story.append(Paragraph("2. <b>Business Logic Layer (Services):</b> rappresenta il nucleo applicativo (`MeasurementService`, `TherapyService`, `MedicalRecordService`, `AlertService`, `AuditService`, `MessageService`, `PatientService`). Questo strato incapsula al 100% le regole cliniche (calcolo soglie, verifica aderenza dei 3 giorni, coerenza assunzioni, dispatch email simulate), garantendo l'indipendenza totale del dominio dall'infrastruttura web.", style_bullet))
    story.append(Paragraph("3. <b>Data Access Layer (DAOs):</b> costituito dai Data Access Objects (`UserDAO`, `PatientDAO`, `TherapyDAO`, `MeasurementDAO`, `MedicationIntakeDAO`, `AlertDAO`, `MedicalRecordDAO`, `ClinicalEventDAO`, `MessageDAO`, `AuditLogDAO`). Ogni DAO incapsula query SQL raw parametriche, isolando SQLite dal resto del codice.", style_bullet))
    story.append(Paragraph("4. <b>Model Layer (Entities):</b> classi dati pure in Python che riflettono i record e gli aggregati del dominio (`User`, `Patient`, `Therapy`, `Measurement`, `Alert`, `MedicalRecord`, `ClinicalEvent`, `Message`, `AuditLog`).", style_bullet))

    story.append(Paragraph("4.2 Ciclo di Vita delle Richieste HTTP e Flusso MVC", style_h2))
    story.append(Paragraph(
        "Ogni interazione utente segue un ciclo di richiesta e risposta rigorosamente tracciato e protetto:",
        style_body
    ))
    story.append(Paragraph("• <b>Intercettazione e Sicurezza:</b> i decoratori `@login_required` e `@role_required(roles)` verificano preventivamente i cookie di sessione crittografati con chiave segreta. Le richieste non autorizzate ricevono un HTTP 302 Redirect con notifica d'errore.", style_bullet))
    story.append(Paragraph("• <b>Delega al Service Layer:</b> il Controller non esegue mai query SQL o calcoli di soglia, ma invoca il metodo del Service corrispondente.", style_bullet))
    story.append(Paragraph("• <b>Persistenza e Audit:</b> se l'operazione comporta modifiche cliniche sensibili, il Service coordina la scrittura atomica su DB e chiama `AuditService.log_operation()`.", style_bullet))
    story.append(Paragraph("• <b>Post-Redirect-Get (PRG):</b> le richieste POST che modificano lo stato completano con un redirect (PRG) alla dashboard, prevenendo reinvii duplicati del form in caso di refresh del browser.", style_bullet))

    story.append(Spacer(1, 10))

    # =========================================================================
    # CAPITOLO 5: DATABASE E MODELLO DATI
    # =========================================================================
    story.append(Paragraph("5. Database e Modello Dati", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("5.1 Schema Entità-Relazione (ERD)", style_h2))
    story.append(Paragraph(
        "Il modello relazionale è stato implementato su SQLite3 ed è incentrato sulla chiara separazione tra credenziali di autenticazione (`users`), "
        "dati anagrafico-clinici dei pazienti (`patients`, `medical_records`), prescrizioni mediche (`therapies`), "
        "diario del paziente (`glycemic_readings`, `medication_intakes`, `clinical_events`), notifiche d'allarme (`alerts`) e audit medico inalterabile (`audit_logs`).",
        style_body
    ))

    img_er = get_scaled_image(os.path.join(allegati_dir, "SchemaER.png"), max_height=260)
    if img_er:
        story.append(KeepTogether([img_er, Paragraph("Figura 5.1: Schema Entità-Relazione (ERD) del Database TeleDiabete", style_caption)]))

    story.append(Spacer(1, 8))
    story.append(Paragraph("5.2 Descrizione Dettagliata delle Tabelle Relazionali", style_h2))
    story.append(Paragraph("• <b>users:</b> anagrafica centrale (id PK, email UNIQUE, password_hash, first_name, last_name, role [0=Patient, 1=Doctor, 2=Admin], is_active).", style_bullet))
    story.append(Paragraph("• <b>patients:</b> specializzazione per il paziente (user_id PK FK su users, doctor_id FK su users indicante il diabetologo di riferimento, date_of_birth, gender).", style_bullet))
    story.append(Paragraph("• <b>medical_records:</b> fascicolo clinico stabile (patient_id PK FK, is_smoker, has_alcohol_issues, has_hypertension, has_obesity).", style_bullet))
    story.append(Paragraph("• <b>therapies:</b> prescrizioni terapeutiche attive e storiche (id PK, patient_id FK, doctor_id FK, drug_name, daily_doses, quantity_per_dose, instructions, is_active, start_date).", style_bullet))
    story.append(Paragraph("• <b>glycemic_readings:</b> log misurazioni del paziente (id PK, patient_id FK, glucose_level INT, reading_datetime DATETIME, meal_context ['BEFORE_MEAL', 'AFTER_MEAL']).", style_bullet))
    story.append(Paragraph("• <b>medication_intakes:</b> registrazioni assunzioni farmaci (id PK, patient_id FK, therapy_id FK, intake_datetime, quantity_taken, is_coherent BOOLEAN).", style_bullet))
    story.append(Paragraph("• <b>clinical_events:</b> segnalazione sintomi/comorbilità (id PK, patient_id FK, event_type ['SYMPTOM', 'PATHOLOGY', 'OTHER_DRUG'], description, start_date, end_date).", style_bullet))
    story.append(Paragraph("• <b>alerts:</b> allarmi clinici aperti o risolti (id PK, doctor_id FK, patient_id FK, severity ['WARNING', 'CRITICAL'], message, is_resolved, created_at).", style_bullet))
    story.append(Paragraph("• <b>messages:</b> comunicazioni interne (id PK, sender_id FK, receiver_id FK, content, sent_at).", style_bullet))
    story.append(Paragraph("• <b>audit_logs:</b> registro legale immutabile (id PK, timestamp, doctor_id FK, patient_id FK, action VARCHAR, details TEXT).", style_bullet))

    story.append(PageBreak())

    story.append(Paragraph("5.3 Codice DDL SQL Ufficiale per SQLite", style_h2))
    story.append(Paragraph(
        "Di seguito si riporta l'estratto formale del DDL SQL implementato in `app/database/schema.sql`, "
        "con l'esplicitazione di tutti i vincoli di integrità referenziale, chiavi esterne e indici:",
        style_body
    ))

    sql_code_text = """-- Schema DDL TeleDiabete (SQLite3) con integrità referenziale abilitata
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role INTEGER NOT NULL, -- 0: Patient, 1: Doctor, 2: Admin
    is_active BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS patients (
    user_id INTEGER PRIMARY KEY,
    doctor_id INTEGER NOT NULL,
    date_of_birth DATE,
    gender CHAR(1),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(doctor_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS therapies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    drug_name VARCHAR(100) NOT NULL,
    daily_doses INTEGER NOT NULL,
    quantity_per_dose REAL NOT NULL,
    instructions VARCHAR(255),
    is_active BOOLEAN DEFAULT 1,
    start_date DATE NOT NULL,
    FOREIGN KEY(patient_id) REFERENCES patients(user_id) ON DELETE CASCADE,
    FOREIGN KEY(doctor_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS glycemic_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    glucose_level INTEGER NOT NULL,
    reading_datetime DATETIME NOT NULL,
    meal_context VARCHAR(20) NOT NULL, -- 'BEFORE_MEAL', 'AFTER_MEAL'
    FOREIGN KEY(patient_id) REFERENCES patients(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    doctor_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    details TEXT,
    FOREIGN KEY(doctor_id) REFERENCES users(id),
    FOREIGN KEY(patient_id) REFERENCES patients(user_id)
);"""
    story.append(Preformatted(sql_code_text, style_code))

    story.append(Spacer(1, 10))
    story.append(Paragraph("5.4 Test e Meccanismi di Consistenza dei Dati (Vincolo Bioinformatica)", style_h2))
    story.append(Paragraph(
        "Essendo il progetto specificamente inquadrato nel curriculum orientato ai dati (Bioinformatica), "
        "sono stati implementati molteplici meccanismi a livello architetturale, logico e di database per garantire l'assoluta consistenza, "
        "l'integrità referenziale e l'inalterabilità dei dati:",
        style_body
    ))
    story.append(Paragraph("1. <b>Abilitazione Tassativa delle Chiavi Esterne (Foreign Keys):</b> per impostazione predefinita, SQLite disabilita il controllo dei vincoli relazionali. Nel file `DatabaseManager.py`, ogni singola connessione thread-local invoca all'apertura il comando <code>PRAGMA foreign_keys = ON;</code>. Ciò rende fisicamente impossibile inserire rilevazioni o prescrizioni per pazienti inesistenti o associare pazienti a medici privi di record nella tabella <code>users</code>.", style_bullet))
    story.append(Paragraph("2. <b>Vincoli di Unicità e Dominio:</b> il campo `email` nella tabella `users` è dichiarato `UNIQUE NOT NULL`. Qualsiasi tentativo di inserire account duplicati solleva un'eccezione `sqlite3.IntegrityError` catturata dal Service Layer. I ruoli sono tipizzati su dominio intero (0, 1, 2) e i contesti pasto su valori discreti ('BEFORE_MEAL', 'AFTER_MEAL').", style_bullet))
    story.append(Paragraph("3. <b>Integrità Medico-Legale: Pattern Append-Only su Audit Log:</b> per adempiere a NFR2 e ai requisiti medico-legali, la classe `AuditLogDAO` include unicamente il metodo di inserimento `insert_log` e metodi di sola lettura. Non esiste e non può esistere alcun metodo di `UPDATE` o `DELETE` su tale tabella. Qualsiasi manomissione è esclusa a livello architetturale.", style_bullet))
    story.append(Paragraph("4. <b>Verifica di Consistenza Terapia-Assunzioni:</b> all'atto della registrazione di una dose in `medication_intakes`, il sistema esegue una query incrociata verso `therapies` tramite `TherapyService.check_intake_consistency()`. Se il farmaco o la quantità differiscono dalla prescrizione attiva, il record viene memorizzato marcando il flag `is_coherent = 0` e scatenando l'alert di warning.", style_bullet))

    story.append(PageBreak())

    # =========================================================================
    # CAPITOLO 6: PROGETTAZIONE DEL SOFTWARE E DESIGN PATTERN
    # =========================================================================
    story.append(Paragraph("6. Progettazione del Software e Design Pattern", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("6.1 Class Diagram del Software Progettato", style_h2))
    story.append(Paragraph(
        "Il diagramma delle classi software illustra l'architettura a oggetti implementata nel codice Python, "
        "organizzata nei package <i>controllers</i> (Presentation), <i>services</i> (Business Logic), <i>daos</i> (Data Access) e <i>models</i> (Domain Entities):",
        style_body
    ))

    img_cd_soft = get_scaled_image(os.path.join(allegati_dir, "ClassDiagramDelSoftware.png"), max_height=260)
    if img_cd_soft:
        story.append(KeepTogether([img_cd_soft, Paragraph("Figura 6.1: Class Diagram dell'Architettura Software (Python / Flask)", style_caption)]))

    story.append(Spacer(1, 8))
    story.append(Paragraph("6.2 Discussione Approfondita dei Design Pattern Utilizzati", style_h2))
    story.append(Paragraph(
        "Al fine di garantire elevata coesione, basso accoppiamento, testabilità e robustezza, sono stati implementati i seguenti pattern architetturali e di design:",
        style_body
    ))

    story.append(Paragraph("1. <b>Data Access Object (DAO) Pattern:</b> "
        "Ogni entità di dominio possiede una classe DAO dedicata (`UserDAO`, `TherapyDAO`, `MeasurementDAO`, ecc.). "
        "Nessun controller o service esegue query SQL dirette. Questo approccio isola completamente il motore del database: se in futuro si volesse migrare da SQLite a PostgreSQL o MySQL, basterà riscrivere i DAO senza toccare una singola riga di logica di business. "
        "Tutte le query utilizzano la parametrizzazione con placeholder `?`, escludendo qualsiasi vulnerabilità da SQL Injection.",
        style_body
    ))

    story.append(Paragraph("2. <b>Singleton Pattern (DatabaseManager):</b> "
        "La gestione dell'accesso a SQLite è centralizzata nella classe `DatabaseManager`. Essendo SQLite un database a singolo file, aperture incontrollate di connessioni concorrenti possono causare lock sul file (`sqlite3.OperationalError: database is locked`). "
        "Il pattern Singleton, protetto da un `threading.Lock()` e abbinato a `threading.local()`, garantisce che esista un'unica istanza globale del manager e connessioni isolate e riutilizzabili per ciascun thread di richiesta.",
        style_body
    ))

    story.append(Paragraph("3. <b>Service Layer (Facade) Pattern:</b> "
        "Le classi Service fungono da punto di accesso unico e facciata per la logica di business. Quando il medico modifica una terapia, il controller non interagisce separatamente con `TherapyDAO` e `AuditLogDAO`, "
        "ma invoca unicamente `TherapyService.save_therapy()`. È il Service che si fa carico di validare i parametri, aggiornare la prescrizione, generare il log medico-legale e notificare eventuali osservatori.",
        style_body
    ))

    story.append(Paragraph("4. <b>Observer Pattern Semplificato (Sistema di Allertamento):</b> "
        "Il meccanismo di allertamento clinico opera in modo disaccoppiato. All'atto dell'inserimento di una misurazione o di un'assunzione, il service valuta le condizioni di pericolo e 'notifica' l'evento tramite `AlertService.create_alert()`. "
        "Il normale flusso di inserimento del paziente non viene interrotto o bloccato, ma l'evento produce la notifica persistente sul cruscotto del medico e la simulazione del dispaccio email.",
        style_body
    ))

    story.append(Paragraph("5. <b>Strictly Append-Only Pattern (Audit Trail Immutabile):</b> "
        "In conformità a NFR2, la classe `AuditLogDAO` espone esclusivamente metodi di scrittura append e lettura sequenziale. "
        "L'assenza deliberata di metodi `update` o `delete` garantisce a livello strutturale l'inalterabilità della traccia delle operazioni del medico.",
        style_body
    ))

    story.append(PageBreak())

    # =========================================================================
    # CAPITOLO 7: SCENARI DI INTERAZIONE (SEQUENCE E ACTIVITY DIAGRAMS)
    # =========================================================================
    story.append(Paragraph("7. Scenari di Interazione (Sequence & Activity Diagrams)", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("7.1 Sequence Diagram UC1: Registrazione Rilevazione Glicemica", style_h2))
    story.append(Paragraph(
        "Il sequence diagram illustra il flusso completo della richiesta HTTP POST per l'aggiunta di una misurazione, "
        "la validazione nel Service, il salvataggio su DB e l'estensione opzionale con creazione dell'alert in caso di valori fuori soglia:",
        style_body
    ))

    img_uc1 = get_scaled_image(os.path.join(allegati_dir, "UC1.png"), max_height=260)
    if img_uc1:
        story.append(KeepTogether([img_uc1, Paragraph("Figura 7.1: Sequence Diagram UC1 — Registrazione Misurazione Glicemica", style_caption)]))

    story.append(Spacer(1, 8))
    story.append(Paragraph("7.2 Sequence Diagram UC2: Gestione Terapia con Audit Log", style_h2))
    story.append(Paragraph(
        "Il sequence diagram illustra la definizione/modifica della terapia da parte del medico diabetologo, "
        "con l'inclusione obbligatoria (include) della scrittura atomica su tabella inalterabile di Audit Trail:",
        style_body
    ))

    img_uc2 = get_scaled_image(os.path.join(allegati_dir, "UC2.png"), max_height=260)
    if img_uc2:
        story.append(KeepTogether([img_uc2, Paragraph("Figura 7.2: Sequence Diagram UC2 — Gestione Terapia con Scrittura Audit Trail", style_caption)]))

    story.append(PageBreak())

    story.append(Paragraph("7.3 Sequence Diagram UC3: Assunzione Farmaco e Verifica Coerenza", style_h2))
    story.append(Paragraph(
        "Il sequence diagram illustra la registrazione dell'assunzione da parte del paziente, l'azzeramento del contatore di aderenza dei 3 giorni "
        "e la verifica automatica di conformità rispetto alla dose prescritta dal medico:",
        style_body
    ))

    img_uc3 = get_scaled_image(os.path.join(allegati_dir, "UC3.png"), max_width=510, max_height=360)
    if img_uc3:
        story.append(KeepTogether([img_uc3, Paragraph("Figura 7.3: Sequence Diagram UC3 — Registrazione Assunzione Farmaco e Verifica Coerenza", style_caption)]))

    story.append(PageBreak())

    story.append(Paragraph("7.4 Sequence Diagram UC4: Autenticazione al Sistema (Login)", style_h2))
    story.append(Paragraph(
        "Il sequence diagram mostra il processo di login: ricezione credenziali, estrazione record utente, validazione dell'hash crittografico della password "
        "e creazione della sessione Flask con reindirizzamento al cruscotto di ruolo:",
        style_body
    ))

    img_uc4 = get_scaled_image(os.path.join(allegati_dir, "UC4.png"), max_width=510, max_height=360)
    if img_uc4:
        story.append(KeepTogether([img_uc4, Paragraph("Figura 7.4: Sequence Diagram UC4 — Autenticazione al Sistema con Hashing e Sessione", style_caption)]))

    story.append(PageBreak())

    story.append(Paragraph("7.5 Activity Diagram: Navigazione e Operatività del Medico", style_h2))
    story.append(Paragraph(
        "L'Activity Diagram modella il workflow operativo del diabetologo all'interno della piattaforma: "
        "autenticazione, consultazione della dashboard con lista pazienti e allarmi pendenti, selezione di un paziente, "
        "esplorazione concorrente (fork) del fascicolo clinico, dei trend glicemici e del form di prescrizione, "
        "fino alla risoluzione degli alert clinici:",
        style_body
    ))

    img_act = get_scaled_image(os.path.join(allegati_dir, "ActivityDiagram.png"), max_height=380)
    if img_act:
        story.append(KeepTogether([img_act, Paragraph("Figura 7.5: Activity Diagram — Flusso di Navigazione e Attività Clinica del Medico", style_caption)]))

    story.append(PageBreak())

    # =========================================================================
    # CAPITOLO 8: PACKAGE DEL SOFTWARE E STRUTTURA MODULARE
    # =========================================================================
    story.append(Paragraph("8. Package del Software e Struttura Modulare", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("8.1 Organizzazione dell'Albero del Codice", style_h2))
    story.append(Paragraph(
        "Il codice sorgente del progetto (presente nella cartella `CodiceProgetto/`) è organizzato in una struttura modulare pulita e scalabile, "
        "ispirata ai canoni di sviluppo di applicazioni enterprise Flask:",
        style_body
    ))

    tree_text = """CodiceProgetto/
├── app.py                     # Entry point Flask e Application Factory
├── requirements.txt          # Dipendenze minime (Flask, Werkzeug)
├── seed_db.py                # Script di popolamento dati realistici di collaudo
├── tests/                    # Suite automatizzata di collaudo
│   └── test_system.py        # 16 Test di sistema completi (TC01-TC20)
└── app/
    ├── __init__.py           # Configurazione Blueprints e decoratori globali
    ├── database/             # Gestore Singleton SQLite (DatabaseManager.py, schema.sql)
    ├── models/               # Data Classes (User, Patient, Therapy, Measurement, Alert...)
    ├── daos/                 # Data Access Objects SQL Raw (UserDAO, TherapyDAO, AuditLogDAO...)
    ├── services/             # Business Logic Layer (AuthService, MeasurementService, TherapyService...)
    ├── controllers/          # Presentation Layer (AuthController, PatientController, DoctorController...)
    └── templates/            # Viste Jinja2 e layout Bootstrap 5 (auth/, patient/, doctor/, admin/)"""
    story.append(Preformatted(tree_text, style_code))

    story.append(Spacer(1, 8))
    story.append(Paragraph("8.2 Moduli Core e Responsabilità", style_h2))
    story.append(Paragraph("• <b>app/models/:</b> definisce le classi di dominio pure (es. `User`, `Patient`, `Therapy`, `Measurement`, `MedicationIntake`, `Alert`, `MedicalRecord`, `ClinicalEvent`, `Message`, `AuditLog`). Ogni classe incapsula campi, costruttori e metodi di utilità (come `to_dict()` o proprietà calcolate).", style_bullet))
    story.append(Paragraph("• <b>app/daos/:</b> implementa i Data Access Objects. Ciascun DAO (es. `TherapyDAO`, `MeasurementDAO`) riceve la connessione da `DatabaseManager` ed esegue istruzioni SQL parametriche. `AuditLogDAO` adotta la politica strettamente append-only per preservare l'integrità medico-legale.", style_bullet))
    story.append(Paragraph("• <b>app/services/:</b> racchiude la business logic clinica. Ad esempio, `MeasurementService` contiene le soglie numeriche (80-130 mg/dL a digiuno, 180 mg/dL post-prandiale) e le regole di allertamento (WARNING/CRITICAL); `TherapyService` valuta la coerenza delle assunzioni e calcola la mancata aderenza superiore a 3 giorni.", style_bullet))
    story.append(Paragraph("• <b>app/controllers/:</b> gestisce il routing HTTP mediante i Blueprint di Flask (`AuthController`, `PatientController`, `DoctorController`, `AdminController`). Le rotte sono protette dai decoratori `@login_required` e `@role_required` definiti in `auth_decorators.py`.", style_bullet))
    story.append(Paragraph("• <b>app/templates/ e Accessibilità Anziani (NFR3):</b> le pagine HTML sono state sviluppate con Bootstrap 5 in lingua italiana, impiegando caratteri tipografici ampi (1.1rem), contrasti cromatici conformi, card intuitive e messaggi flash d'errore o successo chiaramente visibili.", style_bullet))

    story.append(PageBreak())

    # =========================================================================
    # CAPITOLO 9: PIANO DI TESTING E VALIDAZIONE
    # =========================================================================
    story.append(Paragraph("9. Piano di Testing e Validazione", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("9.1 Obiettivo e Metodologia di Collaudo", style_h2))
    story.append(Paragraph(
        "La fase di verifica e validazione (V&V) del software è stata condotta adottando una strategia combinata "
        "<b>Black-Box</b> (verifica dei requisiti funzionali e dei flussi utente) e <b>White-Box</b> (integrità del codice, correttezza delle transazioni e gestione eccezioni). "
        "Tutti i test di sistema sono stati automatizzati mediante il framework standard `unittest` (PyUnit), impiegando il `test_client()` di Flask "
        "per simulare interazioni HTTP realistiche (autenticazione, invio form, gestione cookie e redirect) su un database di collaudo SQLite (`test_e2e.db`) popolato da `seed_db.py`.",
        style_body
    ))

    story.append(Paragraph("9.2 Ambiente di Esecuzione e Riproducibilità", style_h2))
    story.append(Paragraph(
        "L'intera suite di collaudo è completamente automatizzata, riproducibile e non richiede dipendenze esterne oltre a Flask. "
        "Il comando per eseguire i test dal terminale nella directory di progetto è:",
        style_body
    ))
    story.append(Preformatted("python3 -m unittest discover -s tests", style_code))

    story.append(Spacer(1, 6))
    story.append(Paragraph("9.3 Output del Terminale di Esecuzione della Test Suite", style_h2))
    story.append(Paragraph("Di seguito si riporta la traccia reale di esecuzione dei 16 test di sistema nel terminale, terminata con esito <b>OK (16 test superati con successo in 2.561 secondi)</b>:", style_body))

    test_terminal_output = """(.venv) simonedalprete@pop-os:~/Desktop/NomeArchivio/Progetto/CodiceProgetto$ python3 -m unittest discover -s tests
--- Inizializzazione e Popolamento Database TeleDiabete ---
[OK] Creato Utente Amministratore: admin@telemedicina.it (Password: admin123)
[OK] Creato Utente Medico: dott.mario.rossi@ospedale.it (Password: dottore123)
[OK] Creato Utente Paziente: giuseppe.verdi@email.it (Password: paziente123) associato a Dr. Mario Rossi
[OK] Inizializzato Fascicolo Clinico (Fattori di rischio: Ipertensione e Obesità)
[OK] Prescritta Terapia Iniziale: Metformina 500mg (2 volte al giorno)
[OK] Inserito Sintomo Iniziale: Spossatezza al risveglio
[OK] Inserite Misurazioni Glicemiche di base
--- Setup Completato con Successo! ---
.....[SIMULATED EMAIL TO DOCTOR #2] Oggetto: ALLARME CLINICO CRITICO - ALLARME CRITICO: Ipoglicemia grave (40 mg/dL, prima del pasto). Richiesto intervento immediato!
.........[SIMULATED EMAIL DISPATCH] Da: Giuseppe Verdi A: dott.mario.rossi@ospedale.it | Testo: Dottore, oggi sento un leggero capogiro dopo i pasti.
[SIMULATED EMAIL DISPATCH] Da: Mario Rossi A: giuseppe.verdi@email.it | Testo: Giuseppe, misura la glicemia subito e bevi un bicchiere d acqua.
..
----------------------------------------------------------------------
Ran 16 tests in 2.561s

OK"""
    story.append(Preformatted(test_terminal_output, style_code))

    story.append(PageBreak())

    story.append(Paragraph("9.4 Tabella Dettagliata dei 16 Test di Sistema Eseguiti", style_h2))
    story.append(Paragraph("La tabella seguente documenta formalmente ciascun test eseguito, indicando obiettivo, procedura, evidenza raccolta ed esito finale:", style_body))

    tests_summary_data = [
        [Paragraph("ID", style_table_header), Paragraph("Obiettivo del Test", style_table_header), Paragraph("Procedura Eseguita", style_table_header), Paragraph("Evidenza Raccolta e Risultato", style_table_header), Paragraph("Esito", style_table_header)],
        [
            Paragraph("<b>TC01</b>", style_table_cell_bold),
            Paragraph("Autenticazione e routing per ruolo (FR1, NFR4)", style_table_cell),
            Paragraph("POST /login con credenziali Paziente, Medico e Admin", style_table_cell),
            Paragraph("Redirect 302 alle rispettive dashboard di competenza", style_table_cell),
            Paragraph("<b>SUPERATO</b>", style_table_cell_bold)
        ],
        [
            Paragraph("<b>TC02</b>", style_table_cell_bold),
            Paragraph("Protezione rotte e password errata (FR1, NFR4)", style_table_cell),
            Paragraph("Tentativo login con password errata e accesso a /doctor/dashboard senza sessione", style_table_cell),
            Paragraph("Credenziali non valide evidenziate e redirect alla pagina di login", style_table_cell),
            Paragraph("<b>SUPERATO</b>", style_table_cell_bold)
        ],
        [
            Paragraph("<b>TC03</b>", style_table_cell_bold),
            Paragraph("Creazione utenze e associazione paziente (FR2, UC5)", style_table_cell),
            Paragraph("Admin invia POST /admin/create-doctor e POST /admin/create-patient con doctor_id", style_table_cell),
            Paragraph("Utenze inserite nel DB con password hashata e vincolo referenziale", style_table_cell),
            Paragraph("<b>SUPERATO</b>", style_table_cell_bold)
        ],
        [
            Paragraph("<b>TC04</b>", style_table_cell_bold),
            Paragraph("Inserimento glicemia normale a digiuno (FR3.1, UC1)", style_table_cell),
            Paragraph("Paziente registra 110 mg/dL prima del pasto", style_table_cell),
            Paragraph("Record salvato in glycemic_readings, nessun alert generato", style_table_cell),
            Paragraph("<b>SUPERATO</b>", style_table_cell_bold)
        ],
        [
            Paragraph("<b>TC05</b>", style_table_cell_bold),
            Paragraph("Sforamento soglia e alert WARNING (FR3.1, FR10)", style_table_cell),
            Paragraph("Paziente registra 150 mg/dL prima del pasto", style_table_cell),
            Paragraph("Misurazione salvata; creato alert WARNING; badge visibile in dashboard medico", style_table_cell),
            Paragraph("<b>SUPERATO</b>", style_table_cell_bold)
        ],
        [
            Paragraph("<b>TC06</b>", style_table_cell_bold),
            Paragraph("Ipoglicemia severa e allarme CRITICAL (FR3.1, FR10)", style_table_cell),
            Paragraph("Paziente registra 40 mg/dL prima del pasto", style_table_cell),
            Paragraph("Creato alert CRITICAL nel DB e simulato dispaccio email d'urgenza al medico", style_table_cell),
            Paragraph("<b>SUPERATO</b>", style_table_cell_bold)
        ],
        [
            Paragraph("<b>TC07</b>", style_table_cell_bold),
            Paragraph("Validazione input misurazione errata (FR3.1, UC1)", style_table_cell),
            Paragraph("Paziente invia valore negativo (-10 mg/dL)", style_table_cell),
            Paragraph("Rigetto con messaggio d'errore; nessun record salvato a DB", style_table_cell),
            Paragraph("<b>SUPERATO</b>", style_table_cell_bold)
        ],
        [
            Paragraph("<b>TC08</b>", style_table_cell_bold),
            Paragraph("Segnalazione sintomo/evento clinico (FR3.2, UC6)", style_table_cell),
            Paragraph("Paziente invia sintomo 'Forte emicrania e vertigini'", style_table_cell),
            Paragraph("Evento persistito in clinical_events con date corrette", style_table_cell),
            Paragraph("<b>SUPERATO</b>", style_table_cell_bold)
        ],
        [
            Paragraph("<b>TC09</b>", style_table_cell_bold),
            Paragraph("Assunzione farmaco conforme a terapia (FR4, FR6)", style_table_cell),
            Paragraph("Paziente registra assunzione Metformina 500mg dose 1.0", style_table_cell),
            Paragraph("Assunzione salvata con flag is_coherent=1; nessun alert", style_table_cell),
            Paragraph("<b>SUPERATO</b>", style_table_cell_bold)
        ],
        [
            Paragraph("<b>TC10</b>", style_table_cell_bold),
            Paragraph("Assunzione incoerente e alert warning (FR4, FR6)", style_table_cell),
            Paragraph("Paziente registra dose anomala (5.0 dosi anziché 1.0)", style_table_cell),
            Paragraph("Assunzione salvata; generato warning visivo e alert al medico", style_table_cell),
            Paragraph("<b>SUPERATO</b>", style_table_cell_bold)
        ],
        [
            Paragraph("<b>TC11</b>", style_table_cell_bold),
            Paragraph("Prescrizione terapia e Audit Log (FR5, FR12, NFR2)", style_table_cell),
            Paragraph("Medico salva nuova terapia per il paziente", style_table_cell),
            Paragraph("Terapia salvata a DB e record generato in audit_logs", style_table_cell),
            Paragraph("<b>SUPERATO</b>", style_table_cell_bold)
        ],
        [
            Paragraph("<b>TC12</b>", style_table_cell_bold),
            Paragraph("Aggiornamento fascicolo clinico (FR7, FR12)", style_table_cell),
            Paragraph("Medico aggiorna fattori di rischio del paziente (fumo, obesità)", style_table_cell),
            Paragraph("medical_records aggiornato e tracciato in audit_logs", style_table_cell),
            Paragraph("<b>SUPERATO</b>", style_table_cell_bold)
        ],
        [
            Paragraph("<b>TC13</b>", style_table_cell_bold),
            Paragraph("Rilevamento mancata aderenza 3 giorni (FR13)", style_table_cell),
            Paragraph("Verifica paziente privo di assunzioni registrate da >3 giorni", style_table_cell),
            Paragraph("Creato alert specifico di aderenza nel cruscotto del medico", style_table_cell),
            Paragraph("<b>SUPERATO</b>", style_table_cell_bold)
        ],
        [
            Paragraph("<b>TC14</b>", style_table_cell_bold),
            Paragraph("Messaggistica bilaterale medico-paziente (FR11, UC9)", style_table_cell),
            Paragraph("Scambio messaggi diretti tra paziente e diabetologo curante", style_table_cell),
            Paragraph("Messaggi persistiti in messages e simulazione email a console", style_table_cell),
            Paragraph("<b>SUPERATO</b>", style_table_cell_bold)
        ],
        [
            Paragraph("<b>TC15</b>", style_table_cell_bold),
            Paragraph("Visualizzazione andamenti clinici e trend (FR8, UC8)", style_table_cell),
            Paragraph("Medico consulta /doctor/patient/<id>/trends", style_table_cell),
            Paragraph("Statistiche aggregate e dati settimanali/mensili caricati", style_table_cell),
            Paragraph("<b>SUPERATO</b>", style_table_cell_bold)
        ],
        [
            Paragraph("<b>TC16</b>", style_table_cell_bold),
            Paragraph("Integrità Audit Trail e divieto update/delete (NFR2)", style_table_cell),
            Paragraph("Verifica architetturale DAO e immutabilità tabella audit_logs", style_table_cell),
            Paragraph("Pattern append-only verificato: integrità medico-legale garantita", style_table_cell),
            Paragraph("<b>SUPERATO</b>", style_table_cell_bold)
        ]
    ]

    t_tests = Table(tests_summary_data, colWidths=[35, 125, 145, 145, 60])
    t_tests.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light]),
        ('ALIGN', (4,1), (4,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_tests)

    # Costruzione finale del documento con NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESSO] Documento PDF generato correttamente: {output_pdf_path}")


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    allegati_path = os.path.join(base_dir, 'Allegati')
    output_pdf = os.path.join(base_dir, 'Documentazione_Progetto2_TeleDiabete.pdf')

    print(f"Directory Allegati: {allegati_path}")
    print(f"Destinazione PDF: {output_pdf}")

    create_documentation_pdf(output_pdf, allegati_path)
