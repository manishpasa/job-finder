from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import CVProfile
from .serializers import CVProfileSerializer


class CVProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = CVProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, created = CVProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                "full_name": self.request.user.username,
                "email": self.request.user.email,
                "phone": "",
            }
        )
        return profile