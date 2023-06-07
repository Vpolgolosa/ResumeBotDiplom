from django.contrib import admin

# Register your models here.
from .models import Resume


class Admin(admin.ModelAdmin):
    pass


admin.site.register(Resume, Admin)
