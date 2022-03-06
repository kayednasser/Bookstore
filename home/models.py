from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Create your models here.

class Contact(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True)
    name = models.CharField(max_length=100,blank=True,null=True)
    email = models.EmailField(blank=True,null=True)
    message = models.TextField(blank=True,null=True)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

