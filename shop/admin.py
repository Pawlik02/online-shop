from django.contrib import admin
from .models import Profile, Category, Product, Cart, CartItem, Order

admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)