
from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    CVProfile,
    Education,
    WorkExperience,
    Skill,
    Certification,
)


User = get_user_model()


class CVBuilderAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="cv_user",
            email="cvuser@test.com",
            password="testpassword123",
            role=User.Role.JOB_SEEKER,
        )

        self.other_user = User.objects.create_user(
            username="other_cv_user",
            email="othercv@test.com",
            password="testpassword123",
            role=User.Role.JOB_SEEKER,
        )

        self.profile = CVProfile.objects.create(
            user=self.user,
            full_name="Test User",
            email="cvuser@test.com",
            phone="9800000000",
        )

        self.client.force_authenticate(user=self.user)

    def test_user_can_retrieve_cv_profile(self):
        response = self.client.get(reverse("cv-profile"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["full_name"], "Test User")

    def test_user_can_update_cv_profile(self):
        response = self.client.patch(
            reverse("cv-profile"),
            {"professional_title": "Python Developer"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.profile.refresh_from_db()

        self.assertEqual(
            self.profile.professional_title,
            "Python Developer",
        )

    def test_user_can_create_education(self):
        response = self.client.post(
            reverse("education-list-create"),
            {
                "institution": "Test University",
                "degree": "Bachelor",
                "field_of_study": "Computer Science",
                "start_year": 2022,
                "end_year": 2026,
                "grade": "A",
                "description": "Computer science degree",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(Education.objects.count(), 1)
        self.assertEqual(
            Education.objects.first().cv_profile,
            self.profile,
        )

    def test_education_rejects_invalid_year_range(self):
        response = self.client.post(
            reverse("education-list-create"),
            {
                "institution": "Test University",
                "degree": "Bachelor",
                "field_of_study": "Computer Science",
                "start_year": 2026,
                "end_year": 2022,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_user_can_create_work_experience(self):
        response = self.client.post(
            reverse("experience-list-create"),
            {
                "job_title": "Python Developer",
                "company": "Test Company",
                "location": "Kathmandu",
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "is_current": False,
                "description": "Backend development",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(WorkExperience.objects.count(), 1)

    def test_work_experience_rejects_invalid_dates(self):
        response = self.client.post(
            reverse("experience-list-create"),
            {
                "job_title": "Python Developer",
                "company": "Test Company",
                "start_date": "2025-01-01",
                "end_date": "2024-01-01",
                "is_current": False,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_current_work_cannot_have_end_date(self):
        response = self.client.post(
            reverse("experience-list-create"),
            {
                "job_title": "Python Developer",
                "company": "Test Company",
                "start_date": "2025-01-01",
                "end_date": "2026-01-01",
                "is_current": True,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_user_can_create_skill(self):
        response = self.client.post(
            reverse("skill-list-create"),
            {
                "name": "Python",
                "proficiency": "Intermediate",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(Skill.objects.count(), 1)

    def test_user_can_create_certification(self):
        response = self.client.post(
            reverse("certification-list-create"),
            {
                "name": "Python Certification",
                "issuing_organization": "Test Organization",
                "issue_date": "2025-01-01",
                "expiry_date": "2027-01-01",
                "credential_id": "CERT-001",
                "credential_url": "https://example.com/certificate",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(Certification.objects.count(), 1)

    def test_certification_rejects_invalid_expiry_date(self):
        response = self.client.post(
            reverse("certification-list-create"),
            {
                "name": "Python Certification",
                "issuing_organization": "Test Organization",
                "issue_date": "2026-01-01",
                "expiry_date": "2025-01-01",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_user_cannot_access_another_users_skill(self):
        other_profile = CVProfile.objects.create(
            user=self.other_user,
            full_name="Other User",
            email="othercv@test.com",
            phone="9800000001",
        )

        other_skill = Skill.objects.create(
            cv_profile=other_profile,
            name="Java",
        )

        response = self.client.get(
            reverse(
                "skill-detail",
                kwargs={"pk": other_skill.id},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_user_cannot_access_another_users_education(self):
        other_profile = CVProfile.objects.create(
            user=self.other_user,
            full_name="Other User",
            email="othercv@test.com",
            phone="9800000001",
        )

        other_education = Education.objects.create(
            cv_profile=other_profile,
            institution="Other University",
            degree="Bachelor",
            field_of_study="IT",
            start_year=2022,
            end_year=2026,
        )

        response = self.client.get(
            reverse(
                "education-detail",
                kwargs={"pk": other_education.id},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
