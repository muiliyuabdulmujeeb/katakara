from rest_framework import serializers
from .models import CartItems
from product.models import Product

class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(
                id=value,
                status="approved"
            )
        except Product.DoesNotExist:
            raise serializers.ValidationError(
                "Product is not available for purchase."
            )

        self.product = product
        return value

    def validate(self, attrs):
        quantity = attrs["quantity"]
        product = self.product

        if quantity > product.quantity:
            raise serializers.ValidationError(
                "Requested quantity exceeds available stock."
            )

        return attrs

class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItems
        fields = [
            "id",
            "product",
            "quantity",
            "price",
            "line_total",
        ]

    def get_product(self, obj):
        product = obj.product_id
        return {
            "id": product.id,
            "name": product.name,
            "price": str(product.price),
            "seller": product.seller.username,
        }

    def get_line_total(self, obj):
        return str(obj.price * obj.quantity)


class CartSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    items = CartItemSerializer(many=True)
    total_items = serializers.IntegerField()
    total_quantity = serializers.IntegerField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
