from django.db import models

# Create your models here.

class User(models.Model):
    currentTab = models.FloatField()
    name = models.CharField(max_length=200)
    number = models.CharField(max_length=20)
    
class Tab(models.Model):
    tabber_id = models.IntegerField()
    tabbee_id = models.IntegerField()
    amount = models.IntegerField()
    date_tabbed = models.DateTimeField('date tabbed')

class Purchasable(models.Model):
    name = models.CharField(max_length=200)
    cost = models.FloatField()
    
