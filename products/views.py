from django.shortcuts import render
from .models import Product
from django.core.paginator import Paginator
from django.db.models import Q
from orders.recom_utils import get_recommendations
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.models import User

def index(request):
    # Fetching products
    featured_products = Product.objects.order_by('priority')[:4]
    latest_product = Product.objects.order_by('-id')[:4]
    exclusive_product = Product.objects.order_by('-id')[:1]

    # Initializing recommendations to None
    recommendations = None

    # Check if the user is authenticated
    if request.user.is_authenticated:
        user = request.user

        try:
            customer = user.customer_profile
            # Fetching recommendations
            recommendations = get_recommendations(customer.id)
        except User.customer_profile.RelatedObjectDoesNotExist:
            customer = None

    # Preparing the context
    context = {
        "featured_products": featured_products,
        "latest_product": latest_product,  # Use consistent naming
        "exclusive_product": exclusive_product,
        "recommendations": recommendations
    }

    # Render the template with context
    return render(request, 'index.html', context)

def list_product(request):
    query = request.GET.get('q', '')
    sort_option = request.GET.get('sort', '')
    page = request.GET.get('page', 1)

    product_list = Product.objects.all()

    if query:
        product_list = product_list.filter(Q(title__icontains=query))

    # Sorting based on the sort_option
    if sort_option == 'price_asc':
        product_list = product_list.order_by('price')
    elif sort_option == 'price_desc':
        product_list = product_list.order_by('-price')
    elif sort_option == 'newest':
        product_list = product_list.order_by('-created_at')
    elif sort_option == 'popularity':
        # Assuming popularity can be inferred from the priority field
        product_list = product_list.order_by('-priority')
    else:
        product_list = product_list.order_by('priority')

    product_paginator = Paginator(product_list, 4)
    product_list = product_paginator.get_page(page)

    context = {'products': product_list, 'query': query, 'sort_option': sort_option}
    return render(request, 'products_layout.html', context)

def detail_product(request, pk):
    product = Product.objects.get(pk=pk)
    product_title_words = product.title.split()

    # Build the query to prioritize similar products
    similar_products_query = Q()
    for word in product_title_words:  # prioritize first three words
        similar_products_query |= Q(title__icontains=word)

    similar_products = Product.objects.filter(
        similar_products_query & ~Q(pk=pk)
    ).distinct()[:4]  # Limit the number of similar products displayed

    context = {
        'product': product,
        'similar_products': similar_products
    }
    return render(request, 'product_detail.html', context)


@require_GET
def search_items(request):
    query = request.GET.get('q', '')
    if query:
        results = Product.objects.filter(title__icontains=query, delete_status=Product.LIVE)
        results_data = [
            {
                'id': product.id,
                'title': product.title,
                'price': product.price,
                'image': product.image.url
            } for product in results
        ]
        return JsonResponse({'results': results_data})
    return JsonResponse({'results': []})