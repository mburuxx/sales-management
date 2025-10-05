from django import forms
from .models import Item, Category, Delivery
from accounts.models import Customer
from phonenumber_field.formfields import PhoneNumberField

class ItemForm(forms.ModelForm):
    """
    A form for creating or updating an Item in the inventory,
    with custom validation for quantity and price.
    """
    class Meta:
        model = Item
        fields = [
            'name',
            'description',
            'category',
            'quantity',
            'price',
            'expiring_date',
            'vendor'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4
                }
            ),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01'
                }
            ),
            'expiring_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
            'vendor': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_quantity(self):
        """ Validation for the quantity field. """
        quantity = self.cleaned_data.get('quantity')

        if quantity is not None and quantity < 1:
            raise forms.ValidationError("The quantity must be 1 or greater.")

        return quantity

    def clean_price(self):
        """ Custom validation to ensure the price is not negative. """
        price = self.cleaned_data.get('price')

        if price is not None and price < 0:
            raise forms.ValidationError("The price cannot be negative.")

        return price


class CategoryForm(forms.ModelForm):
    """
    A form for creating or updating category.
    """
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name',
                'aria-label': 'Category Name'
            }),
        }
        labels = {
            'name': 'Category Name',
        }

class DeliveryForm(forms.ModelForm):

    # Set required=False here because the customer might be created via the other fields.
    existing_customer = forms.ModelChoiceField(
        queryset=Customer.objects.all().order_by('first_name'),
        required=False,
        empty_label="--- Select Existing Customer ---",
        label="Select Existing Customer",
        widget=forms.Select(attrs={'class': 'form-control select2-enabled'})
    )

    # Fields for creating a new customer if not selecting an existing one
    new_customer_first_name = forms.CharField(
        max_length=256, required=False, label="New Customer First Name",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Only fill if new customer'})
    )
    new_customer_phone = PhoneNumberField(
        required=False, label="New Customer Phone",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone for new customer'})
    )
    new_customer_location = forms.CharField(
        max_length=256, required=False, label="New Customer Address/Location",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address for new customer'})
    )

    class Meta:
        model = Delivery
        fields = ['item', 'date', 'is_delivered'] 
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_delivered': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['is_delivered', 'existing_customer', 'new_customer_phone']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        
        existing_customer = cleaned_data.get('existing_customer')
        new_first_name = cleaned_data.get('new_customer_first_name')
        new_phone = cleaned_data.get('new_customer_phone')

        is_new_customer = bool(new_first_name or new_phone)

        if existing_customer and is_new_customer:
            raise forms.ValidationError(
                "Please either select an existing customer OR fill out the new customer details, not both."
            )
        
        if not existing_customer and not is_new_customer:
            raise forms.ValidationError(
                "You must either select an existing customer or provide details for a new one."
            )

        if is_new_customer:
            if not new_first_name:
                 self.add_error('new_customer_first_name', "First Name is required for a new customer.")
            if not new_phone:
                 self.add_error('new_customer_phone', "Phone Number is required for a new customer.")
            
        return cleaned_data