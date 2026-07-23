# test_comparisons/serializers.py

from rest_framework import serializers
from .models import TestComparison
from patients.serializers import PatientSerializer
from lab_tests.serializers import LabTestSerializer
from test_results.serializers import TestResultSerializer


class TestComparisonSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    test = LabTestSerializer(read_only=True)
    old_result = TestResultSerializer(read_only=True, allow_null=True)
    new_result = TestResultSerializer(read_only=True, allow_null=True)

    class Meta:
        model = TestComparison
        fields = [
            'comparison_id',
            'patient',
            'test',
            'old_result',
            'new_result',
            'trend',
            'change_percentage',
            'created_at',
        ]
        read_only_fields = ['comparison_id', 'created_at', 'change_percentage']