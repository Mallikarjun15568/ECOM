from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from cart.models import Cart
from orders.models import Order
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = cart.items.all()

    if not cart_item:
        messages.error(request, "Your cart is empty!")
        return redirect('cart')
    
    if request.method == 'POST':

        for items in cart_item:
            if items.quantity > items.product.stock:
                messages.error(request, f"Not enough stock for {items.product.name}. Available stock: {items.product.stock}")
                return redirect('cart')
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        total_price = sum(item.product.price * item.quantity for item in cart_item)

        order = Order.objects.create(
            user = request.user,
            name = name,
            address = address,
            phone = phone,
            total_price = total_price
        )

        for item in cart_item:
            order.items.create(
                product = item.product,
                quantity = item.quantity,
                price = item.product.price
            )

        cart.items.all().delete()
        messages.success(request, "Your order has been placed successfully!")
        return redirect('order_history')

    return render(request, 'orders/checkout.html', {'cart': cart})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status in ['shipped', 'delivered', 'cancelled']:
        messages.error(request, "This order cannot be cancelled.")
        return redirect('order_history')

    order.status = 'cancelled'
    order.save()
    messages.success(request, "Your order has been cancelled.")
    return redirect('order_history')