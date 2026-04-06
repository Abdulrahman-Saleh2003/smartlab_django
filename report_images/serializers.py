# report_images/serializers.py

from rest_framework import serializers
from .models import ReportImage
from lab_reports.serializers import LabReportSerializer


class ReportImageSerializer(serializers.ModelSerializer):
    report = LabReportSerializer(read_only=True)

    class Meta:
        model = ReportImage
        fields = [
            'image_id',
            'report',
            'image_path',
            'ocr_confidence',
            'ocr_text',
            'ocr_success',
            'uploaded_by',
            'uploaded_at',
        ]
        read_only_fields = ['image_id', 'uploaded_at', 'ocr_success', 'uploaded_by']