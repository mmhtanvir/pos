from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotAllowed
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category, Brand

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