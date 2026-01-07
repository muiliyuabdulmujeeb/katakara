from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import AddToCartSerializer, CartSerializer
from .services import get_cart_summary, get_or_create_cart, add_product_to_cart, remove_product_from_cart, clear_cart


class AddToCartView(APIView):
    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = get_or_create_cart(request)
        try:
            item = add_product_to_cart(
                cart=cart,
                product=serializer.product,
                quantity=serializer.validated_data["quantity"]
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {
                "detail": "Product added to cart successfully.",
                "item_id": item.id,
                "quantity": item.quantity
            },
            status=status.HTTP_201_CREATED
        )

class RemoveFromCartView(APIView):
    def delete(self, request, product_id):
        cart = get_or_create_cart(request)
        try:
            remove_product_from_cart(cart, product_id)
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"detail": "Product removed from cart."},
            status=status.HTTP_200_OK
        )

class ClearCartView(APIView):
    def delete(self, request):
        cart = get_or_create_cart(request)
        clear_cart(cart)
        return Response(
            {"detail": "Cart cleared successfully."},
            status=status.HTTP_200_OK
        )


class ViewCartView(APIView):
    def get(self, request):
        cart = get_or_create_cart(request)
        cart_data = get_cart_summary(cart)
        serializer = CartSerializer(cart_data)
        return Response(serializer.data)
