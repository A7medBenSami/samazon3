from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from user.models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    max_num = 1
    can_delete = False


class UserAdmin(AuthUserAdmin):
    inlines = [ProfileInline]


# unregister old user admin
admin.site.unregister(User)
# register new user admin
admin.site.register(User, UserAdmin)
