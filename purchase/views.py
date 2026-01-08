from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status

from .serializers import CreateOrderFromCartSerializer, OrderListSerializer
from .services import create_order_from_cart, delete_order, get_order_for_request, get_user_order_by_id, get_user_orders, initiate_payment, save_order


class CreateOrderFromCartView(APIView):
    def post(self, request):
        serializer = CreateOrderFromCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = create_order_from_cart(request)
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {
                "order_id": str(order.id),
                "status": order.status,
                "created_at": order.created_at,
            },
            status=status.HTTP_201_CREATED
        )

class MyOrdersView(APIView):
    def get(self, request):
        orders = get_user_orders(request).order_by("-created_at")
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class OrderDetailView(APIView):
    def get(self, request, order_id):
        order = get_user_order_by_id(request, order_id)
        if not order:
            return Response(
                {"detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
            )

class SaveOrderView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, order_id):
        order = get_order_for_request(request, order_id)

        if not order:
            return Response(
                {"detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            save_order(order)
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"detail": "Order saved successfully."},
            status=status.HTTP_200_OK
        )


class DeleteOrderView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def delete(self, request, order_id):
        order = get_order_for_request(request, order_id)

        if not order:
            return Response(
                {"detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            delete_order(order)
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"detail": "Order deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )

class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, order_id):
        order = get_order_for_request(request, order_id)

        if not order:
            return Response(
                {"detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            initiate_payment(order)
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "detail": "Payment initiated. Awaiting payment.",
                "order_status": order.status
            },
            status=status.HTTP_200_OK
        )