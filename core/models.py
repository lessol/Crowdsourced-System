import uuid
from multiselectfield import MultiSelectField
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class passenger(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='passenger/avatars/', blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True)
    stripe_passenger_id = models.CharField(max_length=255, blank=True)
    stripe_payment_method_id = models.CharField(max_length=255, blank=True)
    stripe_card_last4 = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.get_full_name()

class driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self) :
        return self.user.get_full_name()

class VehicleType(models.Model):
    slug = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
        return self.name

class Spot(models.Model):
    CREATION_STATUS = 'creating'
    PROCESSING_STATUS = 'processing'
    DRIVER_EN_ROUTE = 'driver en route'
    PICKED_UP = 'picked up'
    DELIVERING = 'delivering'
    DELIVERED = 'delivered'
    COMPLETED_STATUS = 'completed'
    CANCELED_STATUS = 'canceled'
    
    STATUS = (
        (CREATION_STATUS, 'Creating'),
    (PROCESSING_STATUS, 'Processing'),
    (DRIVER_EN_ROUTE, 'Driver en route'),
    (PICKED_UP, 'Picked up'),
    (DELIVERING, 'Delivering'),
    (DELIVERED, 'Delivered'),
    (COMPLETED_STATUS, 'Completed'),
    (CANCELED_STATUS, 'Canceled'),
    )
   
    #Step1
    origin_point = models.CharField(max_length=255, blank=True)
    origin_lat = models.FloatField(default=0)
    origin_lng = models.FloatField(default=0)

    #Step2
    end_point = models.CharField(max_length=255, blank=True)
    end_lat = models.FloatField(default=0)
    end_lng = models.FloatField(default=0)

    # Step3
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    passenger = models.ForeignKey(passenger, on_delete=models.CASCADE, null=True)
    driver = models.ForeignKey(driver, on_delete=models.CASCADE, null=True, blank=True)
    description = models.CharField(max_length=255)
    Types_of_Vehicle = models.ForeignKey(VehicleType, on_delete=models.SET_NULL, null=True, blank=True)
    Number_of_Guest = models.IntegerField(default=0.0)
    photo = models.ImageField(upload_to='spot/photos/')
    status = models.CharField(max_length=20, choices=STATUS, default=CREATION_STATUS)
    created_at = models.DateTimeField(default=timezone.now)

    # Step 4
    duration = models.IntegerField(default=0)
    distance = models.FloatField(default=0)
    price = models.FloatField(default=0)


    #Extra Info
    origin_photo = models.ImageField(upload_to='spot/origin_photos/', null=True, blank=True)
    origin_at = models.DateTimeField(null=True, blank=True)
    
    end_photo = models.ImageField(upload_to='spot/end_photos/', null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return self.origin_point

class Transaction(models.Model):
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.stripe_payment_intent_id