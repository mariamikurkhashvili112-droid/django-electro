from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView

from .forms import ProductForm
from .models import Category, Product

SORT_OPTIONS = {
    "price_asc": "price",
    "price_desc": "-price",
    "name_asc": "name",
    "name_desc": "-name",
    "newest": "-id",
}

SORT_LABELS = [
    ("price_asc", "Price: low to high"),
    ("price_desc", "Price: high to low"),
    ("name_asc", "Name: A to Z"),
    ("name_desc", "Name: Z to A"),
    ("newest", "Newest first"),
]


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
    paginate_by = 6

    @staticmethod
    def _to_decimal(value):
        if not value:
            return None
        try:
            return Decimal(value)
        except InvalidOperation:
            return None

    def get_queryset(self):
        queryset = Product.objects.select_related("category")
        params = self.request.GET

        q = params.get("q", "").strip()
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
            )

        category_id = params.get("category", "")
        if category_id.isdigit():
            queryset = queryset.filter(category_id=int(category_id))

        min_price = self._to_decimal(params.get("min_price"))
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)

        max_price = self._to_decimal(params.get("max_price"))
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)

        if params.get("sale") == "1":
            queryset = queryset.filter(is_on_sale=True)

        sort = params.get("sort", "price_asc")
        return queryset.order_by(SORT_OPTIONS.get(sort, "price"), "id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET

        context["categories"] = Category.objects.annotate(
            product_count=Count("products")
        )

        query = params.copy()
        query.pop("page", None)
        context["querystring"] = query.urlencode()

        category_id = params.get("category", "")
        context["q"] = params.get("q", "").strip()
        context["selected_category"] = int(category_id) if category_id.isdigit() else None
        context["min_price"] = params.get("min_price", "")
        context["max_price"] = params.get("max_price", "")
        context["sale"] = params.get("sale") == "1"
        context["sort"] = params.get("sort", "price_asc")
        context["sort_options"] = SORT_LABELS
        return context


class CategoryDetailView(DetailView):
    model = Category
    template_name = "store/category.html"
    context_object_name = "category"
    pk_url_kwarg = "category_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.filter(category=self.object).order_by("price")
        paginator = Paginator(products, 4)
        page_obj = paginator.get_page(self.request.GET.get("page"))
        context["products"] = page_obj
        context["page_obj"] = page_obj
        context["is_paginated"] = page_obj.has_other_pages()
        return context


class SaleProductsView(ListView):
    model = Product
    template_name = "store/sale.html"
    context_object_name = "products"
    paginate_by = 4

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