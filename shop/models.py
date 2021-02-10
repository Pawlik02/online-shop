from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

    def get_profile_by_request(view_request):
        return Profile.objects.get(user=view_request.user.id)
    
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = self.name.replace(" ", "-")
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    slug = models.SlugField(max_length=100, blank=True, editable=False)
    available_quantity = models.DecimalField(max_digits=10, decimal_places=0, default=1)

    def save(self, *args, **kwargs):
        self.slug = self.name.replace(" ", "-")
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return "Category: "+self.category.__str__()+" | Product: "+self.name+" | Price: "+str(self.price)+" zł"+" | Id: "+str(self.id)

class Cart(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    
    def __str__(self):
        return "Id: "+str(self.id)+" | Cart - "+self.profile.user.username

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ordered_quantity = models.DecimalField(max_digits=10, decimal_places=0, default=1)

    class Meta:
        unique_together = ["cart", "product"]

    def __str__(self):
        return "Cart: "+self.cart.profile.user.username+" | Product: "+self.product.name+" | Quantity: "+str(self.ordered_quantity)+" | Total price: "+str(self.get_price())+" zł"
    
    def get_price(self):
        return self.ordered_quantity*self.product.price

class Order(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    address = models.CharField(max_length=150)
    email = models.EmailField(max_length=150)
    phone = models.CharField(max_length=12)

    class Status(models.IntegerChoices):
        NEW = 1
        IN_PROGRESS = 2
        SENT = 3
        ENDED = 4

    status = models.IntegerField(choices=Status.choices, default=1)

    def __str__(self):
        return "Order id: "+str(self.id)+" | User: "+self.profile.user.username+" | Cart id: "+str(self.cart.id)