from django.urls import path

from .views import (
    ApplyForJobAPIView,
    MyApplicationsAPIView,
    JobApplicantsAPIView,
    UpdateApplicationStatusAPIView,
)

urlpatterns = [
    path("apply/", ApplyForJobAPIView.as_view(), name="apply"),
    path("my/", MyApplicationsAPIView.as_view(), name="my-applications"),
    path(
        "job/<int:job_id>/",
        JobApplicantsAPIView.as_view(),
        name="job-applicants"
    ),
    path(
        "<int:pk>/status/",
        UpdateApplicationStatusAPIView.as_view(),
        name="update-application-status"
    ),
]