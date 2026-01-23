from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from .models import PatientRecord, PatientsAccessLog
from .serializers import PatientSerializer


FERNET_KEYS = ["your-very-secure-random-key-here"]


def welcome(request):
    return {"welcome the health care system"}


class PatientDataInsert(APIView):

    def get(self, request):
        return Response({"message": "Use POST method."}, status=200)

    def post(self, request):
        serializer = PatientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        name_data = data["name"][0]
        full_name = f"{name_data['given'][0]} {name_data['family']}"

        ssn = None
        for ident in request.data.get("identifier", []):
            if ident.get("system") == "http://hl7.org/fhir/sid/us-ssn":
                ssn = ident.get("value")

        patient = PatientRecord(
            patient_id=data["id"],
            full_name=full_name,
            gender=data["gender"],
            birth_date=data["birthDate"],
            raw_payload=request.data,
        )

        if ssn:
            patient.set_ssn(ssn)

        patient.save()

        return Response(
            {"message": "Patient ingested successfully"}, status=status.HTTP_201_CREATED
        )


class PatientRetrieveView(APIView):

    def get(self, request, patient_id):
        try:
            patient = PatientRecord.objects.get(patient_id=patient_id)
        except PatientRecord.DoesNotExist:
            return Response(
                {"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND
            )

        user = request.user if request.user.is_authenticated else None
        PatientsAccessLog.objects.create(
            patient=patient,
            accessed_by=user,
            ip_address=request.META.get("REMOTE_ADDR"),
        )

        return Response(
            {
                "patient_id": patient.patient_id,
                "name": patient.full_name,
                "gender": patient.gender,
                "birth_date": patient.birth_date,
                "ssn": patient.masked_ssn(),
            }
        )
