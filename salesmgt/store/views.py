"""
Module: store.views

Contains Django views for managing items, profiles,
and deliveries in the store application.

Classes handle product listing, creation, updating,
deletion, and delivery management.
The module integrates with Django's authentication
and querying functionalities.
"""

# Standard library imports
import operator
from functools import reduce

# Django core imports
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count, Sum

# Authentication and permissions
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# Class-based views
from django.views.generic import (
    DetailView, CreateView, UpdateView, DeleteView, ListView
)
from django.views.generic.edit import FormMixin

# Third-party packages
from django_tables2 import SingleTableView
import django_tables2 as tables
from django_tables2.export.views import ExportMixin

# Local app imports
from accounts.models import Profile, Vendor
#from transactions.models import Sale
from .models import Category, Item, Delivery
from .forms import ItemForm, CategoryForm, DeliveryForm
from .tables import ItemTable
from .mixins import PermissionDeniedMixin
from accounts.models import UserRole


@login_required
def dashboard(request):
    profiles = Profile.objects.all()
    Category.objects.annotate(nitem=Count("item"))
    items = Item.objects.all()
    total_items = (
        Item.objects.all()
        .aggregate(Sum("quantity"))
        .get("quantity__sum", 0.00)
    )
    items_count = items.count()
    profiles_count = profiles.count()

    # Prepare data for charts
    category_counts = Category.objects.annotate(
        item_count=Count("item")
    ).values("name", "item_count")
    categories = [cat["name"] for cat in category_counts]
    category_counts = [cat["item_count"] for cat in category_counts]

    #sale_dates = (
    #    Sale.objects.values("date_added__date")
    #   .annotate(total_sales=Sum("grand_total"))
    #    .order_by("date_added__date")
    #)
    #sale_dates_labels = [
    #    date["date_added__date"].strftime("%Y-%m-%d") for date in sale_dates
    #]
    #sale_dates_values = [float(date["total_sales"]) for date in sale_dates]

    context = {
        "items": items,
        "profiles": profiles,
        "profiles_count": profiles_count,
        "items_count": items_count,
        "total_items": total_items,
        "vendors": Vendor.objects.all(),
        "delivery": Delivery.objects.all(),
        #"sales": Sale.objects.all(),
        "categories": categories,
        "category_counts": category_counts,
        #"sale_dates_labels": sale_dates_labels,
        #"sale_dates_values": sale_dates_values,
    }
    return render(request, "store/dashboard.html", context)


class ProductListView(LoginRequiredMixin, ExportMixin, tables.SingleTableView):
    """
    View class to display a list of products.

    Attributes:
    - model: The model associated with the view.
    - table_class: The table class used for rendering.
    - template_name: The HTML template used for rendering the view.
    - context_object_name: The variable name for the context object.
    - paginate_by: Number of items per page for pagination.
    """

    model = Item
    table_class = ItemTable
    template_name = "store/product_list.html"
    context_object_name = "items"
    paginate_by = 10
    SingleTableView.table_pagination = False


class ItemSearchListView(ProductListView):
    """
    View class to search and display a filtered list of items.

    Attributes:
    - paginate_by: Number of items per page for pagination.
    """

    paginate_by = 10

    def get_queryset(self):
        result = super(ItemSearchListView, self).get_queryset()

        query = self.request.GET.get("q")
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(
                    operator.and_, (Q(name__icontains=q) for q in query_list)
                )
            )
        return result


class ProductDetailView(LoginRequiredMixin, FormMixin, DetailView):
    """
    View class to display detailed information about a product.

    Attributes:
    - model: The model associated with the view.
    - template_name: The HTML template used for rendering the view.
    """

    model = Item
    template_name = "store/product_detail.html"
    form_class = ItemForm

    def get_success_url(self):
        return reverse("product-detail", kwargs={"slug": self.object.slug})


class ProductCreateView(LoginRequiredMixin, PermissionDeniedMixin, CreateView):
    """
    View class to create a new product.

    Attributes:
    - model: The model associated with the view.
    - template_name: The HTML template used for rendering the view.
    - form_class: The form class used for data input.
    - success_url: The URL to redirect to upon successful form submission.
    """

    model = Item
    template_name = "store/product_create.html"
    form_class = ItemForm
    success_url = reverse_lazy("productslist")

    permission_denied_message = "You must have admin status to create inventory products."

    def test_func(self):
        """
        Required by UserPassesTestMixin. Checks if the user is a superuser OR staff.
        """
        return self.request.user.get_role() in [UserRole.ADMIN, UserRole.EXECUTIVE]

    


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    View class to update product information.

    Attributes:
    - model: The model associated with the view.
    - template_name: The HTML template used for rendering the view.
    - fields: The fields to be updated.
    - success_url: The URL to redirect to upon successful form submission.
    """

    model = Item
    template_name = "store/product_update.html"
    form_class = ItemForm
    success_url = reverse_lazy("productslist") 

    # Custom permission handling
    permission_denied_message = "You must have admin status to update inventory items."
    
    # 2. Prevent raising 403, allowing handle_no_permission to execute
    raise_exception = False 

    def test_func(self):
        # Only allow superusers to access this page
        return self.request.user.is_superuser

    def handle_no_permission(self):
        """
        Called when the user fails the test_func. 
        Instead of 403, render a custom message template that redirects.
        """
        context = {
            'message': self.permission_denied_message,
            'redirect_url': reverse_lazy('dashboard'), # Redirect to your dashboard URL name
            'redirect_delay': 3 # Redirect after 3 seconds
        }
        # Use render() to display the custom template with the message/redirect info
        return render(self.request, 'store/permission_denied.html', context, status=403)



class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View class to delete a product.

    Attributes:
    - model: The model associated with the view.
    - template_name: The HTML template used for rendering the view.
    - success_url: The URL to redirect to upon successful deletion.
    """

    model = Item
    template_name = "store/product_delete.html"
    success_url = "/products/"

    def test_func(self):
        return self.request.user.get_role() in [UserRole.ADMIN, UserRole.EXECUTIVE]



