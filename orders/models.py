import datetime
import uuid

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


class DeliveryRun(models.Model):
    """
    DeliveryRun.objects.create(id='3b32d552-d99b-472d-8943-e4576ba064a2',code='RM2', name="Rundle Mall 02");
    DeliveryRun.objects.create(id='3d5eec92-4814-4295-a75c-1e14dddf58f8',code='W', name="West");
    DeliveryRun.objects.create(id='6c99c449-7738-45d9-84e5-1416c0f174c6',code='ED', name="Early Delivery");
    DeliveryRun.objects.create(id='36f336bc-49a6-4e2b-a894-6f6ea8f693cb',code='EE', name="Early East");
    DeliveryRun.objects.create(id='177d340e-aa7b-4f57-991c-681910b44aa6',code='LE', name="Late East");
    DeliveryRun.objects.create(id='488afc25-0586-45be-b992-5eebb7bbe2ef',code='RM1', name="Rundle Mall 01");
    DeliveryRun.objects.create(id='868df027-2574-4e88-8c42-7a20df17fd75',code='S', name="South & Hill");
    DeliveryRun.objects.create(id='1316a549-6bef-4fcc-8cdd-55cc28ec8a8d',code='EA', name="East Afternoon");
    DeliveryRun.objects.create(id='7247dc93-0c14-4c9d-91d8-39e55f9a51da',code='N', name="North");
    DeliveryRun.objects.create(id='bf067e17-a77d-4581-a2fb-aae30b528585',code='PU', name="Pickup");
    DeliveryRun.objects.create(id='d0a1ad7e-4615-4b86-8050-4f7e7f472f0e',code='TTP', name="Tea Tree Plaza");
    DeliveryRun.objects.create(id='6de261d9-ab7b-41bb-af91-aada8be3040e',code='CA', name="Chinatown Afternoon");
    DeliveryRun.objects.create(id='923e95f6-56cd-4f02-a46e-cb1520125c04',code='CT', name="Chinatown");
    DeliveryRun.objects.create(id='cc23150e-1bab-4906-aa6a-11e00c367ff1',code='~NR', name="No Run Assigned");
    """
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    code = models.CharField(unique=True, blank=False, null=False, max_length=32)
    name = models.CharField(unique=True, blank=False, null=False, max_length=128)
    created_at = models.DateTimeField(blank=True, null=True, db_comment='UTC',
                                      default=datetime.datetime.now(datetime.UTC))
    updated_at = models.DateTimeField(blank=True, null=True, db_comment='UTC',
                                      default=datetime.datetime.now(datetime.UTC))

    class Meta:
        managed = True
        db_table = 'runs'

    def __str__(self):
        return f"{self.name}"
