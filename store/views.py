from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm
from .models import Category, Product


def home(request):
    # All products ordered by price (ascending)
    products = Product.objects.order_by("price")

    # Only categories that contain at least one product
    categories = Category.objects.annotate(
        product_count=Count("products")
    ).filter(product_count__gt=0)

    context = {
        "products": products,
        "categories": categories,
    }
    return render(request, "store/home.html", context)


def shop(request):
    products = Product.objects.order_by("price")
    categories = Category.objects.annotate(product_count=Count("products"))

    context = {
        "products": products,
        "categories": categories,
    }
    return render(request, "store/shop.html", context)


def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category).order_by("price")

    context = {
        "category": category,
        "products": products,
    }
    return render(request, "store/category.html", context)


def sale_products(request):
    # Only products that are on sale
    products = Product.objects.filter(is_on_sale=True).order_by("price")
    return render(request, "store/sale.html", {"products": products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "store/product_detail.html", {"product": product})


def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            return redirect("product_detail", product_id=product.id)
    else:
        form = ProductForm()

    context = {
        "form": form,
        "title": "Add Product",
    }
    return render(request, "store/product_form.html", context)


def product_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
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


def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product.delete()
        return redirect("shop")

    return render(request, "store/product_confirm_delete.html", {"product": product})