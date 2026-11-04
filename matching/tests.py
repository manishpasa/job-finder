
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import JobSeekerProfile
from cv_builder.models import CVProfile, Skill
from jobs.models import Job


User = get_user_model()


class JobRecommendationsAPITests(APITestCase):

    def setUp(self):
        # Create a job seeker.
        self.seeker = User.objects.create_user(
            username="test_seeker",
            email="seeker@test.com",
            password="testpassword123",
            role=User.Role.JOB_SEEKER,
        )

        # Create the seeker's experience profile.
        JobSeekerProfile.objects.create(
            user=self.seeker,
            total_experience_years=2.5,
        )

        # Create the seeker's CV.
        self.cv = CVProfile.objects.create(
            user=self.seeker,
            full_name="Test Seeker",
            email="seeker@test.com",
            phone="9800000000",
            professional_title="Python Developer",
            career_objective="Looking for a Python development role.",
        )

        # Add skills to the CV.
        Skill.objects.create(
            cv_profile=self.cv,
            name="Python",
        )
        Skill.objects.create(
            cv_profile=self.cv,
            name="Django",
        )

        # Create a job provider.
        self.provider = User.objects.create_user(
            username="test_provider",
            email="provider@test.com",
            password="testpassword123",
            role=User.Role.JOB_PROVIDER,
        )

        self.url = reverse("job-recommendations")

        self.client.force_authenticate(user=self.seeker)

    def create_job(
        self,
        title,
        required_skills,
        min_experience_years=0,
        is_active=True,
        description="A software development position.",
    ):
        return Job.objects.create(
            provider=self.provider,
            title=title,
            company_name="Test Company",
            description=description,
            required_skills=required_skills,
            category="IT",
            location="Kathmandu",
            min_experience_years=min_experience_years,
            is_active=is_active,
        )

    def test_recommendation_returns_all_matching_scores(self):
        self.create_job(
            title="Python Developer",
            required_skills="Python, Django, REST API",
            min_experience_years=5,
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        job = response.data["results"][0]

        # Two of three required skills match.
        self.assertEqual(job["skill_match_percentage"], 66.67)

        # Candidate has 2.5 years; job requires 5 years.
        self.assertEqual(job["candidate_experience_years"], 2.5)
        self.assertEqual(job["required_experience_years"], 5)
        self.assertEqual(job["experience_match_percentage"], 50.0)

        # TF-IDF should produce a valid percentage.
        self.assertGreaterEqual(
            job["tfidf_similarity_percentage"], 0
        )
        self.assertLessEqual(
            job["tfidf_similarity_percentage"], 100
        )

        # Verify the weighted 50/30/20 calculation.
        expected_score = round(
            job["skill_match_score"]
            + job["experience_match_score"]
            + job["tfidf_similarity_score"],
            2,
        )

        self.assertEqual(job["match_percentage"], expected_score)

        # Verify the maximum weighted points.
        self.assertEqual(job["skill_match_score"], 33.34)
        self.assertEqual(job["experience_match_score"], 15.0)

    def test_matched_and_missing_skills_are_identified(self):
        self.create_job(
            title="Python Developer",
            required_skills="Python, Django, REST API",
        )

        response = self.client.get(self.url)
        job = response.data["results"][0]

        self.assertEqual(
            set(job["matched_skills"]),
            {"Python", "Django"},
        )
        self.assertEqual(
            set(job["missing_skills"]),
            {"REST API"},
        )

    def test_inactive_jobs_are_not_recommended(self):
        self.create_job(
            title="Active Python Developer",
            required_skills="Python, Django",
            is_active=True,
        )

        self.create_job(
            title="Inactive Python Developer",
            required_skills="Python, Django",
            is_active=False,
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["title"],
            "Active Python Developer",
        )

    def test_recommendations_are_sorted_by_final_score(self):
        self.create_job(
            title="Python Developer",
            required_skills="Python, Django",
            description="Python Django backend development.",
        )

        self.create_job(
            title="Frontend Developer",
            required_skills="HTML, CSS, React",
            description="Frontend web development using HTML CSS React.",
        )

        response = self.client.get(self.url)

        scores = [
            job["match_percentage"]
            for job in response.data["results"]
        ]

        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_non_job_seeker_cannot_access_recommendations(self):
        self.client.force_authenticate(user=self.provider)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
