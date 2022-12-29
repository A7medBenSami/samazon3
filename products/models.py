from datetime import datetime
from ckeditor.fields import RichTextField
from django.db import models
from django.utils.text import slugify
from django.utils.safestring import mark_safe


# Create your models here.


class Category(models.Model):
    catname = models.CharField(max_length=150)
    catparent = models.ForeignKey('self', limit_choices_to={'catparent__isnull':True},on_delete=models.CASCADE,blank=True,null=True)
    catdesc = models.CharField(max_length=150)

    def __str__(self):
        return self.catname


class Product(models.Model):
    STATUS = (
        ('True', 'True'),
        ('False', 'False'),
    )

    VARIANTS = (
        ('None', 'None'),
        ('Size', 'Size'),
        ('Color', 'Color'),
        ('Size-Color', 'Size-Color'),

    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, blank=True, null=True)
    default_img = models.ImageField(upload_to='photos/%Y/%m/%d')
    default_price = models.DecimalField(max_digits=12, decimal_places=2)
    description = RichTextField()
    mini_description = RichTextField()
    active = models.BooleanField(default=True)
    new = models.BooleanField(default=True, blank=True, null=True)
    Featured = models.BooleanField( default=False,blank=True, null=True)
    flash_sale = models.BooleanField(default=False,blank=True, null=True)
    week_deal = models.BooleanField(default=False,blank=True, null=True)
    created = models.DateTimeField(default=datetime.now)
    stock = models.IntegerField( editable = False, blank=True, null=True)
    variant = models.CharField(max_length=10,choices=VARIANTS)
    category = models.ForeignKey(
        'Category', on_delete=models.CASCADE, related_name='pro_category' )

    class Meta:
        ordering = ('-created',)
        index_together = (('id', 'slug'),)
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Images(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    title = models.CharField(max_length=50,blank=True)
    image = models.ImageField(blank=True, upload_to='images/')

    def __str__(self):
        return self.title

class Color(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=10, blank=True,null=True)
    def __str__(self):
        return self.name
    def color_tag(self):
        if self.code is not None:
            return mark_safe('<p style="background-color:{}">Color </p>'.format(self.code))
        else:
            return ""


class Size(models.Model):
    name = models.CharField(max_length=20)
    code = models.CharField(max_length=10, blank=True,null=True)
    def __str__(self):
        return self.name

class Variants(models.Model):
    title = models.CharField(max_length=100, blank=True,null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE,blank=True,null=True)
    size = models.ForeignKey(Size, on_delete=models.CASCADE,blank=True,null=True)
    image_id = models.IntegerField(blank=True,null=True,default=0)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2,default=0)

    def __str__(self):
        return self.title

    def image(self):
        img = Images.objects.get(id=self.image_id)
        if img.id is not None:
             varimage=img.image.url
        else:
            varimage=""
        return varimage

    def image_tag(self):
        img = Images.objects.get(id=self.image_id)
        if img.id is not None:
             return mark_safe('<img src="{}" height="50"/>'.format(img.image.url))
        else:
            return ""
