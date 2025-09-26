# tests/test_models.py

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Profile, Vendor, Customer, ProfileStatus, UserRole

class ProfileModelTest(TestCase):
    """
    Tests for the Profile model.
    """
    @classmethod
    def setUpTestData(cls):
        # Create a user which will in turn create a profile via a signal
        cls.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='password123'
        )
        cls.profile = cls.user.profile 
        
        # You can update it if needed
        cls.profile.first_name='Test'
        cls.profile.last_name='User'
        cls.profile.save()

    def test_profile_creation(self):
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.status, ProfileStatus.INACTIVE)
        self.assertEqual(str(self.profile), 'testuser Profile')
        # AutoSlugField populates from email
        self.assertEqual(self.profile.slug, 'testexamplecom')

    def test_get_absolute_url(self):
        expected_url = reverse('profile-update', kwargs={'slug': self.profile.slug})
        self.assertEqual(self.profile.get_absolute_url(), expected_url)

    def test_image_url_property(self):
        # Test with default image
        self.assertIn('profile_pics/default.jpg', self.profile.image_url)

    def test_verbose_names(self):
        self.assertEqual(self.profile._meta.get_field('slug').verbose_name, 'Account ID')
        self.assertEqual(self.profile._meta.verbose_name, 'Profile')
        self.assertEqual(self.profile._meta.verbose_name_plural, 'Profiles')


class VendorModelTest(TestCase):
    """
    Tests for the Vendor model.
    """
    @classmethod
    def setUpTestData(cls):
        cls.vendor = Vendor.objects.create(
            name='Awesome Goods Inc.',
            phone_number=1234567890,
            address='123 Main St'
        )

    def test_vendor_creation(self):
        self.assertEqual(self.vendor.name, 'Awesome Goods Inc.')
        self.assertEqual(str(self.vendor), 'Awesome Goods Inc.')
        self.assertEqual(self.vendor.slug, 'awesome-goods-inc')
    
    def test_get_absolute_url(self):
        expected_url = reverse('vendor-update', kwargs={'slug': self.vendor.slug})
        self.assertEqual(self.vendor.get_absolute_url(), expected_url)


class CustomerModelTest(TestCase):
    """
    Tests for the Customer model.
    """
    @classmethod
    def setUpTestData(cls):
        cls.customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@email.com',
            loyalty_points=100
        )

    def test_customer_creation(self):
        self.assertEqual(self.customer.first_name, 'John')
        self.assertEqual(self.customer.loyalty_points, 100)

    def test_str_method(self):
        self.assertEqual(str(self.customer), 'John Doe')

    def test_get_full_name(self):
        self.assertEqual(self.customer.get_full_name(), 'John Doe')
        
        # Test with no last name
        customer_no_last = Customer.objects.create(first_name='Jane')
        self.assertEqual(customer_no_last.get_full_name(), 'Jane')
        
    def test_to_select2(self):
        expected_dict = {
            "label": "John Doe",
            "value": self.customer.id
        }
        self.assertEqual(self.customer.to_select2(), expected_dict)
    
    def test_get_absolute_url(self):
        expected_url = reverse('customer_update', kwargs={'pk': self.customer.pk})
        self.assertEqual(self.customer.get_absolute_url(), expected_url)