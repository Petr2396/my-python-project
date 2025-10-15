from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.db.models import Q
from django.http import JsonResponse

def product_list(request):
    products = Product.objects.all()
    category_slug = request.GET.get('category')
    query = request.GET.get("q")
    
    # Фильтрация по категории
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    else:
        category = None
    
    # Поиск
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    # Получаем все категории для меню
    categories = Category.objects.all()
    
    return render(request, "catalog/product_list.html", {
        "products": products, 
        "query": query,
        "categories": categories,
        "current_category": category
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    images = product.images.all()
    return render(request, 'catalog/product_detail.html', {'product': product, 'images': images})

def product_search(request):
    q = request.GET.get("q", "").strip()
    results = []
    if q:
        qs = Product.objects.filter(
            Q(name__icontains=q) | Q(description__icontains=q)
        )[:10]
        for p in qs:
            url = ""
            try:
                url = reverse("catalog:product_detail", args=[p.slug])
            except Exception:
                url = ""
            image = ""
            try:
                if hasattr(p, "images") and p.images.exists():
                    image = p.images.first().image.url
            except Exception:
                image = ""
            results.append({
                "id": p.id,
                "name": p.name,
                "price": str(p.price),
                "url": url,
                "image": image,
            })
    return JsonResponse({"results": results})