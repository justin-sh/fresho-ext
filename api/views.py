import csv
import datetime
import logging
import os
from io import TextIOWrapper

import requests
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
        product = self.request.query_params.get('product')
        if del_date:
            orders = orders.filter(delivery_date=del_date)
        if customer:
            orders = orders.filter(receiving_company_name__icontains=customer)
        if product:
            orders = orders.filter(products__icontains=product)
        if not del_date and not customer and not product:
            return orders.none()
        return orders.order_by('receiving_company_name', '-delivery_date')[:200]

    @action(detail=False)
    def init(self, request):
        cookies = {
            '_capsule-digital-template_session': os.environ.get('FRESHO_COOKIE')
        }
        url = 'https://app.fresho.com/api/v1/my/suppliers/supplier_orders'

        # logger.info(request.GET['delivery_date'])
        params = {'page': 1,
                  'per_page': 200,
                  'q[order_state]': 'all',
                  'q[receiving_company_id]': '',
                  'q[delivery_run_code]': '',
                  'q[delivery_date]': request.GET['delivery_date'],
                  'sort': '-delivery_date,-submitted_at,-order_number',
                  }
        rv = requests.get(url, params=params, cookies=cookies)
        data = rv.json()
        utc_now = datetime.datetime.now(datetime.UTC)
        for x in data['supplier_orders']:
            x['payable_total_in_cents'] = x['cached_payable_total_in_cents'] \
                if x['cached_payable_total_in_cents'] else 0
            x['locked'] = 0
            x['created_at'] = utc_now
            x['updated_at'] = utc_now

        order_serilizer = OrderSerializer(data=data['supplier_orders'], many=True)
        if order_serilizer.is_valid():
            order_serilizer.save()
            # logger.info(o)
        else:
            logger.info(order_serilizer.data)
            logger.error(order_serilizer.errors)
        logger.info(len(data['supplier_orders']))
        return Response('ok from viewsets')

    """
    update order detail
    """
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

        orders = {}

        for x in reader:
            # logger.info(x)
            if x['Order Number'] not in orders:
                orders[x['Order Number']] = { 'products':[], 'run':x['Delivery Run']}
            # if x['Order Number'] in orders else orders[x['Order Number']]
            p = {
                'code': x['Product Code'].strip("'"),
                'group': x['Product Group'],
                'name': x['Product Name'],
                'qty': x['Quantity'],
                'qtyType': x['Qty Type'],
                'customerNotes': x['Customer Notes'],
                'supplierNotes': x['Supplier Notes'],
                'status': x['Product Status'],
            }
            orders[x['Order Number']]['products'].append(p)
        logger.info(orders)

        return Response("ok from viewsets")


    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], url_path='detail-upload/')
    def uploadDetail(self, request):
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