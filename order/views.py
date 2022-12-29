from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.crypto import get_random_string
from django.shortcuts import render, get_object_or_404, redirect
from order.models import ShopCart, ShopCartForm, OrderForm, Order, OrderProduct
from products.models import Category, Product, Variants
from user.models import Profile
import stripe


stripe.api_key = 'sk_test_51M8qGSGrudnGZQOKK9zBQ5paV7j8sEy1lILyqbd9nj7aSuFSjSgo66Jqwbfn7eQT8QGXrhebyKbfASBJ1YRck1fH00kggt4emO'



def index(request):
    return HttpResponse ("Order Page")

@login_required(login_url='/login') # Check login
def addtoshopcart(request,id):
    url = request.META.get('HTTP_REFERER')  # get last url
    current_user = request.user  # Access User Session information
    product= Product.objects.get(pk=id)

    if product.variant != 'None':
        variantid = request.POST.get('variantid')  # from variant add to cart
        checkinvariant = ShopCart.objects.filter(variant_id=variantid, user_id=current_user.id)  # Check product in shopcart
        if checkinvariant:
            control = 1 # The product is in the cart
        else:
            control = 0 # The product is not in the cart"""
    else:
        checkinproduct = ShopCart.objects.filter(product_id=id, user_id=current_user.id) # Check product in shopcart
        if checkinproduct:
            control = 1 # The product is in the cart
        else:
            control = 0 # The product is not in the cart"""

    if request.method == 'POST':  # if there is a post
        form = ShopCartForm(request.POST)
        if form.is_valid():
            if control == 1 :  # Update  shopcart
                data = ShopCart.objects.get(product_id=id, variant_id=variantid, user_id=current_user.id)
                if str(data.variant.quantity) > str(data.quantity):
                    data.quantity += form.cleaned_data['quantity']
                    data.save()  # save data
                    messages.success(request, "Shop Cart Updated")
                else:
                    messages.success(request, "No More Products In Stock")

            else:  # Inser to Shopcart
                data = ShopCart()
                data.user_id = current_user.id
                data.product_id = id
                data.variant_id = variantid
                data.quantity = form.cleaned_data['quantity']
                data.save()
                messages.success(request, "Product added to Shopcart ")
        return HttpResponseRedirect(url)

    else:  # if there is no post
        if control == 1 :  # Update  shopcart
            data = ShopCart.objects.get(variant_id=id, user_id=current_user.id)
            data.quantity += 1
            data.save()  #
        else:  # Inser to Shopcart
            data = ShopCart()  # model ile bağlantı kur
            data.user_id = current_user.id
            data.product_id = id
            data.quantity = 1
            data.variant_id = None
            data.save()  #
        messages.success(request, "Shop Cart Updated")
        return HttpResponseRedirect(url)


def shopcart(request):
    category = Category.objects.all()
    current_user = request.user  # Access User Session information
    shopcart = ShopCart.objects.filter(user_id=current_user.id)
    total=0
    for rs in shopcart:
        if rs.product.variant == 'None':
            total += rs.product.price * rs.quantity
        else:
            total += rs.variant.price * rs.quantity
    #return HttpResponse(str(total))
    context={'shopcart': shopcart,
             'category':category,
             'total': total,
             }
    return render(request, 'order/shopcart_products.html', context)

@login_required(login_url='/login') # Check login
def deletefromcart(request,id):
    ShopCart.objects.filter(id=id).delete()
    messages.success(request, "Your item deleted form Shopcart.")
    return HttpResponseRedirect("/order/shopcart")


