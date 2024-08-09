from django.contrib import admin

from .models import Order


class CustomerNameFilter(admin.SimpleListFilter):
    title = 'Customer name'
    parameter_name = 'customer_name'

    # template = 'admin_input_filter.html'

    def lookups(self, request, model_admin):
        return ((None, None),)

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(receiving_company_name__icontains=value)


class ProductsFilter(admin.SimpleListFilter):
    title = "Product"
    parameter_name = "prd_name"

    # template = "admin_input_filter.html"

    def lookups(self, request, model_admin):
        return ((None, None),)

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(products__icontains=value)


class OrdersAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'receiving_company_name', 'delivery_date')
    list_filter = [CustomerNameFilter, ProductsFilter]
    search_fields = ('receiving_company_name',)
    list_per_page = 200
    ordering = ("-delivery_date",)
    actions_on_top = False
    actions = None


admin.site.register(Order, OrdersAdmin)
