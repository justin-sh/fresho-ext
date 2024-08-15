import csv
import datetime
import json
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
        ret = {'success': {'cnt': 0}, 'failure': {'cnt': 0, 'data': []}, 'duplicate': {'cnt': 0}}
        for x in data['supplier_orders']:
            x['payable_total_in_cents'] = x['cached_payable_total_in_cents'] \
                if x['cached_payable_total_in_cents'] else 0
            x['locked'] = 0
            x['created_at'] = utc_now
            x['updated_at'] = utc_now

            order_ser = OrderSerializer(data=x)
            if order_ser.is_valid():
                try:
                    order_ser.save()
                    ret['success']['cnt'] += 1
                except Exception as ex:
                    ret['failure']['cnt'] += 1
                    ret['failure']['data'].append({'name': x['receiving_company_name'], 'msg': ex.args})
                    logger.error("save order failed for %s" % x['receiving_company_name'], ex)
            else:
                if ('id' in order_ser.errors or 'unique' == order_ser.errors['id'].code) or \
                        not ('order_number' in order_ser.errors or 'unique' == order_ser.errors['id'].code):
                    ret['duplicate']['cnt'] += 1
                else:
                    ret['failure']['cnt'] += 1
                    ret['failure']['data'].append({'name': x['receiving_company_name'], 'msg': order_ser.errors})
                    logger.error("save order for %s failed" % x['receiving_company_name'], order_ser.errors)

        # logger.info(len(data['supplier_orders']))
        return Response(ret)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def upload(self, request):
        """
        update order detail
        """
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
            if "'STD_FREIGHT_BOX'" == x['Product Code']:
                continue
            if x['Order Number'] not in orders:
                orders[x['Order Number']] = {'products': [], 'run': x['Delivery Run']}
            p = {
                'code': x['Product Code'].strip("'"),
                'group': x['Product Group'],
                'name': x['Product Name'],
                'qty': float(x['Quantity']),
                'qtyType': x['Qty Type'],
                'customerNotes': x['Customer Notes'],
                'supplierNotes': x['Supplier Notes'],
                'status': x['Product Status'],
            }
            orders[x['Order Number']]['products'].append(p)

        ret = {'failure':{'cnt': 0, 'data': []}, 'success': {'cnt': 0}}
        for k, v in orders.items():
            logger.info(k + '=>' + json.dumps(v))
            try:
                order = Order.objects.get(order_number=k)
            except Exception as e:
                ret['failure']['cnt'] += 1
                ret['failure']['data'].append({'orderNo': k, 'msg': ex.args})
                logger.error("update order products for %s failed" % k, ex.args)
            else:
                order.products = v
                order.save()
                ret['success']['cnt'] += 1

        return Response(ret)

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
