from django.contrib import admin
from .models import Order


class OrdersAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'receiving_company_name', 'delivery_date')
    # list_filter = ('delivery_date',)
    search_fields = ('receiving_company_name',)
    list_per_page = 200
    ordering = ("-delivery_date",)


admin.site.register(Order, OrdersAdmin)
