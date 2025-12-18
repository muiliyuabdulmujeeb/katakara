import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager
from datetime import timedelta

# Create your models here.

def get_banned_user_expires_at():
    """Function to set the default time for expires_at field in BannedUser Model which is approximately 200 years in weeks"""
    return timezone.now() + timedelta(weeks= 10400)


class Role(models.Model):
    id= models.UUIDField(primary_key= True, default= uuid.uuid4, editable= False)
    name= models.CharField(max_length= 50)


class KatakaraBaseUserManager(BaseUserManager):
    """User manager to create user using first_name, last_name, email and password"""
    def create_user(self, first_name, last_name, email, password, is_active=True, **extra_fields):

        if not first_name:
            raise ValueError("First name cannot be blank")
        if not last_name:
            raise ValueError("Last name cannot be blank")
        if not email:
            raise ValueError("email cannot be blank")

        user = self.model(
            first_name= first_name,
            last_name= last_name,
            email= self.normalize_email(email=email),
            is_active= is_active,
            **extra_fields
        )
        user.set_password(password)
        user.save(using= self._db)
        return user
    
    """User manager to create super user using first_name, last_name, email and password"""
    def create_superuser(self, first_name, last_name, email, password, **extra_fields):
        user = self.create_user(first_name= first_name, last_name= last_name, email= email, password= password, **extra_fields)

        user.is_active = True
        user.is_staff = True
        user.is_superuser = True

        user.save(using= self._db)

        return user

class KatakaraUser(AbstractUser):
    id= models.UUIDField(primary_key= True, default= uuid.uuid4, editable= False)
    first_name= models.CharField(max_length= 50)
    last_name= models.CharField(max_length= 50)
    email= models.EmailField(unique= True)
    role= models.ManyToManyField(Role)

    objects= KatakaraBaseUserManager()

    USERNAME_FIELD= "email"
    REQUIRED_FIELDS= ["first_name", "last_name", "password"]

    def __str__(self):
        return self.get_full_name()

class BlacklistedTokens(models.Model):
    id= models.UUIDField(primary_key= True, default= uuid.uuid4, editable= False)
    user= models.ForeignKey(KatakaraUser, on_delete= models.CASCADE)
    token= models.CharField(max_length= 50)


    def __str__(self):
        return self.user__email
    
class BannedUser(models.Model):
    id= models.UUIDField(primary_key= True, default= uuid.uuid4, editable= False)
    user= models.ForeignKey(KatakaraUser, on_delete= models.CASCADE)
    banned_at= models.DateTimeField(auto_now_add= True)
    expires_at= models.DateTimeField(default= get_banned_user_expires_at)