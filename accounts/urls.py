
from django.urls import path

from .views import (
    RegisterAPIView,
    LoginAPIView,
    CurrentUserAPIView,
    JobSeekerProfileAPIView,
    JobProviderProfileAPIView,
)

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("me/", CurrentUserAPIView.as_view(), name="current-user"),

    path(
        "profile/seeker/",
        JobSeekerProfileAPIView.as_view(),
        name="seeker-profile",
    ),
    path(
        "profile/provider/",
        JobProviderProfileAPIView.as_view(),
        name="provider-profile",
    ),
]
