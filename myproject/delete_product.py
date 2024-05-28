import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from store.models import Product

def delete_product(product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.delete()
        print(f"Product with id {product_id} deleted successfully!")
    except Product.DoesNotExist:
        print(f"Product with id {product_id} does not exist.")

if __name__ == "__main__":
    # Укажите id товара, который нужно удалить
    product_id = 13
    delete_product(product_id)
