from rest_framework.permissions import BasePermission


class IsListCreator(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.creator == request.user


class IsUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsPortfolioCreator(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.portfolio.user == request.user


class PortfolioKeywordPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return request.user == obj.portfolio_stocks.all().first().portfolio.user
        return super().has_object_permission(request, view, obj)
