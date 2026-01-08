from django.db import transaction
from django.utils import timezone

from cart.models import UserCart, CartItems
from product.models import Product
from .models import Order, OrderItems

def get_active_cart(request):
    if request.user.is_authenticated:
        return UserCart.objects.filter(
            user=request.user,
            is_active=True
        ).first()
    return UserCart.objects.filter(
        session_key=request.session.session_key,
        is_active=True
    ).first()

@transaction.atomic
def create_order_from_cart(request):
    cart = get_active_cart(request)

    if not cart:
        raise ValueError("No active cart found.")
    cart_items = CartItems.objects.select_related(
        "product", "seller"
    ).filter(cart=cart)

    if not cart_items.exists():
        raise ValueError("Cart is empty.")
    for item in cart_items:
        if item.product.status != "approved":
            raise ValueError(f"{item.product.name} is not available.")

        if item.quantity > item.product.quantity:
            raise ValueError(
                f"Insufficient stock for {item.product.name}."
            )
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_key=None if request.user.is_authenticated else request.session.session_key,
        status="draft",
        source_cart=cart
    )
    for item in cart_items:
        OrderItems.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            product_price=item.price,
            quantity=item.quantity,
            final_price_per_item=item.price,
        )
    cart.is_active = False
    cart.save(update_fields=["is_active"])

    cart_items.delete()
    return order


def get_user_orders(request):
    if request.user.is_authenticated:
        return Order.objects.filter(user=request.user)
    return Order.objects.filter(
        session_key=request.session.session_key
    )

def get_user_order_by_id(request, order_id):
    qs = get_user_orders(request)
    return qs.filter(id=order_id).first()

def save_order(order):
    if order.status != "draft":
        raise ValueError("Only draft orders can be saved.")

    order.status = "saved"
    order.save(update_fields=["status"])
    return order

def delete_order(order):
    if order.status not in ["draft", "saved"]:
        raise ValueError("Only draft or saved orders can be deleted.")

    order.delete()

def get_order_for_request(request, order_id):
    qs = Order.objects.filter(id=order_id)

    if request.user.is_authenticated:
        return qs.filter(user=request.user).first()

    if request.session.session_key:
        return qs.filter(session_key=request.session.session_key).first()

    return None

from purchase.models import Order, OrderItems

def initiate_payment(order):
    if order.status != "saved":
        raise ValueError("Only saved orders can initiate payment.")

    if not OrderItems.objects.filter(order=order).exists():
        raise ValueError("Order has no items.")

    order.status = "awaiting_payment"
    order.save(update_fields=["status"])

    return order
