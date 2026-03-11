# test_results/serializers.py

from rest_framework import serializers
from .models import TestResult
from lab_tests.serializers import LabTestSerializer
from reports.serializers import LabReportsSerializer


class TestResultSerializer(serializers.ModelSerializer):
    test = LabTestSerializer(read_only=True)
    report = LabReportsSerializer(read_only=True)
    is_out_of_range = serializers.ReadOnlyField()

    class Meta:
        model = TestResult
        fields = [
            'result_id',
            'report',
            'test',
            'value',
            'unit',
            'status',
            'is_out_of_range',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['result_id', 'created_at', 'updated_at', 'is_out_of_range']