from rest_framework.permissions import BasePermission


class OwnResourcePermission(BasePermission):
    message = "You don't have rights for this operation."

    def has_object_permission(self, request, view, obj):
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return request.user == obj.author
        return True



