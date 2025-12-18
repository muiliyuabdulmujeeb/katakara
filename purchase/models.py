import uuid
from django.db import models
from product.models import Products


# Create your models here.

class Order(models.Model):
    STATUS_CHOICES =[
        ("paid", "Paid"),
        ("pending", "Pending"),
        ("not_paid", "Not Paid")
    ]
    id= models.UUIDField(primary_key=True, default= uuid.uuid4, editable= False)
    status= models.TextChoices(choices= STATUS_CHOICES, default= "not_paid")
    created_at= models.DateTimeField(auto_now_add= True)


class OrderItems(models.Model):
    id= models.UUIDField(primary_key= True, default= uuid.uuid4, editable= False)
    order= models.ForeignKey(Order, on_delete= models.CASCADE)
    product= models.ForeignKey(Products, on_delete= models.CASCADE)
    product_name = models.CharField(max_length= 200)
    product_price = models.DecimalField(max_digits= 10, decimal_places= 2)          #the price the product was listed
    quantity = models.IntegerField(default= 1)
    final_price_per_item = models.DecimalField(max_digits= 10, decimal_places= 2)   #useful if there's a discount on the product