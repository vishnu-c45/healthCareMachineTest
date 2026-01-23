from django.db import models

from django.contrib.auth.models import User

from django.db import models
from .utils import encrypt_value, decrypt_value
from cryptography.fernet import InvalidToken

class PatientRecord(models.Model):
    patient_id = models.CharField(max_length=100, unique=True)
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=20)
    birth_date = models.DateField()
    ssn_encrypted = models.TextField(null=True, blank=True)
    passport_encrypted = models.TextField(null=True, blank=True)
    raw_payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def set_ssn(self, ssn):
        self.ssn_encrypted = encrypt_value(ssn)

    def get_ssn(self):
        return decrypt_value(self.ssn_encrypted)

    def masked_ssn(self):
        try:
            ssn = self.get_ssn()
        except InvalidToken:
            return "INVALID-ENCRYPTED-DATA"

        return f"***-**-{ssn[-4:]}"


class PatientsAccessLog(models.Model):
    patient = models.ForeignKey(PatientRecord, on_delete=models.CASCADE)
    accessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    ip_address = models.GenericIPAddressField()
    accessed_at = models.DateTimeField(auto_now_add=True)
