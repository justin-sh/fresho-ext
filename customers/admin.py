from django.contrib import admin
from .models import Customer


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_code', 'customer_name', 'active')
    search_fields = ('customer_name',)
    list_per_page = 200
    ordering = ("customer_name",)


admin.site.register(Customer, CustomerAdmin)
