from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def home(request):
    # ყველა პროდუქტი ფასის ზრდადობით
    products = Product.objects.order_by("price")

    # მხოლოდ ის კატეგორიები, სადაც ერთი პროდუქტი მაინც არის
    categories = Category.objects.annotate(
        product_count=Count("products")
    ).filter(product_count__gt=0)

    context = {
        "products": products,
        "categories": categories,
    }
    return render(request, "store/home.html", context)


def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category).order_by("price")

    context = {
        "category": category,
        "products": products,
    }
    return render(request, "store/category.html", context)


def sale_products(request):
    # მხოლოდ ფასდაკლებული პროდუქტები
    products = Product.objects.filter(is_on_sale=True).order_by("price")
    return render(request, "store/sale.html", {"products": products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "store/product_detail.html", {"product": product})

