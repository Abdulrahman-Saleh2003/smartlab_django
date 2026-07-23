# lab_reports/serializers.py

from rest_framework import serializers
from .models import LabReport
from patients.serializers import PatientSerializer


from rest_framework import serializers
from patients.models import Patient
from lab_reports.models import LabReport
from patients.serializers import PatientSerializer



class LabReportSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)

    class Meta:
        model = LabReport
        fields = [
            'report_id',
            'patient',
            'report_date',
            'upload_date',
            'file_path',
            'status',
            'created_by',
            'created_at',
            'updated_at',
            'is_recent',
            'report_type',
            'title',
            'description',
            'priority',
            'cost',
            'internal_notes',
            'lab_name',
            'category',
            'body_part',
          
        ]
        read_only_fields = ['report_id', 'upload_date', 'created_at', 'updated_at', 'is_recent', 'created_by']







 





 