
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Job
from accounts.models import JobProviderProfile


User = get_user_model()


class JobAPITests(APITestCase):

    def setUp(self):
        self.provider = User.objects.create_user(
            username="provider1",
            email="provider1@test.com",
            password="testpassword123",
            role=User.Role.JOB_PROVIDER,
        )

        self.other_provider = User.objects.create_user(
            username="provider2",
            email="provider2@test.com",
            password="testpassword123",
            role=User.Role.JOB_PROVIDER,
        )

        self.seeker = User.objects.create_user(
            username="seeker1",
            email="seeker1@test.com",
            password="testpassword123",
            role=User.Role.JOB_SEEKER,
        )

        JobProviderProfile.objects.create(
            user=self.provider,
            company_name="Test Technologies",
        )

        JobProviderProfile.objects.create(
            user=self.other_provider,
            company_name="Other Technologies",
        )

        self.job = Job.objects.create(
            provider=self.provider,
            title="Python Developer",
            company_name="Test Technologies",
            description="Develop backend applications.",
            required_skills="Python, Django, SQL",
            category="Software Development",
            location="Kathmandu",
            employment_type="FULL_TIME",
            vacancies=2,
            min_experience_years=1,
            is_active=True,
        )

        self.other_job = Job.objects.create(
            provider=self.other_provider,
            title="Java Developer",
            company_name="Other Technologies",
            description="Develop Java applications.",
            required_skills="Java, Spring",
            category="Software Development",
            location="Pokhara",
            is_active=True,
        )

        self.list_url = reverse("job-list")

    def create_job_data(self):
        return {
            "title": "Django Developer",
            "description": "Develop Django applications.",
            "required_skills": "Python, Django",
            "category": "Software Development",
            "location": "Kathmandu",
            "employment_type": "FULL_TIME",
            "salary": "50000",
            "vacancies": 2,
            "min_experience_years": 1,
            "is_active": True,
        }

    def test_public_can_view_active_jobs(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data), 2)

    def test_public_cannot_view_inactive_jobs(self):
        inactive_job = Job.objects.create(
            provider=self.provider,
            title="Inactive Developer",
            company_name="Test Technologies",
            description="Inactive job.",
            category="Software",
            location="Kathmandu",
            is_active=False,
        )

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [item["id"] for item in response.data]

        self.assertNotIn(inactive_job.id, returned_ids)

    def test_provider_can_view_own_inactive_jobs(self):
        inactive_job = Job.objects.create(
            provider=self.provider,
            title="My Inactive Job",
            company_name="Test Technologies",
            description="Inactive job.",
            category="Software",
            location="Kathmandu",
            is_active=False,
        )

        self.client.force_authenticate(user=self.provider)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [item["id"] for item in response.data]

        self.assertIn(inactive_job.id, returned_ids)

    def test_job_search_by_title(self):
        response = self.client.get(
            self.list_url,
            {"search": "Python"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Python Developer")

    def test_job_search_by_location(self):
        response = self.client.get(
            self.list_url,
            {"search": "Pokhara"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Java Developer")

    def test_provider_can_create_job(self):
        self.client.force_authenticate(user=self.provider)

        response = self.client.post(
            self.list_url,
            self.create_job_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        created_job = Job.objects.get(title="Django Developer")

        self.assertEqual(created_job.provider, self.provider)
        self.assertEqual(
            created_job.company_name,
            "Test Technologies",
        )

    def test_seeker_cannot_create_job(self):
        self.client.force_authenticate(user=self.seeker)

        response = self.client.post(
            self.list_url,
            self.create_job_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_unauthenticated_user_cannot_create_job(self):
        response = self.client.post(
            self.list_url,
            self.create_job_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_provider_must_complete_company_profile(self):
        incomplete_provider = User.objects.create_user(
            username="incomplete_provider",
            email="incomplete@test.com",
            password="testpassword123",
            role=User.Role.JOB_PROVIDER,
        )

        JobProviderProfile.objects.create(
            user=incomplete_provider,
            company_name="",
        )

        self.client.force_authenticate(user=incomplete_provider)

        response = self.client.post(
            self.list_url,
            self.create_job_data(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            Job.objects.filter(title="Django Developer").exists()
        )

    def test_provider_can_update_own_job(self):
        self.client.force_authenticate(user=self.provider)

        response = self.client.patch(
            reverse("job-detail", kwargs={"pk": self.job.id}),
            {"title": "Senior Python Developer"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.job.refresh_from_db()

        self.assertEqual(
            self.job.title,
            "Senior Python Developer",
        )

    def test_provider_cannot_update_another_providers_job(self):
        self.client.force_authenticate(user=self.provider)

        response = self.client.patch(
            reverse("job-detail", kwargs={"pk": self.other_job.id}),
            {"title": "Unauthorized Update"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_provider_can_delete_own_job(self):
        self.client.force_authenticate(user=self.provider)

        response = self.client.delete(
            reverse("job-detail", kwargs={"pk": self.job.id})
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Job.objects.filter(id=self.job.id).exists()
        )

    def test_provider_cannot_delete_another_providers_job(self):
        self.client.force_authenticate(user=self.provider)

        response = self.client.delete(
            reverse("job-detail", kwargs={"pk": self.other_job.id})
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            Job.objects.filter(id=self.other_job.id).exists()
        )

    def test_admin_can_update_another_providers_job(self):
        admin = User.objects.create_user(
            username="admin1",
            email="admin@test.com",
            password="testpassword123",
            role=User.Role.ADMIN,
        )

        self.client.force_authenticate(user=admin)

        response = self.client.patch(
            reverse("job-detail", kwargs={"pk": self.other_job.id}),
            {"title": "Admin Updated Job"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.other_job.refresh_from_db()

        self.assertEqual(
            self.other_job.title,
            "Admin Updated Job",
        )

    def test_invalid_vacancies_are_rejected(self):
        self.client.force_authenticate(user=self.provider)

        data = self.create_job_data()
        data["vacancies"] = 0

        response = self.client.post(
            self.list_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
