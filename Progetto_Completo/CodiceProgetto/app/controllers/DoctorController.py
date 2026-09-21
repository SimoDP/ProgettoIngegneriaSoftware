from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.controllers.auth_decorators import doctor_required
from app.services.PatientService import PatientService
from app.services.TherapyService import TherapyService
from app.services.MeasurementService import MeasurementService
from app.services.MedicalRecordService import MedicalRecordService
from app.services.AlertService import AlertService
from app.services.MessageService import MessageService
from app.services.AuditService import AuditService

doctor_bp = Blueprint('doctor', __name__)

patient_service = PatientService()
therapy_service = TherapyService()
measurement_service = MeasurementService()
record_service = MedicalRecordService()
alert_service = AlertService()
message_service = MessageService()
audit_service = AuditService()

@doctor_bp.route('/doctor/dashboard')
@doctor_required
def dashboard():
    """
    Doctor dashboard:
    - Dynamically checks 3-day adherence for all assigned patients (FR13 / TC18)
    - Shows list of patients
    - Shows open clinical alerts
    """
    doctor_id = session['user_id']

    # Dynamic 3-day adherence evaluation on dashboard load (as per project spec)
    therapy_service.check_adherence_alerts_for_doctor(doctor_id)

    patients = patient_service.get_doctor_patients(doctor_id)
    unresolved_alerts = alert_service.get_unresolved_alerts(doctor_id)

    return render_template(
        'doctor/dashboard.html',
        patients=patients,
        alerts=unresolved_alerts
    )

@doctor_bp.route('/doctor/alert/<int:alert_id>/resolve', methods=['POST'])
@doctor_required
def resolve_alert(alert_id):
    """Marks an alert as handled and resolved, logging to audit trail."""
    doctor_id = session['user_id']
    success = alert_service.resolve_alert(alert_id, doctor_id)
    if success:
        flash(f"Avviso #{alert_id} contrassegnato come risolto.", "success")
    else:
        flash("Impossibile risolvere l'avviso specificato.", "danger")
    return redirect(url_for('doctor.dashboard'))

@doctor_bp.route('/doctor/patient/<int:patient_id>/dossier')
@doctor_required
def patient_dossier(patient_id):
    """Comprehensive clinical dossier of a patient (FR7, FR5, FR3.2)."""
    doctor_id = session['user_id']
    patient = patient_service.get_patient(patient_id)
    if not patient:
        flash("Paziente non trovato.", "danger")
        return redirect(url_for('doctor.dashboard'))

    # Record view action in audit trail
    audit_service.log_operation(doctor_id, "VIEW_PATIENT", patient_id, f"Consultazione fascicolo paziente {patient.full_name}")

    medical_record = record_service.get_patient_record(patient_id)
    active_therapies = therapy_service.get_active_therapies(patient_id)
    all_therapies = therapy_service.get_all_therapies(patient_id)
    clinical_events = record_service.get_clinical_events(patient_id)
    recent_readings = measurement_service.get_patient_readings(patient_id, limit=10)
    recent_intakes = therapy_service.get_patient_intakes(patient_id, limit=10)

    return render_template(
        'doctor/patient_dossier.html',
        patient=patient,
        medical_record=medical_record,
        active_therapies=active_therapies,
        all_therapies=all_therapies,
        clinical_events=clinical_events,
        recent_readings=recent_readings,
        recent_intakes=recent_intakes
    )

@doctor_bp.route('/doctor/patient/<int:patient_id>/trends')
@doctor_required
def patient_trends(patient_id):
    """FR8 / UC8: Weekly and monthly glycemic trends, summary and statistics."""
    patient = patient_service.get_patient(patient_id)
    if not patient:
        flash("Paziente non trovato.", "danger")
        return redirect(url_for('doctor.dashboard'))

    period = request.args.get('period', '30')
    days = 7 if period == '7' else 30

    report = measurement_service.get_summary_report(patient_id, days=days)

    return render_template(
        'doctor/patient_trends.html',
        patient=patient,
        report=report,
        days=days
    )

