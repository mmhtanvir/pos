from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    part_name = models.CharField(max_length=100)
    part_number = models.CharField(max_length=50, unique=True)
    compatibility = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    condition = models.CharField(max_length=50, choices=[('new', 'New'), ('used', 'Used')])
    warranty = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    stock_quantity = models.PositiveIntegerField(default=0)
    availability_status = models.BooleanField(default=True)
    image = models.ImageField(upload_to='static/products/', blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.part_name} ({self.part_number})"

class Customer(models.Model):
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return f"{self.full_name} ({self.phone})"

class Sale(models.Model):    
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    sale_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Sale #{self.id} - {self.customer.full_name}"   