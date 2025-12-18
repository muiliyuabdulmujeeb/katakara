import uuid
from django.db import models
from katakara_auth.models import KatakaraUser
from product.models import Products

# Create your models here.

class Disputes(models.Model):
    DISPUTE_STATUS = [
        ("resolved", "Resolved"),
        ("escalated", "Escalated"),
        ("pending", "Pending"),
        ("cancelled", "Cancelled")
    ]
    id= models.UUIDField(primary_key= True, default= uuid.uuid4, editable= False)
    user= models.ForeignKey(KatakaraUser, on_delete= models.SET_NULL, null= True, blank= True)
    session_key= models.CharField(max_length= 40, null= True, blank= True)
    product= models.ForeignKey(Products, on_delete= models.RESTRICT)
    title= models.CharField(max_length= 50)
    description= models.TextField()
    status = models.TextChoices(choices= DISPUTE_STATUS, default= "pending")
    created_at = models.DateTimeField(auto_now_add= True)
