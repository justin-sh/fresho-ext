import csv
import logging
import os
from io import TextIOWrapper

from django.contrib.auth.models import User
from django.utils.datastructures import MultiValueDict
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from orders.models import Order
from .serializers import UserSerializer, OrderSerializer

logger = logging.getLogger(__file__)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        orders = Order.objects
        del_date = self.request.query_params.get('delivery_date')
        customer = self.request.query_params.get('customer')
        if del_date:
            orders = orders.filter(delivery_date=del_date)
        if customer:
            orders = orders.filter(receiving_company_name__icontains=customer)
        if not del_date and not customer:
            return orders.none()
        return orders.order_by('receiving_company_name', '-delivery_date')

    @action(detail=False)
    def init(self, request):
        cookies = {
            '_capsule-digital-template_session': os.environ.get('FRESHO_COOKIE')
        }
        url = 'https://app.fresho.com/api/v1/my/suppliers/supplier_orders'

        logger.info(request.GET['delivery_date'])
        params = {'page': 1,
                  'per_page': 200,
                  'q[order_state]': 'all',
                  'q[receiving_company_id]': '',
                  'q[delivery_run_code]': '',
                  'q[delivery_date]': request.GET['delivery_date'],
                  'sort': '-delivery_date,-submitted_at,-order_number',
                  }
        # rv = requests.get(url, params=params, cookies=cookies)
        # data = rv.json()
        data = {'supplier_orders': [
            {'additional_notes': None, 'contact_name': 'Gilbert Street Hotel', 'contact_phone': '8231 9909',
             'delivery_address': '88 Gilbert Street, Adelaide SA 5000', 'delivery_date': '2024-08-08',
             'delivery_method': 'Delivery', 'delivery_venue': 'Gilbert Street Hotel', 'discount_percent': '0.0',
             'external_reference': None, 'id': 'ad0c287b-671a-43c7-9563-643764d777a0', 'number_of_boxes': None,
             'order_number': '30935007', 'parent_order_id': None, 'standing_order_enabled': False,
             'start_as_invoice': False, 'state': 'invoiced', 'submitted_at': '2024-08-08T05:00:31.080+01:00',
             'invoice_confirmed': False, 'selling_company_id': 'b181ee08-2214-46ec-ad1e-926a2bbfb8fb',
             'delivery_instructions': 'PLEASE DELIVER BEFORE 11AM', 'cached_payable_total_in_cents': 14264,
             'prefixed_order_number': 'F30935007', 'cancellable': True, 'chargeable': True, 'charge_credit_card': False,
             'latest_charge_state': None, 'is_locked': True, 'finalised': True, 'has_zero_price_product_orders': False,
             'is_credit_note': False, 'supplier_may_finalise': False, 'formatted_cached_payable_total': '$142.64',
             'may_mark_as_paid': True, 'receiving_company_id': '83d7ec7e-a03d-45f2-ac7b-569905a42f7c',
             'status_icons': '',
             'has_credit_card_fee': False, 'receiving_company_name': 'Gilbert Street Hotel',
             'placed_by_name': 'qian zhang'},
            {'additional_notes': None, 'contact_name': 'Mugen House City, Zhenghan Jiang',
             'contact_phone': '0416761214, 61429 993 018',
             'delivery_address': '408 King William St, Adelaide SA 5000',
             'delivery_date': '2024-08-08', 'delivery_method': 'Delivery',
             'delivery_venue': 'Mugen House City', 'discount_percent': '0.0',
             'external_reference': None, 'id': '0298e64b-a65c-4552-aa04-6617366043d5',
             'number_of_boxes': None, 'order_number': '30928168', 'parent_order_id': None,
             'standing_order_enabled': False, 'start_as_invoice': False,
             'state': 'cancelled', 'submitted_at': '2024-08-08T03:51:36.329+01:00',
             'invoice_confirmed': False,
             'selling_company_id': 'b181ee08-2214-46ec-ad1e-926a2bbfb8fb',
             'delivery_instructions': '', 'cached_payable_total_in_cents': 28527,
             'prefixed_order_number': 'F30928168', 'cancellable': True,
             'chargeable': False, 'charge_credit_card': False,
             'latest_charge_state': None, 'is_locked': True, 'finalised': False,
             'has_zero_price_product_orders': False, 'is_credit_note': False,
             'supplier_may_finalise': False, 'formatted_cached_payable_total': '$285.27',
             'may_mark_as_paid': False,
             'receiving_company_id': '7a8d5ef4-f416-418d-a5f3-600b66703fe1',
             'status_icons': '', 'has_credit_card_fee': False,
             'receiving_company_name': 'Mugen House City',
             'placed_by_name': 'qian zhang'},
            {'additional_notes': None, 'contact_name': 'Yvonne', 'contact_phone': '0473657917',
             'delivery_address': '36, Wright Street, Adelaide.', 'delivery_date': '2024-08-08',
             'delivery_method': 'Delivery', 'delivery_venue': 'Ding Hao', 'discount_percent': '0.0',
             'external_reference': None, 'id': '0692e127-d778-4956-9cb3-d4f6b4202cd2', 'number_of_boxes': 1,
             'order_number': '30700764', 'parent_order_id': None, 'standing_order_enabled': False,
             'start_as_invoice': False, 'state': 'invoiced', 'submitted_at': '2024-07-31T20:36:54.669+01:00',
             'invoice_confirmed': False, 'selling_company_id': 'b181ee08-2214-46ec-ad1e-926a2bbfb8fb',
             'delivery_instructions': '', 'cached_payable_total_in_cents': 24240, 'prefixed_order_number': 'F30700764',
             'cancellable': True, 'chargeable': True, 'charge_credit_card': False, 'latest_charge_state': None,
             'is_locked': True, 'finalised': True, 'has_zero_price_product_orders': True, 'is_credit_note': False,
             'supplier_may_finalise': False, 'formatted_cached_payable_total': '$242.40', 'may_mark_as_paid': True,
             'receiving_company_id': '161f1339-d0a3-4292-9cc8-1290fe21816b', 'status_icons': '💳',
             'has_credit_card_fee': False, 'receiving_company_name': 'Ding Hao', 'placed_by_name': 'Justin'}],
            'meta': {'total_objects': 3, 'total_pages': 1,
                     'supplier_dashboard': {'next_delivery_order_count': 142, 'future_delivery_order_count': 35}}}
        # logger.info(rv.url)
        # logger.info(rv.status_code)

        logger.info(len(data['supplier_orders']))
        return Response('ok from viewsets')

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def upload(self, request):
        logger.info("---------")
        files: MultiValueDict = request.FILES
        if files and len(files) != 1:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        order_file = files.get("orderFile")

        # max size : 1M
        if order_file.size > 1 * 1024 * 1024:
            return Response("File is too big", status=status.HTTP_400_BAD_REQUEST)

        f = TextIOWrapper(order_file, encoding="utf-8", newline="")
        reader = csv.DictReader(f)
        logger.info(reader.fieldnames)
        for x in reader:
            logger.info(x)

        return Response("ok from viewsets")
