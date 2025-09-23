from django.shortcuts import render

from store.models import Product


# Create your views here.
def home(request):
    products = Product.objects.all()
    context = {'products': products}

    return render(request, 'store/home.html', context)


def product_detail(request, pk):
    product = Product.objects.get(pk=pk)
    related_products = Product.objects.filter(category=product.category).exclude(id=pk)

    context = {'product': product, 'related_products': related_products}
    return render(request, 'store/product_detail.html', context)
