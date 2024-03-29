from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import ProtectedError
from django.shortcuts import redirect


class UserAuthRequiredMixin(LoginRequiredMixin):
    """
    Mixin to require user authentication.

    This mixin ensures that the user is authenticated before accessing a view.
    If the user is not authenticated, it displays an error message and
     redirects them to the login page.

    Attributes:
        permission_denied_message (str): The message to display when
         permission is denied.
        login_url (str): The URL to redirect to for login.
    """
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.error(self.request, self.permission_denied_message)
            return redirect(self.login_url)
        return super().dispatch(request, *args, **kwargs)


class UserPermissionMixin(UserPassesTestMixin):
    """
    Mixin to check user permissions.

    This mixin ensures that the user has permission to access a view based on
     a test function.
    If the test function fails, it displays an error message and redirects
     them to a specified URL.

    Attributes:
        permission_message (str): The message to display when permission
         is denied.
        permission_url (str): The URL to redirect to when permission
         is denied.
    """
    permission_message = None
    permission_url = None

    def test_func(self):
        return self.get_object() == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, self.permission_message)
        return redirect(self.permission_url)


class BookingPermissionMixin(UserPassesTestMixin):
    """
    Test function to check booking permission.

    Returns:
        bool: True if the user has permission, False otherwise.
    """
    foreign_book_message = None
    foreign_book_url = None

    def test_func(self):
        booking = self.get_object()
        return booking.rider == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, self.foreign_book_message)
        return redirect(self.foreign_book_url)


class ObjectDoesNotExistMixin:
    """
    Mixin to handle ObjectDoesNotExist exceptions.

    This mixin catches ObjectDoesNotExist exceptions raised during view
     dispatching.
    If such an exception occurs, it displays an error message and redirects
     the user to a specified URL.

    Attributes:
        not_existed_message (str): The message to display when the object
         does not exist.
        not_existed_url (str): The URL to redirect to when the object
         does not exist.
    """
    not_existed_message = None
    not_existed_url = None

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except ObjectDoesNotExist:
            messages.error(request, self.not_existed_message)
            return redirect(self.not_existed_url)


class DeleteProtectionMixin:
    """
    Mixin to handle ProtectedError exceptions during deletion.

    This mixin catches ProtectedError exceptions raised during deletion
     operations.
    If such an exception occurs, it displays an error message and redirects
     the user to a specified URL.

    Attributes:
        protection_message (str): The message to display when deletion
         is protected.
        protected_url (str): The URL to redirect to when deletion
         is protected.
    """
    protection_message = None
    protected_url = None

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, self.protection_message)
            return redirect(self.protected_url)
