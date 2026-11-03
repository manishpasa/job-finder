
from rest_framework import serializers
from .models import (
    CVProfile,
    Education,
    WorkExperience,
    Skill,
    Certification,
)


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


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = [
            "id",
            "institution",
            "degree",
            "field_of_study",
            "start_year",
            "end_year",
            "grade",
            "description",
        ]
        read_only_fields = ["id"]

    def validate(self, data):
        start_year = data.get(
            "start_year",
            self.instance.start_year if self.instance else None
        )
        end_year = data.get(
            "end_year",
            self.instance.end_year if self.instance else None
        )

        if end_year and start_year and end_year < start_year:
            raise serializers.ValidationError(
                "End year cannot be earlier than start year."
            )

        return data


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = [
            "id",
            "job_title",
            "company",
            "location",
            "start_date",
            "end_date",
            "is_current",
            "description",
        ]
        read_only_fields = ["id"]

    def validate(self, data):
        start_date = data.get(
            "start_date",
            self.instance.start_date if self.instance else None
        )
        end_date = data.get(
            "end_date",
            self.instance.end_date if self.instance else None
        )
        is_current = data.get(
            "is_current",
            self.instance.is_current if self.instance else False
        )

        if end_date and start_date and end_date < start_date:
            raise serializers.ValidationError(
                "End date cannot be earlier than start date."
            )

        if is_current and end_date:
            raise serializers.ValidationError(
                "Current employment cannot have an end date."
            )

        return data


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name", "proficiency"]
        read_only_fields = ["id"]


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = [
            "id",
            "name",
            "issuing_organization",
            "issue_date",
            "expiry_date",
            "credential_id",
            "credential_url",
        ]
        read_only_fields = ["id"]

    def validate(self, data):
        issue_date = data.get(
            "issue_date",
            self.instance.issue_date if self.instance else None
        )
        expiry_date = data.get(
            "expiry_date",
            self.instance.expiry_date if self.instance else None
        )

        if issue_date and expiry_date and expiry_date < issue_date:
            raise serializers.ValidationError(
                "Expiry date cannot be earlier than issue date."
            )

        return data
