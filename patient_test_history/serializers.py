# patient_test_history/serializers.py

from rest_framework import serializers
from .models import PatientTestHistory
from lab_tests.serializers import LabTestSerializer
from patients.serializers import PatientSerializer
from test_results.serializers import TestResultSerializer


class PatientTestHistorySerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    test = LabTestSerializer(read_only=True)
    result = TestResultSerializer(read_only=True, allow_null=True)
    is_out_of_range = serializers.ReadOnlyField()

    class Meta:
        model = PatientTestHistory
        fields = [
            'history_id',
            'patient',
            'test',
            'result',
            'value',
            'unit',
            'status',
            'is_out_of_range',
            'recorded_at',
            'notes',
        ]
        read_only_fields = ['history_id', 'recorded_at', 'is_out_of_range']