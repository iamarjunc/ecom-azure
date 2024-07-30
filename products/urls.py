from django.urls import path
from .  import views
urlpatterns = [
    path('',views.index,name='index'),
    path('products/',views.list_product,name='list_product'),
    path('product-details/<pk>',views.detail_product, name='detail_product'),
    
    path('search/', views.search_items, name='search_items'),
]