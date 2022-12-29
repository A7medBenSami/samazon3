from django.urls import path

from . import views
from . import views as userview
urlpatterns = [
    path('', views.index, name='user_index'),
    path('login/', views.login_form, name='login'),
    path('logout/', views.logout_func, name='logout'),
    path('signup/', views.signup_form, name='signup'),
    path('update/', views.user_update, name='user_update'),
    path('password/', views.user_password, name='user_password'),
    path('orders/', views.user_orders, name='user_orders'),
    path('orders_product/', views.user_order_product, name='user_order_product'),
    path('orderdetail/<int:id>', views.user_orderdetail, name='user_orderdetail'),
    path('order_product_detail/<int:id>/<int:oid>', views.user_order_product_detail, name='user_order_product_detail'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),




]