from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
import re

# Create your models here.
class User(models.Model):
    UserID=models.AutoField(primary_key=True)
    username=models.CharField(max_length=250)
    password=models.CharField(max_length=250)


    # def clean(self):
    #     if not self.phone_number or not re.match('^\d{11}$', self.phone_number):
    #         raise ValidationError("Invalid phone number")

    # class Meta:
    #     constraints = [
    #         models.CheckConstraint(
    #             check=Q(phone_number__regex='^(\+?\d{1,4}[-\s]??)?\(?\d{1,3}\)?[-\s]??\d{1,4}[-\s]??\d{1,9}$'),
    #             name="valid_phone_number"),
    #     ]




class month_budget(models.Model):
    budget_id = models.AutoField(primary_key=True)
    UserID = models.ForeignKey('User', on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField()
    kind = models.CharField(max_length=10)
    budget_amount = models.DecimalField(max_digits=10,decimal_places=2)

    class Meta:
        indexes = [
            models.Index(fields=['UserID', 'year','month']),
        ]

class Bill(models.Model):
    id=models.AutoField(primary_key=True)
    UserID = models.ForeignKey('User', on_delete=models.CASCADE)
    name=models.CharField(max_length=32)
    income=models.IntegerField(max_length=32)
    note=models.CharField(max_length=32)
    number=models.FloatField()
    year=models.IntegerField(max_length=4)
    month=models.IntegerField(max_length=2)
    day=models.IntegerField(max_length=2)
    type=models.CharField(max_length=32)

class Clock_in(models.Model):
    id = models.AutoField(primary_key=True)
    UserID = models.ForeignKey('User', on_delete=models.CASCADE)
    year = models.IntegerField(max_length=10)
    month = models.IntegerField(max_length=10)
    day = models.IntegerField(max_length=10)
