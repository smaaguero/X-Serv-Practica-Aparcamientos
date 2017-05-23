from django.db import models

class UserData(models.Model):
    name = models.CharField(max_length=64)
    background = models.TextField()
    size = models.IntegerField()
    title = models.TextField()

class Parking(models.Model):
    idNumber = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    description = models.TextField()
    url = models.TextField()
    phoneNumber = models.TextField()
    mail = models.TextField()
    latitude = models.DecimalField(max_digits=20, decimal_places=17)
    longitude = models.DecimalField(max_digits=20, decimal_places=17)
    neighborhood = models.CharField(max_length=64)
    district = models.CharField(max_length=64)
    accessibility = models.BooleanField()
    numberOfComments = models.IntegerField()
    punctuation = models.IntegerField()

class Comment(models.Model):
    parking = models.ForeignKey('Parking', on_delete=models.CASCADE)
    content = models.TextField()

class Selected(models.Model):
    parking = models.ForeignKey('Parking', on_delete=models.CASCADE)
    userName = models.CharField(max_length=64)
    date = models.DateTimeField(auto_now_add=True, blank=True)
