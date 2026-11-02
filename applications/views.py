from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from .models import Application
from .serializers import (
    ApplicationSerializer,
    ApplicationStatusSerializer,
)
from .permissions import IsJobSeeker, IsJobProvider


class ApplyForJobAPIView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsJobSeeker]

    def perform_create(self, serializer):
        job = serializer.validated_data.get("job")

        if Application.objects.filter(
            job=job,
            seeker=self.request.user
        ).exists():
            raise ValidationError("You have already applied for this job.")

        if not job.is_active:
            raise ValidationError("This job is no longer active.")

        serializer.save(seeker=self.request.user)


class MyApplicationsAPIView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsJobSeeker]

    def get_queryset(self):
        return Application.objects.filter(
            seeker=self.request.user
        ).select_related("job", "seeker")


class JobApplicantsAPIView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsJobProvider]

    def get_queryset(self):
        job_id = self.kwargs["job_id"]

        return Application.objects.filter(
            job_id=job_id,
            job__provider=self.request.user
        ).select_related("job", "seeker")


class UpdateApplicationStatusAPIView(generics.UpdateAPIView):
    serializer_class = ApplicationStatusSerializer
    permission_classes = [IsAuthenticated, IsJobProvider]
    http_method_names = ["patch", "options", "head"]

    def get_queryset(self):
        return Application.objects.filter(
            job__provider=self.request.user
        ).select_related("job", "seeker")