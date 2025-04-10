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
    SALE_TYPE_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid')
    ]
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('online_payment', 'Bkash/Nagad/Upay'),
        ('transfer', 'Bank Transfer'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    sale_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    sale_type = models.CharField(max_length=7, choices=SALE_TYPE_CHOICES)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Sale #{self.id} - {self.customer.full_name if self.customer else 'Walk-in'}"    

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=100, default='Deleted Product')
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        if self.product:
            self.product_name = self.product.part_name
            self.product_price = self.product.price
        self.subtotal = self.product_price * self.quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name} in Sale #{self.sale.id}"