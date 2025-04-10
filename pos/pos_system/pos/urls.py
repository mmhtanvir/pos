from django.urls import path
from . import views

urlpatterns = [
    # Product-related URLs
    path('product_list/', views.product_list, name='product_list'),
    path('create_product/', views.create_product, name='create_product'),
    path('update_product/<int:product_id>/', views.update_product, name='update_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('categories/create/', views.create_category, name='create_category'),
    path('brands/create/', views.create_brand, name='create_brand'),
]
