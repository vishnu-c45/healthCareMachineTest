from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache

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

import time

class PatientRetrieveView(APIView):

    def get(self, request, patient_id):
        start_time = time.time()

        cache_key = f"{patient_id}"

        cache_data = cache.get(cache_key)

        if cache_data:
            print("*** data in")
            patientInfo = cache_data
            duration = (time.time() - start_time) * 1000
            print(f"*** Cache HIT: {duration:.2f}ms")

        else:
            try:
                patient = PatientRecord.objects.get(patient_id=patient_id)

            except PatientRecord.DoesNotExist:
                return Response(
                    {"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND
                )

            # user = request.user if request.user.is_authenticated else None
            # PatientsAccessLog.objects.create(
            #     patient=patient,
            #     accessed_by=user,
            #     ip_address=request.META.get("REMOTE_ADDR"),
            # )
            patientInfo = {
                "patient_id": patient.patient_id,
                "name": patient.full_name,
                "gender": patient.gender,
                "birth_date": patient.birth_date,
                "ssn": patient.masked_ssn(),
            }
            cache.set(cache_key, patientInfo, timeout=900)
            
            duration = (time.time() - start_time) * 1000
            print(f"*** DATABASE HIT: {duration:.2f}ms")

        return Response(patientInfo)
