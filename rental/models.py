from django.db import models
from django.contrib.auth.models import User

class Car(models.Model):
    category = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    number_plate = models.CharField(max_length=100)
    current_city = models.CharField(max_length=100)
    rent_per_hr = models.IntegerField()
    rent_history = models.JSONField(default=list)

class Rent(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    hours_requirement = models.IntegerField()
    total_payable_amt = models.IntegerField()

    


