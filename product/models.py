from django.db import models
import uuid
from katakara_auth.models import KatakaraUser

# Create your models here.

class Category(models.Model):
    CATEGORY_NAMES = [
        ("general", "General")
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
    created_by = models.ForeignKey(KatakaraUser, on_delete= models.CASCADE)
    name = models.CharField(max_length= 200, unique= True)
    description= models.TextField(max_length= 500)
    category= models.ManyToManyField(Category)
    price = models.DecimalField(max_digits= 10, decimal_places= 2)
    quantity= models.IntegerField(default=0)
    created_at= models.DateTimeField(auto_now_add= True)

class Review(models.Model):
    id = models.UUIDField(primary_key= True, default= uuid.uuid4, editable= False)
    created_by = models.ForeignKey(KatakaraUser, on_delete= models.CASCADE)
    product = models.ForeignKey(Products, on_delete= models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at= models.DateTimeField(auto_now_add= True)