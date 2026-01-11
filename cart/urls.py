from django.urls import path
from .views import AddToCartView, ClearCartView, RemoveFromCartView, ViewCartView


urlpatterns = [
    path("cart/items/", AddToCartView.as_view(), name="add-to-cart"),
    path("cart/items/<uuid:product_id>/", RemoveFromCartView.as_view(), name="remove-from-cart"),
    path("cart/clear/", ClearCartView.as_view(), name="clear-cart"),
    path("cart/", ViewCartView.as_view(), name="view-cart"),
]
