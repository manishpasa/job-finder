
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .models import JobSeekerProfile, JobProviderProfile


User = get_user_model()


class AccountsAPITests(APITestCase):

    def setUp(self):
        self.seeker = User.objects.create_user(
            username="test_seeker",
            email="seeker@test.com",
            password="testpassword123",
            role=User.Role.JOB_SEEKER,
        )

        self.provider = User.objects.create_user(
            username="test_provider",
            email="provider@test.com",
            password="testpassword123",
            role=User.Role.JOB_PROVIDER,
        )

    # REGISTRATION

    def test_user_can_register_as_job_seeker(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "new_seeker",
                "email": "newseeker@test.com",
                "password": "newpassword123",
                "role": "JOB_SEEKER",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertTrue(
            User.objects.filter(username="new_seeker").exists()
        )

    def test_user_can_register_as_job_provider(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "new_provider",
                "email": "newprovider@test.com",
                "password": "newpassword123",
                "role": "JOB_PROVIDER",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_registration_rejects_admin_role(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "new_admin",
                "email": "admin@test.com",
                "password": "newpassword123",
                "role": "ADMIN",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_registration_rejects_short_password(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "short_password",
                "email": "short@test.com",
                "password": "123",
                "role": "JOB_SEEKER",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # LOGIN

    def test_user_can_login_and_receive_token(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "test_seeker",
                "password": "testpassword123",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("token", response.data)
        self.assertEqual(
            response.data["role"],
            "JOB_SEEKER",
        )

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "test_seeker",
                "password": "wrongpassword",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # CURRENT USER

    def test_authenticated_user_can_access_current_user(self):
        self.client.force_authenticate(user=self.seeker)

        response = self.client.get(reverse("current-user"))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["username"],
            "test_seeker",
        )

    def test_unauthenticated_user_cannot_access_current_user(self):
        response = self.client.get(reverse("current-user"))

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # JOB SEEKER PROFILE

    def test_job_seeker_can_access_own_profile(self):
        self.client.force_authenticate(user=self.seeker)

        response = self.client.get(reverse("seeker-profile"))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertTrue(
            JobSeekerProfile.objects.filter(user=self.seeker).exists()
        )

    def test_job_seeker_can_update_own_profile(self):
        self.client.force_authenticate(user=self.seeker)

        response = self.client.patch(
            reverse("seeker-profile"),
            {"headline": "Python Developer"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        profile = JobSeekerProfile.objects.get(user=self.seeker)
        self.assertEqual(profile.headline, "Python Developer")

    def test_provider_cannot_access_seeker_profile(self):
        self.client.force_authenticate(user=self.provider)

        response = self.client.get(reverse("seeker-profile"))

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # JOB PROVIDER PROFILE

    def test_provider_can_access_own_profile(self):
        self.client.force_authenticate(user=self.provider)

        response = self.client.get(reverse("provider-profile"))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertTrue(
            JobProviderProfile.objects.filter(user=self.provider).exists()
        )

    def test_provider_can_update_own_profile(self):
        self.client.force_authenticate(user=self.provider)

        response = self.client.patch(
            reverse("provider-profile"),
            {"company_name": "Test Technologies"},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        profile = JobProviderProfile.objects.get(user=self.provider)
        self.assertEqual(
            profile.company_name,
            "Test Technologies",
        )

    def test_seeker_cannot_access_provider_profile(self):
        self.client.force_authenticate(user=self.seeker)

        response = self.client.get(reverse("provider-profile"))

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
