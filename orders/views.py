from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Order, OrderedItem
from products.models import Product
from .recom_utils import get_recommendations  # Import the utility function

@login_required(login_url='account')
def show_cart(request):
    user = request.user
    customer = user.customer_profile
    cart_obj, created = Order.objects.get_or_create(
        owner=customer,
        order_status=Order.CART_STAGE
    )

    # Fetch recommendations based on recent cart activity
    recommendations = get_recommendations(customer.id)
    
    context = {
        'cart': cart_obj,
        'recommendations': recommendations
    }
    return render(request, 'cart.html', context)

@login_required(login_url='account')
def add_to_cart(request):
    if request.POST:
        user = request.user
        print(user)
        
        customer = user.customer_profile
        print(customer)
        quantity = int(request.POST.get('quantity'))
        product_id = request.POST.get('product_id')
        cart_obj, created = Order.objects.get_or_create(
            owner=customer,
            order_status=Order.CART_STAGE
        )
        product = Product.objects.get(pk=product_id)
        ordered_item, created = OrderedItem.objects.get_or_create(
            product=product,
            owner=cart_obj
        )
        if created:
            ordered_item.quantity = quantity
            ordered_item.save()
        else:
            ordered_item.quantity = quantity + ordered_item.quantity
            ordered_item.save()
    return redirect('cart')

def remove_item_from_cart(request, pk):
    item = OrderedItem.objects.get(pk=pk)
    if item:
        item.delete()
    return redirect('cart')

def checkout_cart(request):
    if request.POST:
        try:
            user = request.user
            customer = user.customer_profile
            total = float(request.POST.get('total'))
            order_obj = Order.objects.get(
                owner=customer,
                order_status=Order.CART_STAGE
            )
            if order_obj:
                order_obj.order_status = Order.ORDER_CONFIRMED
                order_obj.total_price = total
                order_obj.save()
                status_message = "Your order is processed. Your items will be delivered within 2 days"
                messages.success(request, status_message)
            else:
                status_message = "Unable to process"
                messages.error(request, status_message)
        except Exception as e:
                status_message = "Unable to process"
                messages.error(request, status_message)
    return redirect('cart')

@login_required(login_url="account")
def show_orders(request):
    user = request.user
    customer = user.customer_profile
    all_orders = Order.objects.filter(owner=customer).exclude(order_status=Order.CART_STAGE)
    
    # Fetch related items for each order 
    orders_with_items = []
    for order in all_orders:
        ordered_items = OrderedItem.objects.filter(owner=order).select_related('product')
        orders_with_items.append({
            'order': order,
            'items': ordered_items,
        })
    
    context = {"orders_with_items": orders_with_items}
    return render(request, 'orders.html', context)

@login_required(login_url='account')
def show_recommendations(request):
    user_id = request.user.customer_profile.id
    recommendations = get_recommendations(user_id)
    
    context = {'recommendations': recommendations}
    return render(request, 'recommendations.html', context)

def track_order(request):
    order_id = request.GET.get('id')
    if not order_id:
        return JsonResponse({'error': 'No order ID provided.'}, status=400)

    try:
        # Fetch the order with the given ID
        order = Order.objects.get(id=order_id, delete_status=Order.LIVE)

        # Define the status mapping manually
        status_mapping = {
            Order.CART_STAGE: 'Cart Stage',
            Order.ORDER_CONFIRMED: 'Order Confirmed',
            Order.ORDER_PROCESSED: 'Order Processed',
            Order.ORDER_DELIVERED: 'Order Delivered',
            Order.ORDER_REJECTED: 'Order Rejected',
        }

        # Get the status using the manual mapping
        status = status_mapping.get(order.order_status, 'Unknown status')

        # Prepare order details to be sent in the response
        order_details = {
            'id': order.id,
            'status': status,
            'total_price': order.total_price,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': order.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'items': [
                {
                    'product_name': item.product.title,
                    'quantity': item.quantity,
                    'price': item.product.price,
                    'image': item.product.image.url,
                } for item in order.added_items.all()
            ]
        }
        return JsonResponse({'order': order_details})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'No order found with the provided ID.'}, status=404)    