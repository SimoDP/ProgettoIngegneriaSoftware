from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.controllers.auth_decorators import admin_required
from app.services.AuthService import AuthService
from app.services.PatientService import PatientService
from app.services.AuditService import AuditService
from app.daos.UserDAO import UserDAO
from app.models.User import User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

auth_service = AuthService()
patient_service = PatientService()
audit_service = AuditService()
user_dao = UserDAO()

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard overview."""
    doctors = user_dao.get_all_by_role(User.ROLE_DOCTOR)
    patients = patient_service.get_all_patients()
    recent_logs = audit_service.get_recent_logs(limit=20)

    return render_template(
        'admin/dashboard.html',
        doctors=doctors,
        patients=patients,
        logs=recent_logs
    )

@admin_bp.route('/create-doctor', methods=['GET', 'POST'])
@admin_required
def create_doctor():
    """FR2 / UC5: Admin creates a new Doctor user account."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()

        try:
            auth_service.register_user(
                email=email,
                raw_password=password,
                first_name=first_name,
                last_name=last_name,
                role=User.ROLE_DOCTOR
            )
            flash(f"Profilo Medico creato con successo per Dr. {first_name} {last_name}.", "success")
            return redirect(url_for('admin.dashboard'))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template('admin/create_doctor.html')

@admin_bp.route('/create-patient', methods=['GET', 'POST'])
@admin_required
def create_patient():
    """FR2 / UC5 / TC03: Admin registers a Patient and assigns them to a specific Doctor."""
    doctors = user_dao.get_all_by_role(User.ROLE_DOCTOR)

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        doctor_id = request.form.get('doctor_id', '').strip()
        date_of_birth = request.form.get('date_of_birth', '').strip()
        gender = request.form.get('gender', '').strip()

        try:
            if not doctor_id:
                raise ValueError("È obbligatorio selezionare un medico di riferimento per il paziente.")

            patient_service.register_patient(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                doctor_id=int(doctor_id),
                date_of_birth=date_of_birth or None,
                gender=gender or None
            )
            flash(f"Paziente {first_name} {last_name} registrato e associato al medico con successo!", "success")
            return redirect(url_for('admin.dashboard'))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template('admin/create_patient.html', doctors=doctors)

@admin_bp.route('/audit-logs')
@admin_required
def audit_logs():
    """FR12 / NFR2: Complete audit log inspection."""
    logs = audit_service.get_recent_logs(limit=200)
    return render_template('admin/audit_logs.html', logs=logs)
