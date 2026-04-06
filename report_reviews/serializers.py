# doctor_notes/serializers.py

from rest_framework import serializers
from .models import report_review
from doctors.serializers import DoctorSerializer
from patients.serializers import PatientSerializer
from lab_reports.serializers import LabReportSerializer


class ReportReviewSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)
    patient = PatientSerializer(read_only=True)
    report = LabReportSerializer(read_only=True, allow_null=True)


    
    class Meta:
        model = report_review
        fields = [
            'review_id',
            'doctor',
            'patient',
            'report',
            'clinical_finding',
            'comparison_with_previous',
            'recommendations',
            'prescribed_medication',
            'require_urgent_action',
            'result_interpretation',
            'doctor_notes',
        ]
        read_only_fields = ['review_id', 'created_at', 'updated_at', 'doctor']

    # def create(self, validated_data):
        
    #     # The current doctor is the one writing the note, so we set it automatically
    #     request = self.context['request']
    #     doctor = request.user.doctor_profile  
    #     validated_data['doctor'] = doctor
    #     return super().create(validated_data)





    def validate_note_text(self, value):
        if not value.strip():
            raise serializers.ValidationError("نص الملاحظة لا يمكن أن يكون فارغًا")
        return value.strip()
    


    # def validate(self, data):
    #     # Additional validation: Ensure the report belongs to the specified patient
    #     if data['lab_reports'].patient != data['patient']:
    #         raise serializers.ValidationError(
    #             {"report": "Security Error: This lab report does not belong to the selected patient."}
    #         )
    #     return data

 

     