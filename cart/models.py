from django.db import models
import uuid
from katakara_auth.models import KatakaraUser
from product.models import Products

# Create your models here.

class UserCart(models.Model):
    id = models.UUIDField(primary_key= True, default= uuid.uuid4, editable= False)
    user = models.OneToOneField(KatakaraUser, on_delete= models.SET_NULL, null= True, blank= True)
    session_key = models.CharField(max_length= 40, null= True, blank= True)
    created_at = models.DateTimeField(auto_now_add= True)

class CartItems(models.Model):
    id = models.UUIDField(primary_key= True, default= uuid.uuid4, editable= False)
    cart_id = models.ForeignKey(UserCart, on_delete= models.CASCADE)
    product_id = models.ForeignKey(Products, on_delete= models.CASCADE)
    price = models.DecimalField(max_digits= 10, decimal_places= 2)
    quantity = models.IntegerField(default= 1)
    created_at = models.DateTimeField(auto_now_add= True)