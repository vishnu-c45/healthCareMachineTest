from django.urls import path
from .views import *

urlpatterns = [
    path("home", welcome, name="welcome"),
    path(
        "api/v1/patient-intake/",
        PatientDataInsert.as_view(),
        name="patient-data-insert",
    ),
    path(
        "api/v1/patient/<str:patient_id>/",
        PatientRetrieveView.as_view(),
        name="patient-retrieve",
    ),
]
