
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import JobSeekerProfile, JobProviderProfile
User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role"]
        read_only_fields = ["id"]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "This email is already registered."
            )
        return value

    def validate_role(self, value):
        if value not in [
            User.Role.JOB_SEEKER,
            User.Role.JOB_PROVIDER,
        ]:
            raise serializers.ValidationError(
                "You can register only as a Job Seeker or Job Provider."
            )
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)



class JobSeekerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSeekerProfile
        fields = [
            "full_name",
            "phone",
            "address",
            "headline",
            "career_objective",
            "total_experience_years",
        ]


class JobProviderProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobProviderProfile
        fields = [
            "company_name",
            "company_description",
            "website",
            "address",
            "phone",
        ]
