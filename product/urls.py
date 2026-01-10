from django.urls import path
from .views import AdminProductListView, ApproveProductView, BlacklistProductView, CreateProductView, MyProductListView, ProductDeleteView, ProductDetailView, ProductListView, ProductUpdateView, RejectProductView, CreateProductCategoryView

urlpatterns = [
    path("products/create/", CreateProductView.as_view(), name="create-product"),
    path("products/<uuid:id>/", ProductDetailView.as_view(), name="product-detail"),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/me/", MyProductListView.as_view(), name="my-product-list"),
    path("products/admin/", AdminProductListView.as_view(), name="admin-product-list"),
    path("products/<uuid:id>/update/", ProductUpdateView.as_view(), name="product-update"),
    path("products/<uuid:id>/delete/", ProductDeleteView.as_view(), name="product-delete"),
    path("products/<uuid:id>/approve/", ApproveProductView.as_view(), name="product-approve"),
    path("products/<uuid:id>/reject/", RejectProductView.as_view(), name="product-reject"),
    path("products/category/", CreateProductCategoryView.as_view(), name= "create-product-category"),
    path("products/<uuid:id>/blacklist/", BlacklistProductView.as_view(), name="product-blacklist"),
]
