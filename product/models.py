from django.db import models
import uuid
from katakara_auth.models import KatakaraUser

# Create your models here.

class Category(models.Model):
    CATEGORY_NAMES = [
        ("general", "General"),
        ("electronics-and-technology", "Electronics & Technology"),
        ("fashion-and-beauty", "Fashion & Beauty"),
        ("home-and-living", "Home & Living"),
        ("sports-and-outdoors", "Sports & Outdoors"),
        ("health-and-personal-care", "Health & Personal Care"),
        ("baby-kids-and-toys", "Baby Kids & Toys"),
        ("groceries-and-essentials", "Groceries & Essentials"),
        ("automotive-and-industrial", "Automotive & Industrial"),
        ("books-and-stationery", "Books & Stationery"),
        ("gaming-and-entertainment", "Gaming & Entertainment"),
        ("pet-supplies", "Pet Supplies"),
        ("office-and-business", "Office & Business"),
        ("art-and-craft", "Art & Craft"),
        ("jewelry-and-accessories", "Jewelry & Accessories"),
        ("appliances", "Appliances"),
        ("hardware-and-diy", "Hardware & DIY"),
        ("music-and-instruments", "Music & Instruments")

    ]

    id = models.UUIDField(primary_key= True, default= uuid.uuid4, editable= False)
    name = models.CharField(max_length= 200, choices= CATEGORY_NAMES, default= "general")

class Products(models.Model):
    id = models.UUIDField(primary_key= True, default= uuid.uuid4, editable= False)
    user = models.ForeignKey(KatakaraUser, on_delete= models.CASCADE)
    name = models.CharField(max_length= 200)
    description= models.TextField(max_length= 500)
    category= models.ManyToManyField(Category)
    price = models.DecimalField(max_digits= 10, decimal_places= 2)
    quantity= models.IntegerField(default=0)
    is_approved = models.BooleanField(default= False)
    created_at= models.DateTimeField(auto_now_add= True)

    class Meta:
        permissions = [
            ("list_products", "list all products"),
            ("list_approved_products", "list only approved products"),
            ("list_unapproved_products", "list only unapproved products"),
            ("view_product_details", "view the details of a product"),
            ("create_product", "can create product"),
            ("update_product_details", "can update product details"),
            ("approve_product", "can approve products"),
            ("disprove_product", "can disprove products"),

        ]

class Review(models.Model):             #one user should be able to review a product only once
    id = models.UUIDField(primary_key= True, default= uuid.uuid4, editable= False)
    user = models.ForeignKey(KatakaraUser, on_delete= models.CASCADE)
    product = models.ForeignKey(Products, on_delete= models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at= models.DateTimeField(auto_now_add= True)

    class Meta:
        permissions = [
            ("review_product", "can review a product"),     #can only review a product if they purchased the product
            ("edit review", "can edit self review"),
            ("view_reviews", "can view all reviews for a product"),
            ("delete_any_review", "can delete any product review"),
        ]