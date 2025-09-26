# tests/test_urls.py

from django.test import SimpleTestCase
from django.urls import reverse, resolve
from accounts import views

class UrlsTest(SimpleTestCase):
    """
    Tests for URL resolution in the accounts app.
    """
    def test_register_url_resolves(self):
        url = reverse('user-register')
        self.assertEqual(resolve(url).func, views.register)

    def test_profile_url_resolves(self):
        url = reverse('user-profile')
        self.assertEqual(resolve(url).func, views.profile)

    def test_profile_list_url_resolves(self):
        url = reverse('profile_list')
        self.assertEqual(resolve(url).func.view_class, views.ProfileListView)

    def test_customer_list_url_resolves(self):
        url = reverse('customer_list')
        self.assertEqual(resolve(url).func.view_class, views.CustomerListView)

    def test_customer_create_url_resolves(self):
        url = reverse('customer_create')
        self.assertEqual(resolve(url).func.view_class, views.CustomerCreateView)

    def test_customer_update_url_resolves(self):
        # Requires a pk argument
        url = reverse('customer_update', args=[1])
        self.assertEqual(resolve(url).func.view_class, views.CustomerUpdateView)

    def test_vendor_list_url_resolves(self):
        url = reverse('vendor-list')
        self.assertEqual(resolve(url).func.view_class, views.VendorListView)

    def test_vendor_create_url_resolves(self):
        url = reverse('vendor-create')
        self.assertEqual(resolve(url).func.view_class, views.VendorCreateView)

    def test_vendor_update_url_resolves(self):
        # Requires a slug argument
        url = reverse('vendor-update', args=['some-slug'])
        self.assertEqual(resolve(url).func.view_class, views.VendorUpdateView)