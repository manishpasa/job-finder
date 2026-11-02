from django.conf import settings
from django.db import models
from jobs.models import Job


class Application(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SHORTLISTED = "SHORTLISTED", "Shortlisted"
        REJECTED = "REJECTED", "Rejected"
        HIRED = "HIRED", "Hired"

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    seeker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_applications"
    )

    cover_letter = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    applied_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["job", "seeker"],
                name="unique_job_application"
            )
        ]
        ordering = ["-applied_at"]

    def __str__(self):
        return f"{self.seeker.username} - {self.job.title}"