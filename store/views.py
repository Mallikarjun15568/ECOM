from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from store.models import Product, Category, Wishlist
from django.contrib import messages
from django.db.models import Avg
# Create your views here.
def home(request):
    featured_products = Product.objects.all()[:6]
    return render(request, 'store/home.html', {'featured_products': featured_products})

def product_list(request):
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')
    sort = request.GET.get('sort', '')

    products = Product.objects.all()
    categories = Category.objects.all()

    if query:
        from django.db.models import Q
        words = query.split()
        q_objects = Q()
        for word in words:
            q_objects |= Q(name__icontains=word)
        products = products.filter(q_objects)

    if category_slug:
        products = products.filter(category__slug = category_slug)

    if sort == 'low':
        products = products.order_by('price')

    if sort == 'high':
        products = products.order_by('-price')

    return render(request, 'store/product_list.html',
                   {'products': products,
                    'categories': categories,
                    'current_category': category_slug,
                    'query': query})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    is_wishlisted = False
    user_review = None
    has_purchased = False
    if request.user.is_authenticated:
        is_wishlisted = request.user.wishlist.filter(product=product).exists()
        user_review = product.reviews.filter(user=request.user).first()
        from orders.models import OrderItem
        has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            order__status='delivered',
            product=product
        ).exists()

    review = product.reviews.filter(status='approved').order_by('-created_at')
    avg_rating = review.aggregate(Avg('rating'))[ 'rating__avg' ]
    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'is_wishlisted': is_wishlisted,
        'user_review': user_review,
        'has_purchased': has_purchased,
        'avg_rating': avg_rating,
        'reviews': review
    })


def search_suggestions(request):
    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse({'results': []})

    products = Product.objects.filter(name__icontains=query)[:5]
    results = [
        {'name': product.name, 'slug': product.slug, 'price': str(product.price)}
        for product in products
    ]
    return JsonResponse({'results': results})

@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item = request.user.wishlist.filter(product=product)
    if wishlist_item.exists():
        wishlist_item.delete()
        messages.success(request, f'"{product.name}" removed from wishlist!')
    else:
        Wishlist.objects.create(user=request.user, product=product)
        messages.success(request, f'"{product.name}" added to wishlist!')
    next_url = request.GET.get('next')
    return redirect(next_url) if next_url else redirect('product_detail', slug=product.slug)

@login_required
def wishlist_page(request):
    wishlist_items = request.user.wishlist.all()
    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    from orders.models import OrderItem
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        order__status='delivered',
        product=product
    ).exists()

    if not has_purchased:
        messages.error(request, 'You can only review products you have purchased!')
        return redirect('product_detail', slug=product.slug)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        if rating and comment:
            review, created = product.reviews.get_or_create(
                user=request.user,
                defaults={'rating': rating, 'comment': comment, 'status': 'pending'}
            )
            if not created:
                review.rating = rating
                review.comment = comment
                review.status = 'pending'
                review.save()
                messages.success(request, 'Review updated!')
            else:
                messages.success(request, 'Review submitted! Pending approval.')
        else:
            messages.error(request, 'Please provide rating and comment!')
            return redirect('product_detail', slug=product.slug)
    return redirect('product_detail', slug=product.slug)