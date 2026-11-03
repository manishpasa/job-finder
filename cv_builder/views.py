
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import (
    CVProfile,
    Education,
    WorkExperience,
    Skill,
    Certification,
)

from .serializers import (
    CVProfileSerializer,
    EducationSerializer,
    WorkExperienceSerializer,
    SkillSerializer,
    CertificationSerializer,
)


class CVProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = CVProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, created = CVProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                "full_name": self.request.user.username,
                "email": self.request.user.email,
                "phone": "",
            }
        )
        return profile


class EducationListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = EducationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Education.objects.filter(
            cv_profile__user=self.request.user
        )

    def perform_create(self, serializer):
        profile, created = CVProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                "full_name": self.request.user.username,
                "email": self.request.user.email,
                "phone": "",
            }
        )
        serializer.save(cv_profile=profile)


class EducationDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EducationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Education.objects.filter(
            cv_profile__user=self.request.user
        )


# WORK EXPERIENCE

class WorkExperienceListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = WorkExperienceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WorkExperience.objects.filter(
            cv_profile__user=self.request.user
        )

    def perform_create(self, serializer):
        profile, created = CVProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                "full_name": self.request.user.username,
                "email": self.request.user.email,
                "phone": "",
            }
        )
        serializer.save(cv_profile=profile)


class WorkExperienceDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkExperienceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WorkExperience.objects.filter(
            cv_profile__user=self.request.user
        )


# SKILLS

class SkillListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Skill.objects.filter(
            cv_profile__user=self.request.user
        )

    def perform_create(self, serializer):
        profile, created = CVProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                "full_name": self.request.user.username,
                "email": self.request.user.email,
                "phone": "",
            }
        )
        serializer.save(cv_profile=profile)


class SkillDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Skill.objects.filter(
            cv_profile__user=self.request.user
        )


# CERTIFICATIONS

class CertificationListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CertificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Certification.objects.filter(
            cv_profile__user=self.request.user
        )

    def perform_create(self, serializer):
        profile, created = CVProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                "full_name": self.request.user.username,
                "email": self.request.user.email,
                "phone": "",
            }
        )
        serializer.save(cv_profile=profile)


class CertificationDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CertificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Certification.objects.filter(
            cv_profile__user=self.request.user
        )
