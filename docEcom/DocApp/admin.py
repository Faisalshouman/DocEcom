from django.contrib import admin
from .models import Product , Cart , CartItem , Order , OrderItem 

# Register your models here.

admin.site.register([Product , Cart , CartItem , Order , OrderItem ])