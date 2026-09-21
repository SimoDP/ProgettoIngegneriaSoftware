from app.controllers.AuthController import auth_bp
from app.controllers.PatientController import patient_bp
from app.controllers.DoctorController import doctor_bp
from app.controllers.AdminController import admin_bp

__all__ = [
    'auth_bp',
    'patient_bp',
    'doctor_bp',
    'admin_bp',
]
