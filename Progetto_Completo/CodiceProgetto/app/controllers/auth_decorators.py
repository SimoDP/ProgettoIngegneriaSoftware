from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    """Decorator to ensure user is authenticated."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Devi effettuare l'accesso per visualizzare questa pagina.", "warning")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """Decorator to ensure user has one of the specified roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Devi effettuare l'accesso per visualizzare questa pagina.", "warning")
                return redirect(url_for('auth.login'))
            user_role = session.get('role')
            if user_role not in allowed_roles:
                flash("Accesso negato: non disponi delle autorizzazioni necessarie.", "danger")
                # Redirect to appropriate dashboard based on actual role
                if user_role == 0:
                    return redirect(url_for('patient.dashboard'))
                elif user_role == 1:
                    return redirect(url_for('doctor.dashboard'))
                elif user_role == 2:
                    return redirect(url_for('admin.dashboard'))
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def patient_required(f):
    return role_required(0)(f)

def doctor_required(f):
    return role_required(1)(f)

def admin_required(f):
    return role_required(2)(f)
