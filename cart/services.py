from django.db.models import Sum
from decimal import Decimal
from .models import UserCart, CartItems


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = UserCart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = UserCart.objects.get_or_create(
            session_key=request.session.session_key
        )
    return cart


def add_product_to_cart(cart, product, quantity):

    #Adds a product to a cart or increments quantity if it already exists.
    item, created = CartItems.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={
            "price": product.price,
            "quantity": quantity
        }
    )
    if not created:
        new_quantity = item.quantity + quantity

        if new_quantity > product.quantity:
            raise ValueError(
                "Total quantity exceeds available stock."
            )

        item.quantity = new_quantity
        item.save()
    return item


def remove_product_from_cart(cart, product_id):
    
    #Removes a product from the given cart.
    
    deleted, _ = CartItems.objects.filter(
        cart=cart,
        product_id=product_id
    ).delete()
    if deleted == 0:
        raise ValueError("Product not found in cart.")
    return True


def clear_cart(cart):
    
    #Removes all items from the given cart.
    
    CartItems.objects.filter(cart=cart).delete()


def get_cart_summary(cart):
    items = (
        CartItems.objects
        .select_related("product", "product__user")
        .filter(
            cart=cart,
            product__status="approved",
        )
    )

    total_quantity = items.aggregate(
        total=Sum("quantity")
    )["total"] or 0

    subtotal = sum(
    (item.price * item.quantity for item in items),
    Decimal("0.00")
)

    return {
        "id": cart.id,
        "items": items,
        "total_items": items.count(),
        "total_quantity": total_quantity,
        "subtotal": subtotal,
    }
