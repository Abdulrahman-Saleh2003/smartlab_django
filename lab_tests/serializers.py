# lab_tests/serializers.py

from rest_framework import serializers
from .models import LabTest


class LabTestSerializer(serializers.ModelSerializer):
    normal_range_display = serializers.ReadOnlyField()

    class Meta:
        model = LabTest
        fields = [
            'test_id',
            'test_name',
            'loinc_code',
            'category',
            'normal_range_min',
            'normal_range_max',
            'unit',
            'description',
            'normal_range_display',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['test_id', 'created_at', 'updated_at', 'normal_range_display']