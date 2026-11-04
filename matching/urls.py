
from django.urls import path

from .views import JobRecommendationsAPIView

urlpatterns = [
    path(
        "recommendations/",
        JobRecommendationsAPIView.as_view(),
        name="job-recommendations"
    ),
]
