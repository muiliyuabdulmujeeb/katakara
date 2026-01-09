from django.urls import path
from .views import ConfirmPaymentBySellerAPIView, CreateOrderFromCartView, DeleteOrderView, InitiatePaymentView, MyOrdersView, OrderDetailView, RejectPaymentBySellerAPIView, SaveOrderView, ConfirmPaymentByBuyerAPIView


urlpatterns = [
    path("orders/from-cart/", CreateOrderFromCartView.as_view(), name="create-order-from-cart"),
    path("orders/", MyOrdersView.as_view(), name="my-orders"),
    path("orders/<uuid:order_id>/", OrderDetailView.as_view(), name="order-detail"),
    path("orders/<uuid:order_id>/save/", SaveOrderView.as_view()),
    path("orders/<uuid:order_id>/delete/", DeleteOrderView.as_view()),
    path("orders/<uuid:order_id>/initiate-payment/", InitiatePaymentView.as_view()),
    path("orders/<uuid:order_id>/confirm-payment/", ConfirmPaymentByBuyerAPIView.as_view(), name="buyer-confirm-payment"),
    path("orders/<uuid:order_id>/confirm-payment-admin/", ConfirmPaymentBySellerAPIView.as_view(), name="seller-confirm-payment"),
    path("orders/<uuid:order_id>/reject-payment/", RejectPaymentBySellerAPIView.as_view(), name="seller-reject-payment"),
]
