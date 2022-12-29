from django.urls import reverse
from django.contrib import admin
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportActionModelAdmin

# Register your models here.
from order.models import ShopCart, Order, OrderProduct


#def order_pdf(obj):
    #return mark_safe('<a href="{}">PDF</a>'.format(reverse('order:admin_Order_pdf', args=[obj.id])))


#order_pdf.short_description = 'Order PDF'


class ShopCartAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'quantity', 'price', 'amount']
    list_filter = ['user']


class OrderProductline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('user', 'product', 'price', 'quantity', 'amount')
    can_delete = False


class OrderAdmin(ImportExportActionModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'phone', 'city', 'total', 'status','paid']
    list_filter = ['status']
    readonly_fields = (
        'user', 'address', 'city', 'phone', 'first_name', 'last_name', 'phone', 'city', 'total')
    can_delete = False
    inlines = [OrderProductline]


class OrderProductAdmin(ImportExportActionModelAdmin):
    list_display = ['user', 'product', 'price', 'quantity', 'amount']
    list_filter = ['user']


admin.site.register(ShopCart, ShopCartAdmin)
admin.site.register(Order, OrderAdmin)
