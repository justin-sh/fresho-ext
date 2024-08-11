from django.db import models


class Customer(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=36)
    customer_name = models.CharField(max_length=128, db_comment='do not edit')
    legal_entity_name = models.CharField(max_length=128, db_comment='do not edit')
    business_tax_number = models.CharField(max_length=128, blank=True, null=True, db_comment='do not edit')
    delivery_address = models.CharField(max_length=255, db_comment='do not edit')
    active = models.CharField(max_length=3, db_comment='Yes or No')
    customer_code = models.CharField(unique=True, max_length=255)
    allow_duplicate_customer_code = models.CharField(max_length=3, db_comment='Yes or No')
    pricing_level = models.CharField(max_length=255, blank=True, null=True)
    negotiated_prices_group = models.CharField(max_length=255, blank=True, null=True)
    discount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    show_only_negotiated_pricing = models.CharField(max_length=3, db_comment='Yes or No')
    show_rrp = models.CharField(max_length=3, db_comment='Yes or No')
    delivery_run_code = models.CharField(max_length=255, blank=True, null=True)
    delivery_run_position = models.IntegerField(blank=True, null=True)
    delivery_days_and_cut_off_times_group = models.CharField(max_length=255, blank=True, null=True)
    payment_term_days = models.IntegerField(blank=True, null=True)
    payment_term_option = models.CharField(max_length=255, blank=True, null=True)
    charge_card = models.CharField(max_length=3, db_comment='Yes or No')
    charge_customer_card_fee = models.CharField(max_length=3, db_comment='Yes or No')
    freight_rule = models.CharField(max_length=255, blank=True, null=True)
    minimum_order_amount_for_freight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    delivery_date_message = models.CharField(max_length=255, blank=True, null=True)
    standing_delivery_instructions = models.CharField(max_length=255, blank=True, null=True)
    standing_picking_instructions = models.CharField(max_length=255, blank=True, null=True)
    internal_customer_contact_notes = models.CharField(max_length=255, blank=True, null=True)
    internal_notes = models.CharField(max_length=255, blank=True, null=True)
    visibility_groups = models.CharField(max_length=255, db_comment='do not edit')
    agreement_id = models.CharField(max_length=36, db_comment='do not edit')
    sales_person = models.CharField(max_length=255, blank=True, null=True, db_comment="who's customer")
    created_at = models.DateTimeField(blank=True, null=True, db_comment='UTC')
    updated_at = models.DateTimeField(blank=True, null=True, db_comment='UTC')

    class Meta:
        managed = True
        db_table = 'customers'

    def __str__(self):
        return f"{self.customer_name} #{self.customer_code}"