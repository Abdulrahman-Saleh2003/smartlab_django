# interpretations/serializers.py

from rest_framework import serializers
from .models import Interpretation
from ai_analysis.serializers import AIAnalysisSerializer


class InterpretationSerializer(serializers.ModelSerializer):
    result = AIAnalysisSerializer(read_only=True)

    class Meta:
        model = Interpretation
        fields = [
            'interpretation_id',
            'result',
            'interpretation_text',
            'severity',
            'created_at',
            'updated_at',
            'created_by',
        ]
        read_only_fields = ['interpretation_id', 'created_at', 'updated_at', 'created_by']