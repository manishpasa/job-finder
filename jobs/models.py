
from django.conf import settings
from django.db import models


class Job(models.Model):

    class EmploymentType(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full Time"
        PART_TIME = "PART_TIME", "Part Time"
        CONTRACT = "CONTRACT", "Contract"
        INTERNSHIP = "INTERNSHIP", "Internship"

    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posted_jobs"
    )

    title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    description = models.TextField()
    required_skills = models.TextField(blank=True)
    category = models.CharField(max_length=100)
    location = models.CharField(max_length=200)

    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME
    )

    salary = models.CharField(max_length=100, blank=True)
    deadline = models.DateField(null=True, blank=True)
    vacancies = models.PositiveIntegerField(default=1)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
