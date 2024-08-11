from django.db import models


class Order(models.Model):
    id = models.CharField(primary_key=True, unique=True, max_length=36)
    order_number = models.CharField(unique=True, max_length=255)
    delivery_date = models.DateField()
    receiving_company_id = models.CharField(max_length=36)
    receiving_company_name = models.CharField(max_length=255)
    additional_notes = models.CharField(max_length=4000, blank=True, null=True)
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    contact_phone = models.CharField(max_length=255, blank=True, null=True)
    delivery_address = models.CharField(max_length=255)
    delivery_method = models.CharField(max_length=255)
    delivery_venue = models.CharField(max_length=255)
    external_reference = models.CharField(max_length=255, blank=True, null=True)
    delivery_instructions = models.CharField(max_length=255, blank=True, null=True)
    prefixed_order_number = models.CharField(max_length=255)
    formatted_cached_payable_total = models.CharField(max_length=255)
    payable_total_in_cents = models.IntegerField(db_comment='total in cents', default=0)
    submitted_at = models.DateTimeField(blank=True, null=True, db_comment='UTC')
    state = models.CharField(max_length=255)
    placed_by_name = models.CharField(max_length=255, blank=True, null=True)
    delivery_run = models.CharField(max_length=255, blank=True, null=True)
    products = models.JSONField(blank=True, null=True)
    delivery_at = models.DateTimeField(blank=True, null=True, db_comment='UTC')
    delivery_by = models.CharField(max_length=255, blank=True, null=True)
    delivery_proof_url = models.CharField(max_length=255, blank=True, null=True)
    locked = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True, db_comment='UTC')
    updated_at = models.DateTimeField(blank=True, null=True, db_comment='UTC')

    class Meta:
        managed = True
        db_table = 'orders'

    def __str__(self):
        return f"{self.receiving_company_name} #{self.order_number}"
