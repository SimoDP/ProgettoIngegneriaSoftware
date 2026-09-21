from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from app.controllers.auth_decorators import patient_required
from app.services.MeasurementService import MeasurementService
from app.services.TherapyService import TherapyService
from app.services.MedicalRecordService import MedicalRecordService
from app.services.MessageService import MessageService
from app.services.PatientService import PatientService

patient_bp = Blueprint('patient', __name__)

measurement_service = MeasurementService()
therapy_service = TherapyService()
record_service = MedicalRecordService()
message_service = MessageService()
patient_service = PatientService()

@patient_bp.route('/patient/dashboard')
@patient_required
def dashboard():
    """Patient dashboard displaying overview, reminders, and active therapies."""
    patient_id = session['user_id']
    patient = patient_service.get_patient(patient_id)

    # FR9 / TC17: Daily reminder check for medication intake
    daily_reminder = therapy_service.check_patient_reminders(patient_id)

    # Load active therapies and recent readings
    active_therapies = therapy_service.get_active_therapies(patient_id)
    recent_readings = measurement_service.get_patient_readings(patient_id, limit=7)
    recent_intakes = therapy_service.get_patient_intakes(patient_id, limit=7)

    return render_template(
        'patient/dashboard.html',
        patient=patient,
        daily_reminder=daily_reminder,
        active_therapies=active_therapies,
        recent_readings=recent_readings,
        recent_intakes=recent_intakes
    )

@patient_bp.route('/measurement/add', methods=['GET', 'POST'])
@patient_required
def add_measurement():
    """UC1: Records a new glycemic reading and validates against clinical thresholds."""
    patient_id = session['user_id']

    if request.method == 'POST':
        glucose_val = request.form.get('glucose_level', '').strip()
        meal_context = request.form.get('meal_context', '').strip()
        reading_dt = request.form.get('reading_datetime', '').strip()

        try:
            reading_id, alert = measurement_service.record_measurement(
                patient_id=patient_id,
                glucose_level=glucose_val,
                reading_datetime=reading_dt,
                meal_context=meal_context
            )

            if alert:
                if alert.severity == 'CRITICAL':
                    flash(
                        f"Rilevazione registrata (#{reading_id}). ATTENZIONE: Valore critico ({glucose_val} mg/dL)! "
                        f"Il medico curante è stato avvisato d'urgenza.",
                        "danger"
                    )
                else:
                    flash(
                        f"Rilevazione registrata (#{reading_id}). Nota: il valore ({glucose_val} mg/dL) è fuori soglia; "
                        f"è stato generato un avviso per il medico.",
                        "warning"
                    )
            else:
                flash(f"Rilevazione glicemica registrata con successo ({glucose_val} mg/dL).", "success")

            return redirect(url_for('patient.dashboard'))

        except ValueError as e:
            flash(str(e), "danger")
            # Preserve user input on error (Flusso Alt. 1.1)
            return render_template(
                'patient/add_measurement.html',
                glucose_level=glucose_val,
                meal_context=meal_context,
                reading_datetime=reading_dt or datetime.now().strftime("%Y-%m-%dT%H:%M")
            )

    default_dt = datetime.now().strftime("%Y-%m-%dT%H:%M")
    return render_template('patient/add_measurement.html', reading_datetime=default_dt)

@patient_bp.route('/intake/add', methods=['GET', 'POST'])
@patient_required
def add_intake():
    """UC3: Records medication intake and checks consistency against prescribed therapy."""
    patient_id = session['user_id']
    active_therapies = therapy_service.get_active_therapies(patient_id)

    if request.method == 'POST':
        drug_name = request.form.get('drug_name', '').strip()
        quantity_taken = request.form.get('quantity_taken', '').strip()
        intake_dt = request.form.get('intake_datetime', '').strip()

        try:
            intake_id, is_consistent, warning_msg = therapy_service.record_intake(
                patient_id=patient_id,
                drug_name=drug_name,
                quantity_taken=quantity_taken,
                intake_datetime=intake_dt
            )

            # Extension Point 3.2: MostraAvvisoIncoerenza (TC10)
            if not is_consistent:
                flash(
                    f"Assunzione registrata con AVVISO: {warning_msg} "
                    f"La segnalazione di discordanza è stata inoltrata al medico curante.",
                    "warning"
                )
            else:
                flash(f"Assunzione del farmaco '{drug_name}' registrata correttamente!", "success")

            return redirect(url_for('patient.dashboard'))

        except ValueError as e:
            flash(str(e), "danger")
            return render_template(
                'patient/add_intake.html',
                active_therapies=active_therapies,
                drug_name=drug_name,
                quantity_taken=quantity_taken,
                intake_datetime=intake_dt or datetime.now().strftime("%Y-%m-%dT%H:%M")
            )

    default_dt = datetime.now().strftime("%Y-%m-%dT%H:%M")
    return render_template(
        'patient/add_intake.html',
        active_therapies=active_therapies,
        intake_datetime=default_dt
    )

@patient_bp.route('/patient/clinical-events', methods=['GET', 'POST'])
@patient_required
def clinical_events():
    """FR3.2 / UC6: Reporting and viewing symptoms, concurrent pathologies, and therapies."""
    patient_id = session['user_id']

    if request.method == 'POST':
        event_type = request.form.get('event_type', '').strip()
        description = request.form.get('description', '').strip()
        start_date = request.form.get('start_date', '').strip()
        end_date = request.form.get('end_date', '').strip()

        try:
            record_service.add_clinical_event(
                patient_id=patient_id,
                event_type=event_type,
                description=description,
                start_date=start_date,
                end_date=end_date if end_date else None
            )
            flash("Evento clinico registrato con successo nel tuo fascicolo.", "success")
            return redirect(url_for('patient.clinical_events'))
        except ValueError as e:
            flash(str(e), "danger")

    events = record_service.get_clinical_events(patient_id)
    return render_template('patient/clinical_events.html', events=events)

@patient_bp.route('/patient/clinical-events/<int:event_id>/delete', methods=['POST'])
@patient_required
def delete_clinical_event(event_id):
    """Deletes a clinical event registered by the patient."""
    patient_id = session['user_id']
    record_service.delete_clinical_event(event_id, patient_id)
    flash("Evento rimosso con successo.", "info")
    return redirect(url_for('patient.clinical_events'))

@patient_bp.route('/patient/messages', methods=['GET', 'POST'])
@patient_required
def messages():
    """FR11 / UC9: Sends communications / simulated email to the assigned doctor."""
    patient_id = session['user_id']
    patient = patient_service.get_patient(patient_id)

    if not patient:
        flash("Profilo paziente non trovato.", "danger")
        return redirect(url_for('patient.dashboard'))

    doctor_id = patient.doctor_id

    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        try:
            message_service.send_message(
                sender_id=patient_id,
                receiver_id=doctor_id,
                content=content
            )
            flash("Messaggio inviato con successo al tuo medico curante.", "success")
            return redirect(url_for('patient.messages'))
        except ValueError as e:
            flash(str(e), "danger")

    conversation = message_service.get_conversation(patient_id, doctor_id)
    return render_template(
        'patient/messages.html',
        patient=patient,
        conversation=conversation
    )
