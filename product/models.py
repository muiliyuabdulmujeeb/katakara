from django.db import models
import uuid
from katakara_auth.models import KatakaraUser

# Create your models here.

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, default="")
    is_active = models.BooleanField(default=True)

class Product(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending Approval"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("blacklisted", "Blacklisted"),
        ("deleted", "Deleted"),
]


    id = models.UUIDField(primary_key= True, default= uuid.uuid4, editable= False)
    user = models.ForeignKey(KatakaraUser, on_delete= models.CASCADE)
    name = models.CharField(max_length= 200)
    description= models.TextField(max_length= 500)
    category= models.ManyToManyField(Category)
    price = models.DecimalField(max_digits= 10, decimal_places= 2)
    quantity= models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
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

class Review(models.Model):
    id = models.UUIDField(primary_key= True, default= uuid.uuid4, editable= False)
    user = models.ForeignKey(KatakaraUser, on_delete= models.CASCADE)
    product = models.ForeignKey(Product, on_delete= models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at= models.DateTimeField(auto_now_add= True)

    class Meta:
        unique_together = ("user", "product")               #one user should be able to review a product only once
        permissions = [
            ("review_product", "can review a product"),     #can only review a product if they purchased the product
            ("edit_review", "can edit self review"),
            ("view_reviews", "can view all reviews for a product"),
            ("delete_any_review", "can delete any product review"),
        ]