def orderproduct(request):
    category = Category.objects.all()
    current_user = request.user
    shopcart = ShopCart.objects.filter(user_id=current_user.id)
    total = 0
    for rs in shopcart:
        if rs.product.variant == 'None':
            total += rs.product.default_price * rs.quantity
        else:
            total += rs.variant.price * rs.quantity

    if request.method == 'POST':  # if there is a post
        form = OrderForm(request.POST)
        #return HttpResponse(request.POST.items())
        if form.is_valid():
            # Send Credit card to bank,  If the bank responds ok, continue, if not, show the error
            # ..............

            data = Order()
            data.first_name = form.cleaned_data['first_name'] #get product quantity from form
            data.last_name = form.cleaned_data['last_name']
            data.address = form.cleaned_data['address']
            data.city = form.cleaned_data['city']
            data.phone = form.cleaned_data['phone']
            data.user_id = current_user.id
            data.total = total
            ordercode= get_random_string(5).upper() # random cod
            data.code =  ordercode
            data.save() #


            for rs in shopcart:
                detail = OrderProduct()
                detail.order_id     = data.id # Order Id
                detail.product_id   = rs.product_id
                detail.user_id      = current_user.id
                detail.quantity     = rs.quantity
                if rs.product.variant == 'None':
                    detail.price    = rs.product.price
                else:
                    detail.price = rs.variant.price
                detail.variant_id   = rs.variant_id
                detail.amount        = rs.amount
                detail.save()
                # ***Reduce quantity of sold product from Amount of Product
                if  rs.product.variant=='None':
                    product = Product.objects.get(id=rs.product_id)
                    product.amount -= rs.quantity
                    product.save()
                else:
                    variant = Variants.objects.get(id=rs.variant_id)
                    variant.quantity -= rs.quantity
                    variant.save()
                #************ <> *****************

            ShopCart.objects.filter(user_id=current_user.id).delete() # Clear & Delete shopcart
            request.session['cart_items']=0
            messages.success(request, "Your Order has been completed. Thank you ")
            return render(request, 'order/Order_Completed.html',{'ordercode':ordercode,'category': category})
        else:
            messages.warning(request, form.errors)
            return HttpResponseRedirect("/order/orderproduct")

    form= OrderForm()
    profile = Profile.objects.get(user_id=current_user.id)
    context = {'shopcart': shopcart,
               'category': category,
               'total': total,
               'form': form,
               'profile': profile,
               }
    return render(request, 'order/Order_Form.html', context)



#########################Srtip############################


def checkout_session(request):
    current_user = request.user
    shopcart = ShopCart.objects.filter(user_id=current_user.id)
    total = 0
    for str in shopcart:
        total += str.variant.price * str.quantity
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': str.variant_id,
                    },
                    'unit_amount': int(total) * 100,
                },
                'quantity': 1,
            }],
            mode='payment',

            success_url='http://127.0.0.1:8000/order/pay_success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://127.0.0.1:8000/pay_cancel',
        )
    return redirect(session.url, code=303)


def pay_success(request):
    current_user = request.user
    total = 0
    shopcart = ShopCart.objects.filter(user_id=current_user.id)
    for rs in shopcart:
        if rs.product.variant == 'None':
            total += rs.product.price * rs.quantity
        else:
            total += rs.variant.price * rs.quantity
    current_user = request.user
    #form = OrderForm(request.POST)
    data = Order()
    data.first_name = current_user.first_name # get product quantity from form
    data.last_name = current_user.last_name
    data.address = current_user.profile.address
    data.city = current_user.profile.city
    data.phone = current_user.profile.phone
    data.paid = True
    data.user_id = current_user.id
    data.total = total
    data.ip = request.META.get('REMOTE_ADDR')
    ordercode = get_random_string(5).upper()  # random cod
    data.code = ordercode
    data.save()  #

    for rs in shopcart:
        detail = OrderProduct()
        detail.order_id = data.id  # Order Id
        detail.product_id = rs.product_id
        detail.user_id = current_user.id
        detail.quantity = rs.quantity
        if rs.product.variant == 'None':
            detail.price = rs.product.price
        else:
            detail.price = rs.variant.price
        detail.variant_id = rs.variant_id
        detail.amount = rs.amount
        detail.save()
        # ***Reduce quantity of sold product from Amount of Product
        if rs.product.variant == 'None':
            product = Product.objects.get(id=rs.product_id)
            product.amount -= rs.quantity
            product.save()
        else:
            variant = Variants.objects.get(id=rs.variant_id)
            variant.quantity -= rs.quantity
            variant.save()


        # ************ <> *****************

    ShopCart.objects.filter(user_id=current_user.id).delete()  # Clear & Delete shopcart
    request.session['cart_items'] = 0
    messages.success(request, "Your Order has been completed. Thank you ")
    return render(request, 'order/Order_Completed.html', {'ordercode': ordercode})


# Cancel
def pay_cancel(request):
    return render(request, 'cancel.html')


###########################################################################################################