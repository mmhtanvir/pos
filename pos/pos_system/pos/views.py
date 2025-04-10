from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotAllowed
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from .models import Product, Sale, Customer, Category, Brand, SaleItem

#dashboard
def dashboard(request):
    today = timezone.now().date()
    
    weekly_sales = Sale.objects.filter(
        sale_date__gte=today - timedelta(days=7)
    ).aggregate(total_sales=Sum('total_price'))['total_sales'] or 0
    
    # Get products with stock less than 3 (you can adjust this threshold)
    low_stock_threshold = 3
    low_stock = Product.objects.filter(stock_quantity__lt=low_stock_threshold).order_by('stock_quantity')[:5]
    low_stock_count = low_stock.count()
    
    context = {
        'product_count': Product.objects.count(),
        'sale_count': Sale.objects.count(),
        'customer_count': Customer.objects.count(),
        'recent_sales': Sale.objects.order_by('-sale_date')[:5],
        'weekly_sales': weekly_sales,
        'low_stock': low_stock,
        'low_stock_count': low_stock_count,
        'low_stock_threshold': low_stock_threshold,
    }
    return render(request, 'index.html', context)

# Product Views
@transaction.atomic
def create_product(request):
    if request.method == 'POST':
        try:
            # Get form data
            part_name = request.POST.get('part_name')
            part_number = request.POST.get('part_number')
            compatibility = request.POST.get('compatibility', '')
            description = request.POST.get('description', '')
            condition = request.POST.get('condition')
            warranty = request.POST.get('warranty', '')
            price = request.POST.get('price')
            discount = request.POST.get('discount', 0)
            stock_quantity = request.POST.get('stock_quantity')
            availability_status = request.POST.get('availability_status') == 'on'
            image = request.FILES.get('image')
            category_id = request.POST.get('category')
            brand_id = request.POST.get('brand')

            # Create product
            product = Product.objects.create(
                part_name=part_name,
                part_number=part_number,
                compatibility=compatibility,
                description=description,
                condition=condition,
                warranty=warranty,
                price=price,
                discount=float(discount),
                stock_quantity=int(stock_quantity),
                availability_status=availability_status,
                image=image,
                category_id=category_id if category_id else None,
                brand_id=brand_id if brand_id else None
            )

            messages.success(request, 'Product created successfully!')
            return redirect('product_list')
        except Exception as e:
            messages.error(request, f'Error creating product: {str(e)}')
            return redirect('product_list')
    return HttpResponseNotAllowed(['POST'])

@transaction.atomic
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        try:
            # Update product fields
            product.part_name = request.POST.get('part_name')
            product.part_number = request.POST.get('part_number')
            product.compatibility = request.POST.get('compatibility', '')
            product.description = request.POST.get('description', '')
            product.condition = request.POST.get('condition')
            product.warranty = request.POST.get('warranty', '')
            product.price = float(request.POST.get('price'))
            product.discount = float(request.POST.get('discount', 0))
            product.stock_quantity = int(request.POST.get('stock_quantity'))
            product.availability_status = request.POST.get('availability_status') == 'on'
            
            # Update category and brand
            category_id = request.POST.get('category')
            brand_id = request.POST.get('brand')
            product.category_id = category_id if category_id else None
            product.brand_id = brand_id if brand_id else None
            
            # Update image if provided
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            
            product.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_list')
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
            return redirect('product_list')
    return HttpResponseNotAllowed(['POST'])

@transaction.atomic
def delete_product(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)
            SaleItem.objects.filter(product=product).update(product=None)
            product.delete()
            
            messages.success(request, 'Product deleted')
            return redirect('product_list')
            
        except Exception as e:
            messages.error(request, f'Error deleting product: {str(e)}')
            return redirect('product_list')
    return HttpResponseNotAllowed(['POST'])

