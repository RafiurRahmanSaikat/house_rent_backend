from django.contrib import admin

from . import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        "slug": ("name",),
    }


admin.site.register(models.House)
admin.site.register(models.Advertisement)
admin.site.register(models.RentRequest)
admin.site.register(models.Review)