class DeliveryListView(
    LoginRequiredMixin, ExportMixin, tables.SingleTableView
):
    """
    View class to display a list of deliveries.

    Attributes:
    - model: The model associated with the view.
    - pagination: Number of items per page for pagination.
    - template_name: The HTML template used for rendering the view.
    - context_object_name: The variable name for the context object.
    """

    model = Delivery
    pagination = 10
    template_name = "store/deliveries.html"
    context_object_name = "deliveries"


class DeliverySearchListView(DeliveryListView):
    """
    View class to search and display a filtered list of deliveries.

    Attributes:
    - paginate_by: Number of items per page for pagination.
    """

    paginate_by = 10

    def get_queryset(self):
        result = super(DeliverySearchListView, self).get_queryset()

        query = self.request.GET.get("q")
        if query:
            query_list = query.split()
            result = result.filter(
                reduce(
                    operator.
                    and_, (Q(customer_name__icontains=q) for q in query_list)
                )
            )
        return result


class DeliveryDetailView(LoginRequiredMixin, DetailView):
    """
    View class to display detailed information about a delivery.

    Attributes:
    - model: The model associated with the view.
    - template_name: The HTML template used for rendering the view.
    """

    model = Delivery
    template_name = "store/delivery_detail.html"


# store/views.py

from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Delivery
from .forms import DeliveryForm
from accounts.models import Customer
# Assuming DeliveryCreateView is defined here

class DeliveryCreateView(LoginRequiredMixin, CreateView):
    model = Delivery
    form_class = DeliveryForm
    template_name = "store/delivery_form.html"
    success_url = "/deliveries/"

    def form_valid(self, form):
        # 1. Check if an existing customer was selected
        customer = form.cleaned_data.get('existing_customer')
        
        if customer:
            # Case A: Existing customer selected. Set the FK field.
            form.instance.customer = customer
        
        else:
            # Case B: New customer details provided. Must create customer first.
            
            # Use form data to create a new Customer object
            new_customer = Customer.objects.create(
                first_name=form.cleaned_data['new_customer_first_name'],
                # We save new customer location in the Customer's 'address' field
                address=form.cleaned_data['new_customer_location'],
                phone=form.cleaned_data['new_customer_phone'],
                # You can add logic for last_name/email if you add those to the form
            )
            
            # Set the new Customer object as the Foreign Key for the Delivery
            form.instance.customer = new_customer
            
        # 2. Save the Delivery object
        return super().form_valid(form)


class DeliveryUpdateView(LoginRequiredMixin, UpdateView):
    """
    View class to update delivery information.

    Attributes:
    - model: The model associated with the view.
    - fields: The fields to be updated.
    - template_name: The HTML template used for rendering the view.
    - success_url: The URL to redirect to upon successful form submission.
    """

    model = Delivery
    form_class = DeliveryForm
    template_name = "store/delivery_form.html"
    success_url = "/deliveries/"


class DeliveryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    View class to delete a delivery.

    Attributes:
    - model: The model associated with the view.
    - template_name: The HTML template used for rendering the view.
    - success_url: The URL to redirect to upon successful deletion.
    """

    model = Delivery
    template_name = "store/delivery_delete.html"
    success_url = "/deliveries/"

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        else:
            return False


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'store/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10
    login_url = 'login'


class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'store/category_detail.html'
    context_object_name = 'category'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        """
        Overrides context data to include a list of all products in this category 
        and the count of unique vendors supplying them.
        """
        context = super().get_context_data(**kwargs)
        
        current_category = self.object
        
        # 1. Fetch all Item objects belonging to this category
        items_in_category = Item.objects.filter(category=current_category)
        context['items_in_category'] = items_in_category
        
        # 2. Efficiently count the number of unique vendors
        # We query the Item model, filter by category, and count the distinct vendor_id values.
        # .distinct() here operates on the QuerySet fields that are being aggregated/counted.
        unique_vendor_count = items_in_category.values('vendor').distinct().count()
        context['unique_vendor_count'] = unique_vendor_count

        return context


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    template_name = 'store/category_form.html'
    form_class = CategoryForm
    login_url = 'login'

    def get_success_url(self):
        return reverse_lazy('category-detail', kwargs={'pk': self.object.pk})


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    template_name = 'store/category_form.html'
    form_class = CategoryForm
    login_url = 'login'

    def get_success_url(self):
        return reverse_lazy('category-detail', kwargs={'pk': self.object.pk})


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'store/category_delete.html'
    context_object_name = 'category'
    success_url = reverse_lazy('category-list')
    login_url = 'login'


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@csrf_exempt
@require_POST
@login_required
def get_items_ajax_view(request):
    if is_ajax(request):
        try:
            term = request.POST.get("term", "")
            data = []

            items = Item.objects.filter(name__icontains=term)
            for item in items[:10]:
                data.append(item.to_json())

            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Not an AJAX request'}, status=400)