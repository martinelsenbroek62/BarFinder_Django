from rest_framework.permissions import IsAuthenticated


class IsOwnerPermission(IsAuthenticated):

    def has_object_permission(self, request, view, obj):
        if request.user != obj:
            return False
        return True
