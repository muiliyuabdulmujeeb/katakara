from django.urls import path
from .views import AdminProductListView, ApproveProductView, CreateProductView, ProductDeleteView, ProductDetailView, ProductListView, ProductUpdateView, RejectProductView, CreateProductCategoryView

urlpatterns = [
    path("products/", CreateProductView.as_view(), name="create-product"),
    path("products/<uuid:id>/", ProductDetailView.as_view(), name="product-detail"),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("admin/products/", AdminProductListView.as_view(), name="admin-product-list"),
    path("products/<uuid:id>/", ProductUpdateView.as_view(), name="product-update"),
    path("products/<uuid:id>/", ProductDeleteView.as_view(), name="product-delete"),
    path("admin/products/<uuid:id>/approve/", ApproveProductView.as_view(), name="product-approve"),
    path("admin/products/<uuid:id>/reject/", RejectProductView.as_view(), name="product-reject"),
    path("admin/products/category", CreateProductCategoryView.as_view(), name= "create-product-category"),

]
