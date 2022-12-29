from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from order.models import Order, OrderProduct
from user.forms import SignUpForm, UserUpdateForm, ProfileUpdateForm
from user.models import Profile
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token



def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect('/')


def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("template_activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear {user} , please go to you email  {to_email}  inbox and click on \
                received activation link to confirm and complete the registration.  Note: Check your spam folder.')
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')






@login_required(login_url='/accounts/login/')
def index(request):
    # category = Category.objects.all()
    current_user = request.user  # Access User Session information
    profile = Profile.objects.get(user_id=current_user.id)
    context = {'profile': profile}
    return render(request, 'registration/profile.html', context)


def login_form(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            current_user = request.user
            data = Profile()
            data.user_id = current_user.id
            data.save()
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            messages.warning(request, "Login Error !! Username or Password is incorrect")
            return HttpResponseRedirect('/')
    context = {  # 'category': category
    }
    return render(request, 'registration/login.html', context)


def logout_func(request):
    logout(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def signup_form(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid() :
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.warning(request, "Confirmation Mail Already Sent")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    form = SignUpForm()


    context = {'form': form}
    return render(request, 'registration/signup.html', context)


@login_required(login_url='/accounts/login/')
def user_update(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)  # request.user is user  data
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your account has been updated!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(
            instance=request.user.profile)  # "userprofile" model -> OneToOneField relatinon with user
        context = {
            'user_form': user_form,
            'profile_form': profile_form
        }
        return render(request, 'registration/user_update.html', context)


@login_required(login_url='/accounts/login/')
def user_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect('/user')
        else:
            messages.error(request, 'Please correct the error below.<br>' + str(form.errors))
            return HttpResponseRedirect('/user/password')
    else:
        # category = Category.objects.all()
        form = PasswordChangeForm(request.user)
        return render(request, 'registration/user_password.html', {'form': form,  # 'category': category
                                                                   })


@login_required(login_url='/accounts/login/')
def user_orders(request):
    # category = Category.objects.all()
    current_user = request.user
    orders = Order.objects.filter(user_id=current_user.id)
    context = {  # 'category': category,
        'orders': orders,
    }
    return render(request, 'registration/user_orders.html', context)


@login_required(login_url='/accounts/login/')
def user_orderdetail(request, id):
    # category = Category.objects.all()
    current_user = request.user
    order = Order.objects.get(user_id=current_user.id, id=id)
    orderitems = OrderProduct.objects.filter(order_id=id)
    context = {
        # 'category': category,
        'order': order,
        'orderitems': orderitems,
    }
    return render(request, 'registration/user_order_detail.html', context)


@login_required(login_url='/accounts/login/')
def user_order_product(request):
    # category = Category.objects.all()
    current_user = request.user
    order_product = OrderProduct.objects.filter(user_id=current_user.id).order_by('-id')
    context = {  # 'category': category,
        'order_product': order_product,
    }
    return render(request, 'user_order_products.html', context)


@login_required(login_url='/accounts/login/')
def user_order_product_detail(request, id, oid):
    # category = Category.objects.all()
    current_user = request.user
    order = Order.objects.get(user_id=current_user.id, id=oid)
    orderitems = OrderProduct.objects.filter(id=id, user_id=current_user.id)
    context = {
        # 'category': category,
        'order': order,
        'orderitems': orderitems,
    }
    return render(request, 'user_order_detail.html', context)


##########################################################################################

