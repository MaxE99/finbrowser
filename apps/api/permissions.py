from rest_framework.permissions import BasePermission

class IsListCreator(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user

class IsUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user