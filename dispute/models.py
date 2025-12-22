import uuid
from django.db import models
from katakara_auth.models import KatakaraUser
from product.models import Products
from purchase.models import Order

# Create your models here.

class Disputes(models.Model):
    DISPUTE_STATUS = [
        ("resolved", "Resolved"),
        ("escalated", "Escalated"),
        ("pending", "Pending"),
        ("cancelled", "Cancelled"),
        ("acknowledged", "Acknowledged"),
        ("action_taken", "Action taken")
    ]
    id= models.UUIDField(primary_key= True, default= uuid.uuid4, editable= False)
    user= models.ForeignKey(KatakaraUser, on_delete= models.SET_NULL, null= True, blank= True)
    session_key= models.CharField(max_length= 40, null= True, blank= True)
    order= models.ForeignKey(Order, on_delete= models.RESTRICT, null= True, blank= True)
    product= models.ForeignKey(Products, on_delete= models.RESTRICT, null= True, blank= True)
    title= models.CharField(max_length= 50)
    description= models.TextField()
    status = models.CharField(choices= DISPUTE_STATUS, default= "pending")
    resolved_by = models.ForeignKey(KatakaraUser, on_delete= models.SET_NULL, null= True, blank= True, related_name= "resolved_disputes")
    created_at = models.DateTimeField(auto_now_add= True)
    acknowledged_at = models.DateTimeField(null= True)
    resolved_at = models.DateTimeField(null= True)
    escalated_at = models.DateTimeField(null= True)
