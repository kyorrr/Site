from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Product, Cart, CartItem, Profile, Order, OrderItem
from django.dispatch import receiver
from django.db.models.signals import post_save
import json
from django.views.decorators.csrf import csrf_exempt
import locale
from django.utils import translation
from django.utils.formats import date_format

def index(request):
    products = Product.objects.all()
    return render(request, 'store/index.html', {'products': products})

def cart(request):
    return render(request, 'store/cart.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
    return render(request, 'store/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        last_name = request.POST['last_name']
        first_name = request.POST['first_name']
        middle_name = request.POST['middle_name']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            user = User.objects.create_user(username=username, password=password, email=email)
            user.last_name = last_name
            user.first_name = first_name
            user.save()
            user.profile.phone = phone
            user.profile.middle_name = middle_name
            user.profile.save()
            login(request, user)
            return redirect('index')
    return render(request, 'store/register.html')

@login_required
def profile_view(request):
    user_profile = request.user.profile
    if request.method == 'POST':
        request.user.username = request.POST['username']
        request.user.email = request.POST['email']
        request.user.first_name = request.POST['first_name']
        request.user.last_name = request.POST['last_name']
        user_profile.phone = request.POST['phone']
        user_profile.middle_name = request.POST['middle_name']
        request.user.save()
        user_profile.save()
        return redirect('profile')

    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    # Установите локаль и активируйте перевод
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
    translation.activate('ru')

    # Преобразование даты заказа в нужный формат
    for order in orders:
        order.formatted_date = date_format(order.created_at, format='d E Y, H:i', use_l10n=True)

    return render(request, 'store/profile.html', {'user': request.user, 'profile': user_profile, 'orders': orders})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created and cart_item.quantity < product.stock:
        cart_item.quantity += 1
    elif created:
        cart_item.quantity = 1
    cart_item.save()

    update_cart_total_price(cart)
    return JsonResponse({'success': True})

@login_required
def get_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    items = [
        {
            'id': item.id,
            'name': item.product.name,
            'quantity': item.quantity,
            'price': item.product.price,
            'item_total_price': item.item_total_price,
            'image_url': item.product.image.url,  # Добавляем URL изображения
            'stock': item.product.stock,
        } for item in cart_items
    ]
    return JsonResponse({'items': items, 'total_price': cart.total_price})

@csrf_exempt
@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quantity = int(data['quantity'])
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
            else:
                cart_item.delete()
            update_cart_total_price(cart_item.cart)
            return JsonResponse({'success': True})
        except (CartItem.DoesNotExist, Cart.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Товар не найден в корзине'})
    return JsonResponse({'success': False, 'error': 'Некорректный запрос'})

@login_required
@csrf_exempt
def remove_cart_item(request, item_id):
    if request.method == 'POST':
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            cart_item.delete()
            update_cart_total_price(cart_item.cart)
            return JsonResponse({'success': True})
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Товар не найден в корзине'})
    return JsonResponse({'success': False, 'error': 'Некорректный запрос'})


def update_cart_total_price(cart):
    cart_items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.item_total_price for item in cart_items)
    cart.total_price = total_price
    cart.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def purchase(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items.exists():
        return JsonResponse({'success': False, 'message': 'Корзина пуста.'})

    order = Order.objects.create(user=request.user, total_price=cart.total_price)
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
            total_price=item.product.price * item.quantity
        )
        item.product.stock -= item.quantity
        item.product.save()
        item.delete()

    cart.total_price = 0
    cart.save()
    return JsonResponse({'success': True})
