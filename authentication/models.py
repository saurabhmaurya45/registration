from django.db import models

# Create your models here.

class signup(models.Model):
    email = models.CharField(max_length=255,primary_key=True)
    name = models.CharField(max_length=50)
    mobileno = models.IntegerField()
    password = models.CharField(max_length=20)

    def __str__(self):
        return self.name 