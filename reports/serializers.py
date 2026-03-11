# reports/serializers.py

from rest_framework import serializers
from .models import LabReports, ReportImages
from accounts.serializers import UserSerializer  # لو عايز تعرض بيانات المريض/الدكتور


class ReportImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportImages
        fields = [
            'image_id',
            'report',               # UUID التقرير
            'image_path',
            'ocr_confidence',
            'uploaded_at',
        ]
        read_only_fields = ['image_id', 'uploaded_at']


class LabReportsSerializer(serializers.ModelSerializer):
    # إذا بدك تعرض صور التقرير مع التقرير نفسه (nested)
    images = ReportImagesSerializer(many=True, read_only=True)

    # عرض بيانات المريض بشكل مختصر (اختياري)
    patient = UserSerializer(read_only=True)

    class Meta:
        model = LabReports
        fields = [
            'report_id',
            'patient',
            'lab_name',
            'report_date',
            'upload_date',
            'file_path',
            'status',
            'created_at',
            'updated_at',
            'images',          # الصور التابعة
        ]
        read_only_fields = ['report_id', 'upload_date', 'created_at', 'updated_at']