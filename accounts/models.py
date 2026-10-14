from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        JOB_SEEKER = "JOB_SEEKER", "Job Seeker"
        JOB_PROVIDER = "JOB_PROVIDER", "Job Provider"
        ADMIN = "ADMIN", "Admin"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.JOB_SEEKER,
    )

    def __str__(self):
        return self.username

class JobSeekerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="seeker_profile",
    )
    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    headline = models.CharField(max_length=200, blank=True)
    career_objective = models.TextField(blank=True)
    total_experience_years = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0,
    )

    def __str__(self):
        return f"Job Seeker: {self.user.username}"


class JobProviderProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="provider_profile",
    )
    company_name = models.CharField(max_length=200)
    company_description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.company_name
