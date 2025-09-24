from django.contrib import admin
from .models import Profile, Vendor, Customer

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Profile model.

    Enhancements include search, filtering, and organizing fields.
    """
    
    # Fields displayed on the main change list page
    list_display = (
        'user', 
        'first_name', 
        'last_name',
        'telephone', 
        'role', 
        'status', 
        'profile_picture_preview'
    )

    # Fields to use for filtering the change list
    list_filter = ('role', 'status')

    # Fields that can be searched using the admin search bar
    search_fields = ('user__username', 'email', 'telephone', 'first_name', 'last_name')
    
    # Fields that will be read-only in the admin forms
    readonly_fields = ('slug', 'profile_picture_preview')

    # Grouping and ordering fields in the admin change form
    fieldsets = (
        ('Account Information', {
            'fields': ('user', 'slug', 'status', 'role'),
            'description': 'Core user and account control settings.'
        }),
        ('Personal Details', {
            'fields': ('first_name', 'last_name', 'email', 'telephone'),
        }),
        ('Profile Picture', {
            'fields': ('profile_picture', 'profile_picture_preview'),
            'classes': ('collapse',), # Optional: Hides this section by default
        }),
    )

    # Custom method to display a clickable image thumbnail in the admin
    def profile_picture_preview(self, obj):
        # Uses HTML to display the image. Requires 'mark_safe' from django.utils.safestring
        # to prevent Django from escaping the HTML.
        from django.utils.safestring import mark_safe
        if obj.profile_picture:
            return mark_safe(f'<img src="{obj.profile_picture.url}" width="50" height="50" style="border-radius: 50%;" />')
        return "No Image"
    
    # Set a short description for the custom method header
    profile_picture_preview.short_description = 'Picture'


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Vendor model.
    """
    
    # Fields displayed on the main change list page
    list_display = ('name', 'phone_number', 'address', 'slug')
    
    # Fields displayed in the form, organized into groups
    fieldsets = (
        (None, { # Group with no title
            'fields': ('name', 'slug')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'address'),
            'description': 'Primary contact details for the vendor.'
        })
    )

    # Fields that can be searched using the admin search bar
    search_fields = ('name', 'phone_number', 'address', 'slug')
    
    # Add a filter option based on whether the address field is set
    list_filter = ('address',)

    # slug is auto-generated, so it should be read-only
    readonly_fields = ('slug',)
    
    
# @admin.register(Customer)
# class CustomerAdmin(admin.ModelAdmin):
#     """
#     Admin interface configuration for the Customer model.
#     """
#     list_display = ('first_name', 'last_name', 'email', 'phone', 'loyalty_points')
#     search_fields = ('first_name', 'last_name', 'email', 'phone')
#     list_filter = ('loyalty_points',)
#     ordering = ('-loyalty_points', 'last_name')