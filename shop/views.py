from django.shortcuts import render
from catalog.models import Product

def home(request):
    # Товары отмеченные для показа на главной
    featured_products = Product.objects.filter(on_main_page=True)[:6]
    
    # Если ни один не отмечен, показываем последние
    if not featured_products:
        featured_products = Product.objects.all().order_by('-id')[:6]
    
    return render(request, "home.html", {
        'featured_products': featured_products
    })
