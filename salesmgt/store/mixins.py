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
    
    # Default URL name to redirect to (change this if your dashboard URL is named differently)
    redirect_url_name = 'dashboard'

    # Default delay before redirection (in seconds)
    redirect_delay = 5 
    
    # CRITICAL: This attribute tells UserPassesTestMixin NOT to raise a 403
    # and instead call the handle_no_permission() method.
    raise_exception = False

    def handle_no_permission(self):
        """
        Renders the custom template with the denial message and redirect logic.
        This method is called when test_func() returns False.
        """
        # Safely retrieve the message defined in the inheriting view
        message = getattr(
            self, 
            'permission_denied_message', 
            'You do not have sufficient permissions to view this content.'
        )
        
        context = {
            'message': message,
            # Resolve the URL name to an actual URL
            'redirect_url': reverse_lazy(self.redirect_url_name), 
            'redirect_delay': self.redirect_delay 
        }
        
        # Render the custom permission denied template using the context
        return render(self.request, 'store/permission_denied.html', context, status=403)
