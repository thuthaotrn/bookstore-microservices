from rest_framework import serializers
from .models import AI_Log

class AILogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AI_Log
        fields = '__all__'