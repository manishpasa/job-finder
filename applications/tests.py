
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from jobs.models import Job
from .models import Application


User = get_user_model()


class ApplicationAPITests(APITestCase):

    def setUp(self):
        self.seeker = User.objects.create_user(
            username="applicant",
            email="applicant@test.com",
            password="testpassword123",
            role=User.Role.JOB_SEEKER,
        )

        self.provider = User.objects.create_user(
            username="provider",
            email="provider@test.com",
            password="testpassword123",
            role=User.Role.JOB_PROVIDER,
        )

        self.other_provider = User.objects.create_user(
            username="other_provider",
            email="other@test.com",
            password="testpassword123",
            role=User.Role.JOB_PROVIDER,
        )

        self.job = self.create_job(
            self.provider,
            "Python Developer",
        )

        self.other_job = self.create_job(
            self.other_provider,
            "Frontend Developer",
        )

        self.apply_url = reverse("apply")
        self.my_applications_url = reverse("my-applications")

    def create_job(self, provider, title):
        return Job.objects.create(
            provider=provider,
            title=title,
            company_name="Test Company",
            description="A test job description.",
            required_skills="Python, Django",
            category="IT",
            location="Kathmandu",
            is_active=True,
        )

    def create_application(self, job, seeker=None):
        return Application.objects.create(
            job=job,
            seeker=seeker or self.seeker,
            cover_letter="I am interested in this position.",
        )

    def test_job_seeker_can_apply_for_active_job(self):
        self.client.force_authenticate(user=self.seeker)

        response = self.client.post(
            self.apply_url,
            {
                "job": self.job.id,
                "cover_letter": "I am interested in this position.",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertTrue(
            Application.objects.filter(
                job=self.job,
                seeker=self.seeker,
            ).exists()
        )

    def test_duplicate_application_is_rejected(self):
        self.create_application(self.job)
        self.client.force_authenticate(user=self.seeker)

        response = self.client.post(
            self.apply_url,
            {"job": self.job.id},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_application_for_inactive_job_is_rejected(self):
        self.job.is_active = False
        self.job.save()

        self.client.force_authenticate(user=self.seeker)

        response = self.client.post(
            self.apply_url,
            {"job": self.job.id},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            Application.objects.filter(
                job=self.job,
                seeker=self.seeker,
            ).exists()
        )

    def test_seeker_can_only_see_own_applications(self):
        self.create_application(self.job, self.seeker)

        another_seeker = User.objects.create_user(
            username="another_seeker",
            password="testpassword123",
            role=User.Role.JOB_SEEKER,
        )

        self.create_application(self.other_job, another_seeker)

        self.client.force_authenticate(user=self.seeker)

        response = self.client.get(self.my_applications_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["seeker"],
            self.seeker.id,
        )

    def test_provider_can_only_see_own_job_applicants(self):
        self.create_application(self.job)
        self.create_application(self.other_job)

        self.client.force_authenticate(user=self.provider)

        response = self.client.get(
            reverse("job-applicants", kwargs={"job_id": self.job.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["job"],
            self.job.id,
        )

    def test_provider_can_update_application_status(self):
        application = self.create_application(self.job)

        self.client.force_authenticate(user=self.provider)

        response = self.client.patch(
            reverse(
                "update-application-status",
                kwargs={"pk": application.id},
            ),
            {"status": Application.Status.SHORTLISTED},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        application.refresh_from_db()

        self.assertEqual(
            application.status,
            Application.Status.SHORTLISTED,
        )

    def test_provider_cannot_update_another_providers_application(self):
        application = self.create_application(self.other_job)

        self.client.force_authenticate(user=self.provider)

        response = self.client.patch(
            reverse(
                "update-application-status",
                kwargs={"pk": application.id},
            ),
            {"status": Application.Status.HIRED},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        application.refresh_from_db()

        self.assertEqual(
            application.status,
            Application.Status.PENDING,
        )

    def test_job_seeker_cannot_view_provider_applicants(self):
        self.client.force_authenticate(user=self.seeker)

        response = self.client.get(
            reverse("job-applicants", kwargs={"job_id": self.job.id})
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
