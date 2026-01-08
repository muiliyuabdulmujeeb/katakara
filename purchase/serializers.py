from rest_framework import serializers
from .models import OrderItems, Order, OrderDelivery


class CreateOrderFromCartSerializer(serializers.Serializer):
    confirm = serializers.BooleanField(default=True)

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItems
        fields = [
            "id",
            "product_name",
            "product_price",
            "final_price_per_item",
            "quantity",
        ]

class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "created_at",
        ]

class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        source="orderitems_set",
        many=True,
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "created_at",
            "items",
        ]


class OrderActionSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()


class InitiatePaymentSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
