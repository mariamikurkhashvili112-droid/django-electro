from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("shop/", views.ShopView.as_view(), name="shop"),
    path("category/<int:category_id>/", views.CategoryDetailView.as_view(), name="category_detail"),
    path("sale/", views.SaleProductsView.as_view(), name="sale"),
    path("product/add/", views.ProductCreateView.as_view(), name="product_create"),
    path("product/<int:product_id>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("product/<int:product_id>/edit/", views.product_update, name="product_update"),
    path("product/<int:product_id>/delete/", views.product_delete, name="product_delete"),
]