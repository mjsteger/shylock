from django.db import models

# Create your models here.

class User(models.Model):
    currentTab = models.FloatField()
    name = models.CharField(max_length=200)
    number = models.CharField(max_length=20)
    text_preference = models.BooleanField()
    
class Tab(models.Model):
    tabber_name = models.CharField(max_length=200)
    tabbee_name = models.CharField(max_length=200)
    amount = models.FloatField()
    item = models.CharField(max_length=200)
    date_tabbed = models.DateTimeField('date tabbed')

class Purchasable(models.Model):
    name = models.CharField(max_length=200)
    cost = models.FloatField()
