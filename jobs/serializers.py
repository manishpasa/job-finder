
from rest_framework import serializers
from .models import Job


class JobSerializer(serializers.ModelSerializer):

    provider_username = serializers.CharField(
        source="provider.username",
        read_only=True
    )

    class Meta:
        model = Job
        fields = [
            "id",
            "provider",
            "provider_username",
            "title",
            "company_name",
            "description",
            "required_skills",
            "category",
            "location",
            "employment_type",
            "salary",
            "deadline",
            "vacancies",
            "min_experience_years",
            "is_active",
            "created_at",
        ]

        read_only_fields = [
    "id",
    "provider",
    "provider_username",
    "company_name",
    "created_at",
]

    def validate_vacancies(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "There must be at least one vacancy."
            )
        return value
