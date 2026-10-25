from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView

from .forms import ProductForm
from .models import Category, Product


class HomeView(ListView):
    model = Product
    template_name = "store/home.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.order_by("price")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.annotate(
            product_count=Count("products")
        ).filter(product_count__gt=0)
        return context


class ShopView(ListView):
    model = Product
    template_name = "store/shop.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.order_by("price")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.annotate(
            product_count=Count("products")
        )
        return context


class CategoryDetailView(DetailView):
    model = Category
    template_name = "store/category.html"
    context_object_name = "category"
    pk_url_kwarg = "category_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = Product.objects.filter(
            category=self.object
        ).order_by("price")
        return context


class SaleProductsView(ListView):
    model = Product
    template_name = "store/sale.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.filter(is_on_sale=True).order_by("price")


class ProductDetailView(DetailView):
    model = Product
    template_name = "store/product_detail.html"
    context_object_name = "product"
    pk_url_kwarg = "product_id"


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "store/product_form.html"
    extra_context = {"title": "Add Product"}

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("product_detail", kwargs={"product_id": self.object.id})


@login_required
def product_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.user != request.user:
        raise PermissionDenied

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect("product_detail", product_id=product.id)
    else:
        form = ProductForm(instance=product)

    context = {
        "form": form,
        "title": "Edit Product",
    }
    return render(request, "store/product_form.html", context)


@login_required
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.user != request.user:
        raise PermissionDenied

    if request.method == "POST":
        product.delete()
        return redirect("shop")

    return render(request, "store/product_confirm_delete.html", {"product": product})