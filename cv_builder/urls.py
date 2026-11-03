
from django.urls import path

from .views import (
    CVProfileAPIView,
    EducationListCreateAPIView,
    EducationDetailAPIView,
    WorkExperienceListCreateAPIView,
    WorkExperienceDetailAPIView,
    SkillListCreateAPIView,
    SkillDetailAPIView,
    CertificationListCreateAPIView,
    CertificationDetailAPIView,
)

urlpatterns = [
    # CV Profile
    path("profile/", CVProfileAPIView.as_view(), name="cv-profile"),

    # Education
    path("education/", EducationListCreateAPIView.as_view(), name="education-list-create"),
    path("education/<int:pk>/", EducationDetailAPIView.as_view(), name="education-detail"),

    # Work Experience
    path("experience/", WorkExperienceListCreateAPIView.as_view(), name="experience-list-create"),
    path("experience/<int:pk>/", WorkExperienceDetailAPIView.as_view(), name="experience-detail"),

    # Skills
    path("skills/", SkillListCreateAPIView.as_view(), name="skill-list-create"),
    path("skills/<int:pk>/", SkillDetailAPIView.as_view(), name="skill-detail"),

    # Certifications
    path("certifications/", CertificationListCreateAPIView.as_view(), name="certification-list-create"),
    path("certifications/<int:pk>/", CertificationDetailAPIView.as_view(), name="certification-detail"),
]
