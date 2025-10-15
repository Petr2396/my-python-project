from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path("search/", views.product_search, name="product_search"),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
    
]
