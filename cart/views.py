from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cart.models import Cart, CartItem
from store.models import Product
# Create your views here.

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/cart.html', {'cart': cart})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
  
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f'"{product.name}" quantity updated!')
    else:
        messages.success(request, f'"{product.name}" added to cart!')
        return redirect('cart')
    
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'"{product_name}" removed from cart!')
    return redirect('cart')

@login_required
def quantity_update(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    action = request.POST.get('action')

    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f'Quantity updated!')
    elif action == 'decrease':
        if cart_item.quantity > 1:
         cart_item.quantity -= 1
         cart_item.save()
         messages.success(request, f'Quantity updated!')
        else:
            product_name = cart_item.product.name
            cart_item.delete()
            messages.success(request, f'"{product_name}" removed from cart!')

    return redirect('cart')  
