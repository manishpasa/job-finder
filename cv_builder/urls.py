from django.urls import path
from .views import (
    CVProfileAPIView,
    EducationListCreateAPIView,
    EducationDetailAPIView,
)

urlpatterns = [
    path("profile/", CVProfileAPIView.as_view(), name="cv-profile"),
    path("education/", EducationListCreateAPIView.as_view(), name="education-list-create"),
    path("education/<int:pk>/", EducationDetailAPIView.as_view(), name="education-detail"),
]