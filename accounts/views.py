
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import JobSeekerProfile, JobProviderProfile
from .permissions import IsJobSeeker, IsJobProvider
from .serializers import (
    RegisterSerializer,
    JobSeekerProfileSerializer,
    JobProviderProfileSerializer,
)

User = get_user_model()


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginAPIView(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        })


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        })


class JobSeekerProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = JobSeekerProfileSerializer
    permission_classes = [IsAuthenticated, IsJobSeeker]

    def get_object(self):
        profile, _ = JobSeekerProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile


class JobProviderProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = JobProviderProfileSerializer
    permission_classes = [IsAuthenticated, IsJobProvider]

    def get_object(self):
        profile, _ = JobProviderProfile.objects.get_or_create(
            user=self.request.user,
            defaults={"company_name": ""},
        )
        return profile
