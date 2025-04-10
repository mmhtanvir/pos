from django.urls import path
from . import views

urlpatterns = [
    # Product-related URLs
    path('product_list/', views.product_list, name='product_list'),
    path('create_product/', views.create_product, name='create_product'),
    path('update_product/<int:product_id>/', views.update_product, name='update_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    
    # Sale-related URLs
    path('create_sale/', views.create_sale, name='create_sale'),
    path('update_sale/<int:sale_id>/', views.update_sale, name='update_sale'),
    path('delete_sale/<int:sale_id>/', views.delete_sale, name='delete_sale'),
    path('sale_list/', views.sale_list, name='sale_list'),
    path('sales_analytics/', views.sales_analytics, name='sales_analytics'),

    # Category and Brand creation URLs
    path('categories/create/', views.create_category, name='create_category'),
    path('brands/create/', views.create_brand, name='create_brand'),
    
    # Dashboard URL
    path('', views.dashboard, name='dashboard'),
]