from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/search/', views.search_suggestions, name='search_suggestions'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/', views.wishlist_page, name='wishlist_page'),
    path('review/<int:product_id>', views.submit_review, name='submit_review'),
]