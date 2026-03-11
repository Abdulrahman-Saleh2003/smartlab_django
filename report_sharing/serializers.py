# report_sharing/serializers.py

from rest_framework import serializers
from .models import ReportSharing
from reports.serializers import LabReportsSerializer
from doctors.serializers import DoctorSerializer


class ReportSharingSerializer(serializers.ModelSerializer):
    report = LabReportsSerializer(read_only=True)
    shared_with = DoctorSerializer(read_only=True)

    class Meta:
        model = ReportSharing
        fields = [
            'share_id',
            'report',
            'shared_with',
            'permission',
            'shared_at',
            'expires_at',
            'created_by',
        ]
        read_only_fields = ['share_id', 'shared_at', 'created_by']

    def create(self, validated_data):
        request = self.context['request']
        validated_data['created_by'] = request.user
        return super().create(validated_data)