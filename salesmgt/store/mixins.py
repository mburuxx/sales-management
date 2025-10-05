from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin


class PermissionDeniedMixin(UserPassesTestMixin):
    """
    Mixin to override the default behavior of UserPassesTestMixin when a 
    permission test fails. 
    
    Instead of raising a 403 exception, it renders the custom permission_denied.html 
    template and handles an automatic redirect to the dashboard.

    Views using this mixin must define:
    - permission_denied_message (string): The message to display to the user.
    """
    
    redirect_url_name = 'dashboard'

    redirect_delay = 5 
    
    raise_exception = False

    def handle_no_permission(self):
        """
        Renders the custom template with the denial message and redirect logic.
        This method is called when test_func() returns False.
        """
        message = getattr(
            self, 
            'permission_denied_message', 
            'You do not have sufficient permissions to view this content.'
        )
        
        context = {
            'message': message,
            'redirect_url': reverse_lazy(self.redirect_url_name), 
            'redirect_delay': self.redirect_delay 
        }
        
        return render(self.request, 'store/permission_denied.html', context, status=403)
