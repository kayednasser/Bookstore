from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    author = models.CharField(max_length=500,blank=True)
    price = models.IntegerField(blank=True)
    image = models.ImageField(upload_to = 'media') 
    rating = models.IntegerField(default=00)
    on_offer = models.BooleanField(default=False)
    pre_discount_price = models.IntegerField(default=00,blank=True)
    stock = models.IntegerField(default=1,blank=True)

    def __str__(self):
        return self.name

   

class Cart(models.Model):
    user  = models.ForeignKey(User,on_delete=models.CASCADE)
    book = models.ForeignKey(Book,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=00)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f'{self.user}______{self.book}'

   
class Order(models.Model):
    user  = models.ForeignKey(User,on_delete=models.CASCADE)
    book = models.ForeignKey(Book,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=00)
    full_name = models.CharField(max_length=100,blank=True)
    city = models.CharField(max_length=100,blank=True)
    address = models.TextField(blank=True)
    landmark = models.CharField(max_length=300,blank=True)
    address_type = models.CharField(max_length=100,blank=True)
    phone = models.IntegerField(default=00, blank=True)


    ORDER_STATUS = (
        ('Ordered', 'Ordered'),
        ('Shipped', 'Shipped'),
        ('Out for delivery', 'Out for delivery'),
        ('Delivered', 'Delivered'),
    )

    status = models.CharField(
        max_length=100,
        choices=ORDER_STATUS,
        blank=True,
        default='Ordered'
    )

    rated  = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=now)

    class Meta:
        ordering = ['-status']

    



class Feedback(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    book = models.ForeignKey(Book,on_delete=models.CASCADE)
    rating = models.IntegerField(default=00)
    comment = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=now)


    def __str__(self):
        return f'{self.user}___{self.book}'

   

class Recommendation(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    book = models.ForeignKey(Book,on_delete=models.CASCADE)

    def __str__(self):
        return f'"{self.user}"  is recommended  "{self.book}"  book'