def product_list(request):
    search_query = request.GET.get('q', '').strip()
    products = Product.objects.all()
    
    if search_query:
        products = products.filter(
            Q(part_name__icontains=search_query) |
            Q(part_number__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    return render(request, 'product.html', {
        'products': products,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
        'search_query': search_query
    })

# Sale Views
@transaction.atomic
def create_sale(request):
    if request.method == 'POST':
        try:
            # Handle customer
            customer_name = request.POST.get('customer')
            phone = request.POST.get('phone', '0000000000')
            customer = None
            if customer_name:
                customer, _ = Customer.objects.get_or_create(
                    phone=phone if phone else '0000000000',
                    defaults={'full_name': customer_name}
                )
            
            # Create sale
            sale = Sale.objects.create(
                customer=customer,
                payment_method=request.POST.get('payment_method', 'cash'),
                sale_type=request.POST.get('sale_type'),
                total_price=0
            )
            
            # Process sale items
            product_ids = request.POST.getlist('products')
            quantities = request.POST.getlist('quantities')
            total_price = 0
            
            for product_id, quantity in zip(product_ids, quantities):
                if not product_id or not quantity:
                    continue
                
                product = Product.objects.get(id=product_id)
                quantity = int(quantity)
                
                if product.stock_quantity < quantity:
                    raise ValueError(f"Not enough stock for {product.part_name}")
                
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    product_name=product.part_name,
                    product_price=product.price,
                    quantity=quantity,
                    subtotal=product.price * quantity
                )
                
                product.stock_quantity -= quantity
                product.save()
                total_price += product.price * quantity
            
            sale.total_price = total_price
            sale.save()
            messages.success(request, f'Sale #{sale.id} created successfully!')
            return redirect('sale_list')
        except Exception as e:
            messages.error(request, f'Error creating sale: {str(e)}')
            return redirect('sale_list')
    return redirect('sale_list')

@transaction.atomic
def update_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    if request.method == 'POST':
        try:
            # Update customer info
            customer_name = request.POST.get('customer')
            phone = request.POST.get('phone', '0000000000')
            if customer_name:
                if sale.customer:
                    sale.customer.full_name = customer_name
                    sale.customer.phone = phone
                    sale.customer.save()
                else:
                    customer = Customer.objects.create(
                        full_name=customer_name,
                        phone=phone
                    )
                    sale.customer = customer
            else:
                sale.customer = None
            
            # Update sale status and payment
            sale.sale_type = request.POST.get('sale_type', 'paid')
            if sale.sale_type == 'paid':
                sale.payment_method = request.POST.get('payment_method', 'cash')
            else:
                sale.payment_method = None
            
            sale.save()
            messages.success(request, f'Sale #{sale.id} updated successfully!')
            return redirect('sale_list')
        except Exception as e:
            messages.error(request, f'Error updating sale: {str(e)}')
            return redirect('sale_list')
    return HttpResponseNotAllowed(['POST'])

@transaction.atomic
def delete_sale(request, sale_id):
    if request.method == 'POST':
        try:
            sale = get_object_or_404(Sale, id=sale_id)
            # Restore product quantities
            for item in sale.items.all():
                product = item.product
                product.stock_quantity += item.quantity
                product.save()
            sale.delete()
            messages.success(request, f'Sale #{sale_id} deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting sale: {str(e)}')
        return redirect('sale_list')
    return HttpResponseNotAllowed(['POST'])

def sale_list(request):
    sales = Sale.objects.all().prefetch_related('items', 'customer').order_by('-sale_date')
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()
    
    if search_query:
        sales = sales.filter(
            Q(customer__full_name__icontains=search_query) |
            Q(customer__phone__icontains=search_query) |
            Q(id__startswith=search_query)
        )
    
    if status_filter in ['paid', 'unpaid']:
        sales = sales.filter(sale_type=status_filter)
    
    return render(request, 'sales.html', {
        'sales': sales,
        'products': Product.objects.filter(availability_status=True),
        'search_query': search_query,
        'status_filter': status_filter
    })

# Category/Brand Views
def create_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name)
            messages.success(request, 'Category created successfully!')
        else:
            messages.error(request, 'Category name is required!')
        return redirect('product_list')
    return HttpResponseNotAllowed(['POST'])

def create_brand(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Brand.objects.create(name=name)
            messages.success(request, 'Brand created successfully!')
        else:
            messages.error(request, 'Brand name is required!')
        return redirect('product_list')
    return HttpResponseNotAllowed(['POST'])
def sales_analytics(request):
    """Sales analytics view with time period toggle"""
    try:
        today = timezone.now().date()
        
        # 1. Today's Sales Data
        todays_sales = (
            SaleItem.objects
            .filter(sale__sale_date__date=today)
            .aggregate(total_sales=Sum('subtotal')))
        
        # 2. Time Period Sales Data (default to weekly)
        time_period = request.GET.get('period', 'weekly')
        
        if time_period == 'daily':
            sales_data = (
                SaleItem.objects
                .filter(sale__sale_date__gte=today - timedelta(days=7))
                .annotate(day=TruncDay('sale__sale_date'))
                .values('day')
                .annotate(total_sales=Sum('subtotal'))
                .order_by('day'))
            labels = [sale['day'].strftime('%b %d') for sale in sales_data]
        elif time_period == 'monthly':
            sales_data = (
                SaleItem.objects
                .filter(sale__sale_date__gte=today - timedelta(days=180))
                .annotate(month=TruncMonth('sale__sale_date'))
                .values('month')
                .annotate(total_sales=Sum('subtotal'))
                .order_by('month'))
            labels = [sale['month'].strftime('%b %Y') for sale in sales_data]
        elif time_period == 'yearly':
            sales_data = (
                SaleItem.objects
                .filter(sale__sale_date__gte=today - timedelta(days=365*5))
                .annotate(year=TruncYear('sale__sale_date'))
                .values('year')
                .annotate(total_sales=Sum('subtotal'))
                .order_by('year'))
            labels = [sale['year'].strftime('%Y') for sale in sales_data]
        else:  # weekly (default)
            sales_data = (
                SaleItem.objects
                .filter(sale__sale_date__gte=today - timedelta(weeks=4))
                .annotate(week=TruncWeek('sale__sale_date'))
                .values('week')
                .annotate(total_sales=Sum('subtotal'))
                .order_by('week'))
            labels = [sale['week'].strftime('%b %d') for sale in sales_data]
        
        # 3. Top Products Data
        top_products = (
            SaleItem.objects
            .values('product_name')
            .annotate(total_sales=Sum('subtotal'))
            .order_by('-total_sales')[:5])
        
        # Prepare Chart.js datasets
        chart_data = {
            'today': float(todays_sales['total_sales'] or 0),
            'time_period': {
                'labels': labels,
                'data': [float(sale['total_sales']) for sale in sales_data],
                'period': time_period,
            },
            'products': {
                'labels': [p['product_name'] for p in top_products],
                'data': [float(p['total_sales']) for p in top_products],
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.5)',
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 206, 86, 0.5)',
                    'rgba(75, 192, 192, 0.5)',
                    'rgba(153, 102, 255, 0.5)'
                ],
            }
        }
        
        return render(request, 'sales_graphs.html', {
            'chart_data': chart_data,
            'top_products': top_products,
            'current_period': time_period,
        })
        
    except Exception as e:
        return render(request, 'sales_graphs.html', {
            'error': str(e)
        })