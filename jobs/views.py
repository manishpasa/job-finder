
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import Job
from .serializers import JobSerializer
from .permissions import IsProviderOrReadOnly

from rest_framework import serializers
class JobViewSet(viewsets.ModelViewSet):

    serializer_class = JobSerializer
    permission_classes = [AllowAny, IsProviderOrReadOnly]

    def get_queryset(self):
        queryset = Job.objects.filter(is_active=True)

        # Providers can also see their own inactive jobs.
        if (
            self.request.user.is_authenticated
            and self.request.user.role == "JOB_PROVIDER"
        ):
            queryset = Job.objects.filter(
                Q(is_active=True) | Q(provider=self.request.user)
            ).distinct()

        # Search by title, category or location.
        search = self.request.query_params.get("search")

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(category__icontains=search)
                | Q(location__icontains=search)
            )

        return queryset.order_by("-created_at")

    def perform_create(self, serializer):
        try:
            company = self.request.user.provider_profile
        except Exception:
            raise serializers.ValidationError(
            "Please complete your company profile before posting a job."
        )

        if not company.company_name.strip():
            raise serializers.ValidationError(
            "Please add your company name before posting a job."
        )

        serializer.save(
            provider=self.request.user,
             company_name=company.company_name
        )