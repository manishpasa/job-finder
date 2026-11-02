from django.urls import path
from .views import CVProfileAPIView

urlpatterns = [
    path("profile/", CVProfileAPIView.as_view(), name="cv-profile"),
]