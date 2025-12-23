import uuid
from django.db import models
from katakara_auth.models import KatakaraUser
from product.models import Products
from purchase.models import Order

# Create your models here.

class Disputes(models.Model):
    DISPUTE_STATUS = [
        ("resolved", "Resolved"),       #by the admin or buyer
        ("escalated", "Escalated"),     #by the buyer or seller
        ("pending", "Pending"),         #default value
        ("cancelled", "Cancelled"),     #by the buyer or admin
        ("acknowledged", "Acknowledged"),          #by the seller
        ("action_taken", "Action taken")    #by the seller
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

    class Meta:
        permissions = [
            ("create_dispute", "can create dispute"),
            ("view_self_disputes", "can view self disputes"),
            ("cancel_dispute", "can cancel dispute"),
            ("escalate_dispute", "can escalate dispute"),
            ("satisfy_dispute", "can get satisfied by the dispute"),     #buyer only permission that changes status to resolved
            ("acknowledge_dispute", "can acknowledge disputes"),
            ("respond_to_dispute", "can respond to dispute"),
            ("resolve_dispute", "can resolve dispute"),
            ("view_escalated_disputes", "can view escalated disputes"),
            ("resolve_escalated_disputes", "can resolve escalated disputes")
        ]