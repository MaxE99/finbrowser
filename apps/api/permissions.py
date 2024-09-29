from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class IsListCreator(BasePermission):
    """
    Permission class to check if the authenticated user is the creator of the list.

    This permission is used to ensure that only the list creator can perform certain actions on the list.
    """

    def has_object_permission(self, request: Request, view, obj) -> bool:
        """
        Checks if the user making the request is the creator of the list.

        Args:
            request (Request): The HTTP request object.
            view (Any): The view object (unused).
            obj (List): The list object to check permissions for.

        Returns:
            bool: True if the authenticated user is the creator of the list, False otherwise.
        """
        return obj.creator == request.user


class IsUser(BasePermission):
    """
    Permission class to check if the authenticated user is the owner of the object.

    This permission is used to ensure that only the user who owns the object can perform actions on it.
    """

    def has_object_permission(self, request: Request, view, obj) -> bool:
        """
        Checks if the user making the request is the owner of the object.

        Args:
            request (Request): The HTTP request object.
            view (Any): The view object (unused).
            obj (UserOwnedObject): The object to check permissions for, which must have a 'user' field.

        Returns:
            bool: True if the authenticated user is the owner of the object, False otherwise.
        """
        return obj.user == request.user


class IsPortfolioCreator(BasePermission):
    """
    Permission class to check if the authenticated user is the creator of the portfolio.

    This permission is used to ensure that only the portfolio creator can perform certain actions on it.
    """

    def has_object_permission(self, request: Request, view, obj) -> bool:
        """
        Checks if the user making the request is the creator of the portfolio associated with the object.

        Args:
            request (Request): The HTTP request object.
            view (Any): The view object (unused).
            obj (PortfolioStock): The portfolio stock object to check permissions for, which has a related portfolio.

        Returns:
            bool: True if the authenticated user is the creator of the portfolio, False otherwise.
        """
        return obj.portfolio.user == request.user


class PortfolioKeywordPermission(BasePermission):
    """
    Custom permission class for PortfolioKeyword objects.

    Ensures that only the portfolio creator can delete a portfolio keyword.
    """

    def has_object_permission(self, request: Request, view, obj) -> bool:
        """
        Checks if the user making the request has permission to access the portfolio keyword.

        If the request method is DELETE, checks if the user is the creator of the portfolio
        associated with the first portfolio stock in the keyword.

        Args:
            request (Request): The HTTP request object.
            view (Any): The view object (unused).
            obj (PortfolioKeyword): The portfolio keyword object to check permissions for.

        Returns:
            bool: True if the request user is allowed to perform the requested action, False otherwise.
        """
        if request.method == "DELETE":
            return request.user == obj.portfolio_stocks.all().first().portfolio.user
        return super().has_object_permission(request, view, obj)
