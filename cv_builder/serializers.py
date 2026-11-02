from rest_framework import serializers
from .models import CVProfile


class CVProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVProfile
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "address",
            "professional_title",
            "career_objective",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]