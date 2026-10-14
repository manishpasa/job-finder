
from rest_framework.permissions import BasePermission


class IsJobSeeker(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "JOB_SEEKER"
        )


class IsJobProvider(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "JOB_PROVIDER"
        )


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_staff
            and request.user.is_superuser
        )