@doctor_bp.route('/doctor/patient/<int:patient_id>/therapy', methods=['GET', 'POST'])
@doctor_required
def manage_therapy(patient_id):
    """UC2 / FR5: Prescribe or update medication therapy with Audit Trail (FR12)."""
    doctor_id = session['user_id']
    patient = patient_service.get_patient(patient_id)
    if not patient:
        flash("Paziente non trovato.", "danger")
        return redirect(url_for('doctor.dashboard'))

    if request.method == 'POST':
        drug_name = request.form.get('drug_name', '').strip()
        daily_doses = request.form.get('daily_doses', '').strip()
        quantity_per_dose = request.form.get('quantity_per_dose', '').strip()
        instructions = request.form.get('instructions', '').strip()
        start_date = request.form.get('start_date', '').strip()

        try:
            th_id = therapy_service.save_therapy(
                patient_id=patient_id,
                doctor_id=doctor_id,
                drug_name=drug_name,
                daily_doses=daily_doses,
                quantity_per_dose=quantity_per_dose,
                instructions=instructions,
                start_date=start_date
            )
            flash(f"Terapia per '{drug_name}' salvata e registrata nell'Audit Log con successo.", "success")
            return redirect(url_for('doctor.patient_dossier', patient_id=patient_id))
        except ValueError as e:
            # Flusso Alt. 2.1: Campi non validi o mancanti
            flash(str(e), "danger")

    active_therapies = therapy_service.get_active_therapies(patient_id)
    return render_template(
        'doctor/manage_therapy.html',
        patient=patient,
        active_therapies=active_therapies
    )

@doctor_bp.route('/doctor/patient/<int:patient_id>/medical-record', methods=['POST'])
@doctor_required
def update_medical_record(patient_id):
    """UC7 / FR7: Updates patient risk factors and comorbidities with Audit Trail (FR12)."""
    doctor_id = session['user_id']
    patient = patient_service.get_patient(patient_id)
    if not patient:
        flash("Paziente non trovato.", "danger")
        return redirect(url_for('doctor.dashboard'))

    is_smoker = bool(request.form.get('is_smoker'))
    has_alcohol_issues = bool(request.form.get('has_alcohol_issues'))
    has_hypertension = bool(request.form.get('has_hypertension'))
    has_obesity = bool(request.form.get('has_obesity'))

    record_service.update_patient_record(
        doctor_id=doctor_id,
        patient_id=patient_id,
        is_smoker=is_smoker,
        has_alcohol_issues=has_alcohol_issues,
        has_hypertension=has_hypertension,
        has_obesity=has_obesity
    )

    flash("Fascicolo clinico aggiornato e operazione tracciata nell'Audit Log.", "success")
    return redirect(url_for('doctor.patient_dossier', patient_id=patient_id))

@doctor_bp.route('/doctor/patient/<int:patient_id>/messages', methods=['GET', 'POST'])
@doctor_required
def messages(patient_id):
    """FR11 / UC9: Communication thread with patient."""
    doctor_id = session['user_id']
    patient = patient_service.get_patient(patient_id)
    if not patient:
        flash("Paziente non trovato.", "danger")
        return redirect(url_for('doctor.dashboard'))

    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        try:
            message_service.send_message(
                sender_id=doctor_id,
                receiver_id=patient_id,
                content=content
            )
            flash("Messaggio inviato al paziente.", "success")
            return redirect(url_for('doctor.messages', patient_id=patient_id))
        except ValueError as e:
            flash(str(e), "danger")

    conversation = message_service.get_conversation(doctor_id, patient_id)
    return render_template(
        'doctor/messages.html',
        patient=patient,
        conversation=conversation
    )

@doctor_bp.route('/doctor/audit-logs')
@doctor_required
def audit_logs():
    """FR12 / NFR2: View immutable doctor audit trail."""
    doctor_id = session['user_id']
    logs = audit_service.get_doctor_logs(doctor_id, limit=100)
    return render_template('doctor/audit_logs.html', logs=logs)
