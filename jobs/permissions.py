
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsProviderOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return (
            request.user.is_authenticated
            and request.user.role == "JOB_PROVIDER"
        )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return (
            request.user.is_authenticated
            and (
                request.user.role == "ADMIN"
                or (
                    request.user.role == "JOB_PROVIDER"
                    and obj.provider_id == request.user.id
                )
            )
        )
