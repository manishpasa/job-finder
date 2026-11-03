from django.conf import settings
from django.db import models


class CVProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cv_profile"
    )

    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255, blank=True)
    professional_title = models.CharField(max_length=200, blank=True)
    career_objective = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"CV of {self.full_name}"
class Education(models.Model):
    cv_profile = models.ForeignKey(
        CVProfile,
        on_delete=models.CASCADE,
        related_name="education"
    )

    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=150)
    field_of_study = models.CharField(max_length=150)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(null=True, blank=True)
    grade = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.degree} - {self.institution}"

class WorkExperience(models.Model):
    cv_profile = models.ForeignKey(
        CVProfile,
        on_delete=models.CASCADE,
        related_name="work_experiences"
    )

    job_title = models.CharField(max_length=150)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.job_title} at {self.company}"


class Skill(models.Model):
    cv_profile = models.ForeignKey(
        CVProfile,
        on_delete=models.CASCADE,
        related_name="skills"
    )

    name = models.CharField(max_length=100)
    proficiency = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name


class Certification(models.Model):
    cv_profile = models.ForeignKey(
        CVProfile,
        on_delete=models.CASCADE,
        related_name="certifications"
    )

    name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    credential_id = models.CharField(max_length=150, blank=True)
    credential_url = models.URLField(blank=True)

    def __str__(self):
        return self.name
