from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django_extensions.db.fields import AutoSlugField
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from phonenumber_field.modelfields import PhoneNumberField


# Define choices using a Class

class ProfileStatus(models.TextChoices):
    """Choices for the user's account status."""
    INACTIVE = 'INA', _('Inactive')
    ACTIVE = 'A', _('Active')
    ON_LEAVE = 'OL', _('On leave')


class UserRole(models.TextChoices):
    """Choices for the user's role within the organization."""
    OPERATIVE = 'OP', _('Operative')
    EXECUTIVE = 'EX', _('Executive')
    ADMIN = 'AD', _('Admin')

# Models
class Profile(models.Model):
    """
    Represents a user profile containing personal and account-related details.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='User'
    )
    slug = AutoSlugField(
        unique=True,
        verbose_name='Account ID',
        populate_from='user__email',
        help_text="Unique identifier for the profile, populated from the email address."
    )
    profile_picture = ProcessedImageField(
        default='profile_pics/default.jpg',
        upload_to='profile_pics',
        format='JPEG',
        processors=[ResizeToFill(150, 150)],
        options={'quality': 100},
        verbose_name='Profile Picture'
    )
    telephone = PhoneNumberField(
        null=True, blank=True, verbose_name='Telephone'
    )
    email = models.EmailField(
        max_length=150, blank=True, null=True, verbose_name='Email'
    )
    first_name = models.CharField(
        max_length=30, blank=True, verbose_name='First Name'
    )
    last_name = models.CharField(
        max_length=30, blank=True, verbose_name='Last Name'
    )

    status = models.CharField(
        choices=ProfileStatus.choices,
        max_length=12,
        default=ProfileStatus.INACTIVE, # Using the TextChoices constant for default
        verbose_name='Status'
    )

    role = models.CharField(
        choices=UserRole.choices,
        max_length=12,
        blank=True,
        null=True,
        verbose_name='Role'
    )

    @property
    def image_url(self):
        """
        Returns the URL of the profile picture.
        Returns an empty string if the image is not available or not set.
        """
        if self.profile_picture:
            try:
                return self.profile_picture.url
            except ValueError:
                return ''
        return ''


    def __str__(self):
        """
        Returns a string representation of the profile using the associated username.
        """
        return f"{self.user.username} Profile"

    class Meta:
        """Meta options for the Profile model."""
        ordering = ['slug']
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def get_absolute_url(self):
        return reverse("profile-update", kwargs={"slug": self.slug})


class Vendor(models.Model):
    """
    Represents a vendor with contact and address information.
    """
    name = models.CharField(max_length=50, verbose_name='Name')
    slug = AutoSlugField(
        unique=True,
        populate_from='name',
        verbose_name='Slug'
    )

    phone_number = models.BigIntegerField(
        blank=True, null=True, verbose_name='Phone Number'
    )
    address = models.CharField(
        max_length=50, blank=True, null=True, verbose_name='Address'
    )

    def __str__(self):
        """
        Returns the name of the vendor.
        """
        return self.name

    class Meta:
        """Meta options for the Vendor model."""
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'

    def get_absolute_url(self):
        return reverse("vendor-update", kwargs={"slug": self.slug})
    
class Customer(models.Model):
    """
    Represents a customer in the sales management system, 
    tracking personal details and loyalty points.
    """
    first_name = models.CharField(max_length=256, verbose_name="First Name") # Added verbose_name
    last_name = models.CharField(max_length=256, blank=True, null=True, verbose_name="Last Name") # Added verbose_name
    address = models.TextField(max_length=256, blank=True, null=True, verbose_name="Address") # Changed to TextField, kept max_length
    email = models.EmailField(max_length=256, blank=True, null=True, verbose_name="Email") # Added verbose_name
    phone = models.CharField(max_length=30, blank=True, null=True, verbose_name="Phone") # Added verbose_name
    loyalty_points = models.IntegerField(default=0, verbose_name="Loyalty Points") # Added verbose_name

    class Meta:
        """Meta options for the Customer model."""
        db_table = 'Customers'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self) -> str:
        """
        Returns the customer's full name.
        """
        return f"{self.first_name} {self.last_name or ''}".strip()

    def get_full_name(self) -> str:
        """
        Returns the customer's full name, handling cases where last_name might be None.
        """
        return f"{self.first_name} {self.last_name or ''}".strip()

    def to_select2(self) -> dict:
        """
        Returns a dictionary formatted for Select2 dropdown widget compatibility.
        """
        select2_data = {
            "label": self.get_full_name(),
            "value": self.id
        }
        return select2_data
    
    def get_absolute_url(self):
        return reverse("customer-update", kwargs={"pk": self.pk})