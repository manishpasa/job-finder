from rest_framework import serializers
from .models import CVProfile
from .models import CVProfile, Education

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