from django.contrib import admin
import admin_thumbnails
from .models import Product, Category, Images, Color,Size,Variants
from import_export.admin import ImportExportActionModelAdmin






@admin_thumbnails.thumbnail('image')
class ProductImageInline(admin.TabularInline):
    model = Images
    readonly_fields = ('id',)
    extra = 1

class ProductVariantsInline(admin.TabularInline):
    model = Variants
    readonly_fields = ('image_tag',)
    extra = 1
    show_change_link = True


class ColorAdmin(ImportExportActionModelAdmin):
    list_display = ['name','code','color_tag']

class SizeAdmin(ImportExportActionModelAdmin):
    list_display = ['name','code']


class VariantsAdmin(admin.ModelAdmin):
    list_display = ['title','product','color','size','price','quantity','image_tag']
    list_editable = ['product','color','size','price','quantity']


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id','catname','catparent']
    list_editable = ['catname','catparent']

@admin_thumbnails.thumbnail('image')
class ImagesAdmin(admin.ModelAdmin):
    list_display = ['image','title','image_thumbnail']


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name',  'category',
                    'active', 'created','new','Featured','flash_sale','default_price',' ']
    search_fields = ['name', 'price', 'category',
                     'active', 'created']
    list_editable = ['category', 'active','new','Featured','flash_sale','default_price','week_deal']
    list_filter = ['name', 'category',
                   'active', 'created']
    date_hierarchy = 'created'
    inlines = [ProductImageInline,ProductVariantsInline]

    class Meta:
        model = Product


admin.site.register(Product, ProductAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Images,ImagesAdmin)
admin.site.register(Color,ColorAdmin)
admin.site.register(Size,SizeAdmin)
admin.site.register(Variants,VariantsAdmin)
