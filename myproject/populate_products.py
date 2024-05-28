import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from store.models import Product

products = [
    {
        'name': 'АККУМУЛЯТОРНАЯ ДРЕЛЬ DEKO ZKCD12FU-LI',
        'description': 'АККУМУЛЯТОРНАЯ ДРЕЛЬ DEKO ZKCD12FU-LI (12В 1X1.5АЧ ВСТРОЕННЫЙ 12НМ 0-800ОБ/МИН БЗП 0.8-10ММ 0.81КГ TYPE-C) КОРОБКА',
        'price': 1880.00,
        'stock': 18,
        'image': 'products/product3.png'
    },
    {
        'name': 'АККУМУЛЯТОРНАЯ ДРЕЛЬ DEKO GCD20DU3 SET4',
        'description': 'АККУМУЛЯТОРНАЯ ДРЕЛЬ DEKO GCD20DU3 SET4 В НАБОРЕ (20В 1Х2.0АЧ LI-ION 40НМ 0-350/1350ОБ/МИН БПЗ 0.8-10ММ) КОРОБКА',
        'price': 5485.00,
        'stock': 12,
        'image': 'products/product1.png'
    },
    {
        'name': 'АККУМУЛЯТОРНАЯ ДРЕЛЬ DEKO SHARKER 20V',
        'description': 'АККУМУЛЯТОРНАЯ ДРЕЛЬ DEKO SHARKER 20V (20В 1Х3.0АЧ СОВМЕСТИМ С АКБ MAKITA 42НМ 0-450/1700ОБ/МИН БЗП 0.8-10ММ 1.35КГ)',
        'price': 7025.00,
        'stock': 10,
        'image': 'products/product2.png'
    },
]

for product_data in products:
    product = Product(**product_data)
    product.save()

print("Products added successfully!")
