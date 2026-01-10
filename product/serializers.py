from rest_framework import serializers
from .models import Product, Category


class ProductCreateSerializer(serializers.ModelSerializer):
    categories = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "quantity",
            "categories",
        ]
    def validate_categories(self, value):
        categories = Category.objects.filter(
            id__in=value,
            is_active=True
        )

        if categories.count() != len(value):
            raise serializers.ValidationError(
                "One or more categories are invalid or inactive."
            )

        return categories

    def create(self, validated_data):
        categories = validated_data.pop("categories")
        user = self.context["request"].user

        product = Product.objects.create(
            user=user,
            status="pending",
            **validated_data
        )

        product.category.set(categories)
        return product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]

class ProductDetailSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(source="category", many=True)
    seller = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "quantity",
            "status",
            "categories",
            "seller",
            "created_at",
        ]
    def get_seller(self, obj):
        return {
            "id": str(obj.user.id),
            "email": obj.user.email,
        }


class ProductListSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(
        source="category",
        many=True,
        read_only=True,
        slug_field="slug"
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "categories",
            "created_at",
        ]

        
class MyProductListSerializer(serializers.ModelSerializer):
    categories = serializers.SlugRelatedField(
        source="category",
        many=True,
        read_only=True,
        slug_field="slug"
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "status",
            "categories",
            "created_at",
        ]


class AdminProductListSerializer(serializers.ModelSerializer):
    seller = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "status",
            "seller",
            "created_at",
        ]

    def get_seller(self, obj):
        return {
            "id": str(obj.user.id),
            "email": obj.user.email,
        }

class ProductUpdateSerializer(serializers.ModelSerializer):
    categories = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "quantity",
            "categories",
        ]

    def validate(self, attrs):
        product = self.instance

        if product.status in ["approved", "blacklisted"]:
            raise serializers.ValidationError(
                "This product cannot be edited in its current state."
            )

        return attrs

    def update(self, instance, validated_data):
        categories = validated_data.pop("categories", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if categories is not None:
            instance.category.set(
                Category.objects.filter(id__in=categories, is_active=True)
            )

        instance.status = "pending"
        instance.save()
        return instance

class ProductDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = []

    def validate(self, attrs):
        product = self.instance

        if product.status in ["approved", "blacklisted"]:
            raise serializers.ValidationError(
                "This product cannot be deleted in its current state."
            )

        return attrs
    
    def update(self, instance, validated_data):
        instance.status = "deleted"
        instance.save()
        return instance

class ProductModerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = []

    def validate(self, attrs):
        product = self.instance
        new_status = self.context.get("new_status")

        if new_status == "blacklisted":
            if product.status != "approved":
                raise serializers.ValidationError(
                    "Only approved products can be blacklisted."
                )

        elif product.status != "pending":
            raise serializers.ValidationError(
                "Only pending products can be moderated."
            )

        return attrs


    def update(self, instance, validated_data):
        new_status = self.context.get("new_status")

        if not new_status:
            raise RuntimeError("Moderation status not provided")

        instance.status = new_status
        instance.save()
        return instance

class CreateProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name", "slug"]

    def validate(self, attrs):
        name = attrs.get("name")
        slug = attrs.get("slug")

        if Category.objects.filter(name= name).exists():
            raise serializers.ValidationError("Category already exist")
        
        if Category.objects.filter(slug= slug).exists():
            raise serializers.ValidationError("Slug name already exist for a category")
        
        return attrs
    
    def create(self, validated_data):

        return Category.objects.create(**validated_data)