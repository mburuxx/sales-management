"""
Test cases for store mixins.
"""

from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import HttpResponse
from django.views.generic import View
from unittest.mock import patch

from accounts.models import Profile, UserRole
from store.mixins import PermissionDeniedMixin

User = get_user_model()


class TestView(PermissionDeniedMixin, View):
    """Test view using PermissionDeniedMixin."""
    
    permission_denied_message = "Test permission denied message"
    
    def test_func(self):
        """Test function that determines if user has permission."""
        return False  # Always deny permission for testing
        
    def get(self, request):
        """Handle GET request."""
        return HttpResponse("Success")


class TestViewWithPermission(PermissionDeniedMixin, View):
    """Test view that grants permission."""
    
    def test_func(self):
        """Test function that grants permission."""
        return True
        
    def get(self, request):
        """Handle GET request."""
        return HttpResponse("Success")


class PermissionDeniedMixinTest(TestCase):
    """Test cases for PermissionDeniedMixin."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.profile = Profile.objects.create(
            user=self.user,
            role=UserRole.ADMIN
        )

    def test_permission_denied_default_message(self):
        """Test default permission denied message."""
        request = self.factory.get('/test/')
        request.user = self.user
        
        view = PermissionDeniedMixin()
        view.request = request
        
        response = view.handle_no_permission()
        
        self.assertEqual(response.status_code, 403)
        self.assertContains(
            response, 
            'You do not have sufficient permissions to view this content.',
            status_code=403
        )

    def test_permission_denied_custom_message(self):
        """Test custom permission denied message."""
        request = self.factory.get('/test/')
        request.user = self.user
        
        view = TestView()
        view.request = request
        
        response = view.handle_no_permission()
        
        self.assertEqual(response.status_code, 403)
        self.assertContains(
            response, 
            'Test permission denied message',
            status_code=403
        )

    def test_permission_denied_context(self):
        """Test that permission denied response includes correct context."""
        request = self.factory.get('/test/')
        request.user = self.user
        
        view = TestView()
        view.request = request
        
        with patch('store.mixins.render') as mock_render:
            mock_render.return_value = HttpResponse("Mocked response", status=403)
            
            response = view.handle_no_permission()
            
            # Check that render was called with correct context
            mock_render.assert_called_once()
            args, kwargs = mock_render.call_args
            
            self.assertEqual(args[0], request)
            self.assertEqual(args[1], 'store/permission_denied.html')
            self.assertEqual(kwargs['status'], 403)
            
            context = args[2]
            self.assertEqual(context['message'], 'Test permission denied message')
            self.assertEqual(context['redirect_delay'], 5)
            self.assertTrue('redirect_url' in context)

    def test_default_redirect_url_name(self):
        """Test default redirect URL name."""
        mixin = PermissionDeniedMixin()
        self.assertEqual(mixin.redirect_url_name, 'dashboard')

    def test_default_redirect_delay(self):
        """Test default redirect delay."""
        mixin = PermissionDeniedMixin()
        self.assertEqual(mixin.redirect_delay, 5)

    def test_raise_exception_false(self):
        """Test that raise_exception is set to False."""
        mixin = PermissionDeniedMixin()
        self.assertFalse(mixin.raise_exception)

    def test_permission_granted_flow(self):
        """Test normal flow when permission is granted."""
        request = self.factory.get('/test/')
        request.user = self.user
        
        view = TestViewWithPermission.as_view()
        response = view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Success")

    def test_permission_denied_flow(self):
        """Test flow when permission is denied."""
        request = self.factory.get('/test/')
        request.user = self.user
        
        with patch('store.mixins.render') as mock_render:
            mock_render.return_value = HttpResponse("Permission denied", status=403)
            
            view = TestView.as_view()
            response = view(request)
            
            self.assertEqual(response.status_code, 403)

    def test_custom_redirect_url_name(self):
        """Test custom redirect URL name."""
        class CustomRedirectView(PermissionDeniedMixin, View):
            redirect_url_name = 'custom-dashboard'
            
            def test_func(self):
                return False
                
            def get(self, request):
                return HttpResponse("Success")

        request = self.factory.get('/test/')
        request.user = self.user
        
        view = CustomRedirectView()
        view.request = request
        
        with patch('store.mixins.render') as mock_render, \
             patch('store.mixins.reverse_lazy') as mock_reverse:
            mock_render.return_value = HttpResponse("Mocked response", status=403)
            mock_reverse.return_value = '/custom-dashboard/'
            
            response = view.handle_no_permission()
            
            mock_reverse.assert_called_once_with('custom-dashboard')

    def test_custom_redirect_delay(self):
        """Test custom redirect delay."""
        class CustomDelayView(PermissionDeniedMixin, View):
            redirect_delay = 10
            
            def test_func(self):
                return False
                
            def get(self, request):
                return HttpResponse("Success")

        request = self.factory.get('/test/')
        request.user = self.user
        
        view = CustomDelayView()
        view.request = request
        
        with patch('store.mixins.render') as mock_render:
            mock_render.return_value = HttpResponse("Mocked response", status=403)
            
            response = view.handle_no_permission()
            
            args, kwargs = mock_render.call_args
            context = args[2]
            self.assertEqual(context['redirect_delay'], 10)

    def test_mixin_inheritance(self):
        """Test that mixin properly inherits from UserPassesTestMixin."""
        from django.contrib.auth.mixins import UserPassesTestMixin
        
        self.assertTrue(issubclass(PermissionDeniedMixin, UserPassesTestMixin))

    def test_template_path(self):
        """Test that correct template path is used."""
        request = self.factory.get('/test/')
        request.user = self.user
        
        view = TestView()
        view.request = request
        
        with patch('store.mixins.render') as mock_render:
            mock_render.return_value = HttpResponse("Mocked response", status=403)
            
            response = view.handle_no_permission()
            
            args, kwargs = mock_render.call_args
            template_path = args[1]
            self.assertEqual(template_path, 'store/permission_denied.html')

    def test_anonymous_user(self):
        """Test mixin behavior with anonymous user."""
        from django.contrib.auth.models import AnonymousUser
        
        request = self.factory.get('/test/')
        request.user = AnonymousUser()
        
        view = TestView()
        view.request = request
        
        with patch('store.mixins.render') as mock_render:
            mock_render.return_value = HttpResponse("Permission denied", status=403)
            
            response = view.handle_no_permission()
            
            self.assertEqual(response.status_code, 403)

    def test_staff_user_permission(self):
        """Test with staff user."""
        staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='testpass123',
            is_staff=True
        )
        
        class StaffOnlyView(PermissionDeniedMixin, View):
            def test_func(self):
                return self.request.user.is_staff
                
            def get(self, request):
                return HttpResponse("Staff access granted")

        request = self.factory.get('/test/')
        request.user = staff_user
        
        view = StaffOnlyView.as_view()
        response = view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "Staff access granted")

    def test_non_staff_user_permission(self):
        """Test with non-staff user."""
        class StaffOnlyView(PermissionDeniedMixin, View):
            permission_denied_message = "Staff access required"
            
            def test_func(self):
                return self.request.user.is_staff
                
            def get(self, request):
                return HttpResponse("Staff access granted")

        request = self.factory.get('/test/')
        request.user = self.user  # Non-staff user
        
        with patch('store.mixins.render') as mock_render:
            mock_render.return_value = HttpResponse("Permission denied", status=403)
            
            view = StaffOnlyView.as_view()
            response = view(request)
            
            self.assertEqual(response.status_code, 403)