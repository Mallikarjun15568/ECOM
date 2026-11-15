from cart.models import Cart
from store.models import Wishlist


def count_cartitem(request):
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.get(user=request.user).items.all()
            return {'cart_item_count': cart_items.count()}
        except:
            return {'cart_item_count': 0}
    return {'cart_item_count': 0}

def wishlist_count(request):
    if request.user.is_authenticated:
        try:
            count = Wishlist.objects.filter(user=request.user).count()
            return {'wishlist_item_count' : count}
        except:
            return {'wishlist_item_count' : 0}
    return {'wishlist_item_count' : 0}