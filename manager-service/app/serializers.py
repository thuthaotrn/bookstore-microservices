from rest_framework import serializers
from .models import RevenueReport

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevenueReport
        fields = '__all__'