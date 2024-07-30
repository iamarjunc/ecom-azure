from django.urls import path
from . import views
urlpatterns = [
    path('',views.show_cart,name='cart'),
    path('orders',views.show_orders,name='orders'),
    path('add_to_cart',views.add_to_cart,name='add_to_cart'),
    path('remove_item/<pk>',views.remove_item_from_cart,name='remove_item'),
    path('checkout',views.checkout_cart,name='checkout'),
    path('recommendations/', views.show_recommendations, name='recommendations'),
    path('track-order', views.track_order, name='track_order'),
]

