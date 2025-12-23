import uuid
from django.db import models
from product.models import Products
from katakara_auth.models import KatakaraUser


# Create your models here.

class Order(models.Model):
    STATUS_CHOICES =[
        ("paid", "Paid"),
        ("pending", "Pending"),
        ("not_paid", "Not Paid"),
        ("saved", "Saved")
    ]
    id= models.UUIDField(primary_key=True, default= uuid.uuid4, editable= False)
    status= models.CharField(choices= STATUS_CHOICES, default= "not_paid")
    created_at= models.DateTimeField(auto_now_add= True)

    class Meta:
        permissions = [
            ("create_order", "can create order"),
            ("cancel_order", "can cancel order"),
            ("save_order", "can save order"),
            ("view_all_orders", "can view all orders"),
            ("view_order_item", "can view order item"),
            ("edit_order", "can edit order"),
            ("pay_order", "can pay for order"),
            ("confirm_payment", "can confirm order payment"),
            ("generate_reciept", "can generate reciept for order"),
            ("deliver_order", "can_deliver_order"),
            ("view_delivery_details", "can view delivery details"),
            ("recieve_order_delivery", "can recieve order delivery"),
        ]

class OrderItems(models.Model):
    id= models.UUIDField(primary_key= True, default= uuid.uuid4, editable= False)
    order= models.ForeignKey(Order, on_delete= models.CASCADE)
    product= models.ForeignKey(Products, on_delete= models.CASCADE)
    product_name = models.CharField(max_length= 200)
    product_price = models.DecimalField(max_digits= 10, decimal_places= 2)          #the price the product was listed
    quantity = models.IntegerField(default= 1)
    final_price_per_item = models.DecimalField(max_digits= 10, decimal_places= 2)   #useful if there's a discount on the product


class OrderDelivery(models.Model):
    STATUS_CHOICES = [
        ("processing", "Processing"),
        ("en-route", "En-route"),
        ("delivered", "Delivered"),
        ("not_recieved", "Not recieved"),
        ("cancelled", "Cancelled")
    ]

    id= models.UUIDField(primary_key=True, default= uuid.uuid4, editable= False)
    order= models.ForeignKey(Order, on_delete= models.RESTRICT)
    user = models.ForeignKey(KatakaraUser, on_delete= models.SET_NULL, null= True, blank= True)
    session_key = models.CharField(max_length= 40, null= True, blank= True)
    address = models.TextField()
    phone = models.CharField(max_length= 20)
    status= models.CharField(choices= STATUS_CHOICES, default= "not_paid")