from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView, RetrieveUpdateAPIView, DestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .serializers import AdminProductListSerializer, ProductCreateSerializer, ProductDeleteSerializer, ProductDetailSerializer, ProductListSerializer, ProductModerationSerializer, ProductUpdateSerializer, CreateProductCategorySerializer
from .permissions import IsAdminOrSuperAdmin, IsProductOwner, IsSeller
from .models import Product
from .pagination import ProductPagination


class CreateProductView(CreateAPIView):
    serializer_class = ProductCreateSerializer
    permission_classes = [IsAuthenticated, IsSeller]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class ProductDetailView(RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user

        base_qs = Product.objects.select_related("user").prefetch_related("category")

        if user.is_authenticated:
            if user.is_superuser or user.groups.filter(name="admin").exists():
                return base_qs

            return base_qs.filter(
                Q(status="approved") | Q(user=user)
            )

        return base_qs.filter(status="approved")


class ProductListView(ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    pagination_class = ProductPagination

    def get_queryset(self):
        queryset = Product.objects.filter(status="approved")

        category = self.request.query_params.get("category")
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        search = self.request.query_params.get("search")

        if category:
            queryset = queryset.filter(category__slug=category)

        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        return queryset.order_by("-created_at")

class AdminProductListView(ListAPIView):
    serializer_class = AdminProductListSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    def get_queryset(self):
        status_param = self.request.query_params.get("status", "pending")

        allowed_statuses = {
            "pending",
            "approved",
            "rejected",
            "blacklisted",
        }

        if status_param not in allowed_statuses:
            status_param = "pending"

        return (
            Product.objects
            .select_related("user")
            .filter(status=status_param)
            .order_by("created_at")
        )

class ProductUpdateView(RetrieveUpdateAPIView):
    serializer_class = ProductUpdateSerializer
    permission_classes = [IsAuthenticated, IsProductOwner]
    lookup_field = "id"

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)

class ProductDeleteView(DestroyAPIView):
    serializer_class = ProductDeleteSerializer
    permission_classes = [IsAuthenticated, IsProductOwner]
    lookup_field = "id"

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        serializer = self.get_serializer(instance)
        serializer.is_valid(raise_exception=True)
        serializer.save()

class ApproveProductView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, id):
        product = get_object_or_404(Product, id=id)

        serializer = ProductModerationSerializer(
            product,
            data={},
            context={"new_status": "approved"}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Product approved."},
            status=status.HTTP_200_OK
        )

class RejectProductView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, id):
        product = get_object_or_404(Product, id=id)

        serializer = ProductModerationSerializer(
            product,
            data={},
            context={"new_status": "rejected"}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Product rejected."},
            status=status.HTTP_200_OK
        )

class CreateProductCategoryView(CreateAPIView):
    permission_classes = [IsAdminOrSuperAdmin]
    serializer_class = CreateProductCategorySerializer


class BlacklistProductView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def post(self, request, id):
        product = get_object_or_404(Product, id=id)

        serializer = ProductModerationSerializer(
            product,
            data={},
            context={"new_status": "blacklisted"}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Product has been blacklisted."},
            status=status.HTTP_200_OK
        )
