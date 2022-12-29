from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from order.forms import CartAddProductForm
from .models import Product, Category, Variants, Images


# Create your views here.
def products(request):
    pro = Product.objects.filter(active=True)
    category = Category.objects.all()
    catid = request.GET.get('category')
    if catid:
        pro = Product.objects.filter(category=catid)
    else:
        pro = Product.objects.filter(active=True)
    name = None
    if 'search' in request.GET:
        name = request.GET['search']
        if name:
            pro = pro.filter(name__icontains=name)


    context = {'products': pro, 'category': category,'name':name}
    return render(request, 'products/products.html', context)


def product(request, id):
    query = request.GET.get('q')
    product = Product.objects.get(pk=id)
    image = Images.objects.filter(product_id=id)
    cart_product_form = CartAddProductForm()
    context = {
        'cart_product_form': cart_product_form,
        'image': image,
        'product': product,
    }

    if product.variant != "None":  # Product have variants
        if request.method == 'POST':  # if we select color
            variant_id = request.POST.get('variantid')
            variant = Variants.objects.get(id=variant_id)  # selected product by click color radio
            colors = Variants.objects.filter(product_id=id, size_id=variant.size_id)
            sizes = Variants.objects.raw('SELECT * FROM  products_variants  WHERE product_id=%s GROUP BY size_id', [id])
            query += variant.title + ' Size:' + str(variant.size) + ' Color:' + str(variant.color)
        else:
            variants = Variants.objects.filter(product_id=id)
            colors = Variants.objects.filter(product_id=id, size_id=variants[0].size_id)
            sizes = Variants.objects.raw('SELECT * FROM  products_variants  WHERE product_id=%s GROUP BY size_id', [id])
            variant = Variants.objects.get(id=variants[0].id)
        context.update({'sizes': sizes, 'colors': colors, 'variant': variant, 'query': query})

    return render(request, 'products/product.html', context=context)


def ajaxcolor(request):
    data = {}
    if request.POST.get('action') == 'post':
        size_id = request.POST.get('size')
        productid = request.POST.get('productid')
        colors = Variants.objects.filter(product_id=productid, size_id=size_id)
        context = {
            'size_id': size_id,
            'productid': productid,
            'colors': colors,
        }
        data = {'rendered_table': render_to_string('products/color_list.html', context=context)}
        return JsonResponse(data)
    return JsonResponse(data)
