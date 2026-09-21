from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services.AuthService import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='')
auth_service = AuthService()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login (UC4 / FR1)."""
    # If already logged in, redirect directly to dashboard
    if 'user_id' in session:
        role = session.get('role')
        if role == 0:
            return redirect(url_for('patient.dashboard'))
        elif role == 1:
            return redirect(url_for('doctor.dashboard'))
        elif role == 2:
            return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = auth_service.authenticate(email, password)
        if user:
            # Initialize Flask session (UC4 Main Flow)
            session['user_id'] = user.id
            session['email'] = user.email
            session['full_name'] = user.full_name
            session['role'] = user.role

            flash(f"Benvenuto/a, {user.full_name}!", "success")

            if user.is_patient():
                return redirect(url_for('patient.dashboard'))
            elif user.is_doctor():
                return redirect(url_for('doctor.dashboard'))
            elif user.is_admin():
                return redirect(url_for('admin.dashboard'))
        else:
            # Generic message to prevent user enumeration (TC02)
            flash("Credenziali non valide. Riprova con email e password corrette.", "danger")

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """Logs the user out and clears session."""
    session.clear()
    flash("Disconnessione avvenuta con successo.", "info")
    return redirect(url_for('auth.login'))
