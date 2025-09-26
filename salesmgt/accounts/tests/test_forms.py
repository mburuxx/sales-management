# tests/test_forms.py

from django.test import TestCase
from accounts.forms import CustomerForm, VendorForm, UserUpdateForm, ProfileUpdateForm

class CustomerFormTest(TestCase):
    """
    Tests for the CustomerForm.
    """
    def test_valid_form(self):
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@test.com',
            'phone': '987654321',
            'loyalty_points': 50
        }
        form = CustomerForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        # Missing required first_name
        data = {'last_name': 'Smith'}
        form = CustomerForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)


class VendorFormTest(TestCase):
    """
    Tests for the VendorForm.
    """
    def test_valid_form(self):
        data = {
            'name': 'Supplier One',
            'phone_number': 1122334455,
            'address': '456 Market St'
        }
        form = VendorForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        # Missing required name
        data = {'phone_number': 1122334455}
        form = VendorForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class ProfileUpdateFormTest(TestCase):
    """
    Tests for ProfileUpdateForm and UserUpdateForm.
    """
    def test_profile_update_form_valid(self):
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'update@test.com',
            'telephone': '+12125552368'
        }
        form = ProfileUpdateForm(data=data)
        self.assertTrue(form.is_valid())