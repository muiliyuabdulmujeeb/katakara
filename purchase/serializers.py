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

class BuyerPaymentConfirmationSerializer(serializers.Serializer):
    def validate(self, attrs):
        order = self.context["order"]

        if order.status != "awaiting_payment":
            raise serializers.ValidationError(
                "This order is not awaiting payment."
            )

        return attrs

    def save(self):
        order = self.context["order"]
        order.status = "payment_pending"
        order.save(update_fields=["status"])
        return order


class SellerConfirmPaymentSerializer(serializers.Serializer):
    def validate(self, attrs):
        order = self.context["order"]

        if order.status != "payment_pending":
            raise serializers.ValidationError(
                "Order is not awaiting payment confirmation."
            )

        return attrs

    def save(self):
        order = self.context["order"]
        order.status = "paid"
        order.save(update_fields=["status"])
        return order


class SellerRejectPaymentSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        order = self.context["order"]

        if order.status != "payment_pending":
            raise serializers.ValidationError(
                "Order is not awaiting payment confirmation."
            )

        return attrs

    def save(self):
        order = self.context["order"]
        order.status = "awaiting_payment"
        order.save(update_fields=["status"])
        return order
