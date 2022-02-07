from rest_framework.permissions import BasePermission


class IsAuthorOrAdminOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return request.user == obj.author or request.user.is_superuser
        return True


class IsAdminOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return request.user.is_superuser
        return True



