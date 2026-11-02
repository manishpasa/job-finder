from rest_framework import serializers
from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):

    job_title = serializers.CharField(
        source="job.title",
        read_only=True
    )

    company_name = serializers.CharField(
        source="job.company_name",
        read_only=True
    )

    seeker_username = serializers.CharField(
        source="seeker.username",
        read_only=True
    )

    class Meta:
        model = Application
        fields = [
            "id",
            "job",
            "job_title",
            "company_name",
            "seeker",
            "seeker_username",
            "cover_letter",
            "status",
            "applied_at",
            "updated_at",
        ]

        read_only_fields = [
    "id",
    "seeker",
    "status",
    "applied_at",
    "updated_at",
]
class ApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["status"]