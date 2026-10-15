from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("shop/", views.shop, name="shop"),
    path("category/<int:category_id>/", views.category_detail, name="category_detail"),
    path("sale/", views.sale_products, name="sale"),
    path("product/add/", views.product_create, name="product_create"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
    path("product/<int:product_id>/edit/", views.product_update, name="product_update"),
    path("product/<int:product_id>/delete/", views.product_delete, name="product_delete"),
]