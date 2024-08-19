import csv
import datetime
import io
import logging
from io import TextIOWrapper

from django.contrib.auth.models import User
from django.utils.datastructures import MultiValueDict
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from orders.models import Order, DeliveryRun
from . import remote
from .serializers import UserSerializer, OrderSerializer

logger = logging.getLogger(__file__)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]


def process_csv_order_details(f):
    reader = csv.DictReader(f)
    to_updated_orders = {}

    for x in reader:
        if "'STD_FREIGHT_BOX'" == x['Product Code']:
            continue
        if x['Order Number'] not in to_updated_orders:
            if float(x['Quantity']) < 0:
                x['Delivery Run'] = 'No Run Assigned'
            to_updated_orders[x['Order Number']] = {'products': [], 'run': x['Delivery Run']}
            # logger.info(x)
            # logger.info(orders[x['Order Number']])
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
        to_updated_orders[x['Order Number']]['products'].append(p)

    return to_updated_orders


def update_order_details(to_updated_orders):
    runs = {x.name: x for x in DeliveryRun.objects.all()}
    ret = {'failure': {'cnt': 0, 'data': []}, 'success': {'cnt': 0}}
    for k, v in to_updated_orders.items():
        # logger.info(k + '=>' + json.dumps(v))
        try:
            order = Order.objects.get(order_number=k)
        except Exception as e:
            ret['failure']['cnt'] += 1
            ret['failure']['data'].append({'orderNo': k, 'msg': e.args})
            logger.error("update order products for %s failed" % k, e.args)
        else:
            order.products = v['products']
            order.delivery_run = runs[v['run']].code
            order.save()
            ret['success']['cnt'] += 1
    return ret


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        orders = Order.objects
        del_date = self.request.query_params.get('delivery_date')
        customer = self.request.query_params.get('customer')
        product = self.request.query_params.get('product')
        order_status = self.request.query_params.getlist('status[]')
        if del_date:
            orders = orders.filter(delivery_date=del_date)
        if customer:
            orders = orders.filter(receiving_company_name__icontains=customer)
        if product:
            orders = orders.filter(products__icontains=product)
        if order_status:
            orders = orders.filter(state__in=order_status)
        if not del_date and not customer and not product:
            return orders.none()
        return orders.order_by('-delivery_date', 'receiving_company_name', 'delivery_run')[:200]

    @action(detail=False)
    def init(self, request):
        data = remote.get_all_orders_by_date(request.GET['delivery_date'])
        utc_now = datetime.datetime.now(datetime.UTC)
        ret = {'success': {'cnt': 0}, 'failure': {'cnt': 0, 'data': []}, 'duplicate': {'cnt': 0}, 'update': {'cnt': 0}}
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
                    try:
                        odr = Order.objects.get(id=x['id'])
                        if odr.state in ('invoiced', 'cancelled', 'paid'):
                            ret['duplicate']['cnt'] += 1
                            continue
                        x['products'] = odr.products
                        update_ser = OrderSerializer(odr, data=x)
                        if update_ser.is_valid():
                            update_ser.save()
                            ret['update']['cnt'] += 1
                        else:
                            ret['failure']['cnt'] += 1
                            ret['failure']['data'].append(
                                {'name': x['receiving_company_name'], 'msg': order_ser.errors}
                            )
                    except Exception as e:
                        ret['duplicate']['cnt'] += 1
                else:
                    ret['failure']['cnt'] += 1
                    ret['failure']['data'].append({'name': x['receiving_company_name'], 'msg': order_ser.errors})
                    logger.error("save order for %s failed" % x['receiving_company_name'], order_ser.errors)

        # logger.info(len(data['supplier_orders']))
        return Response(ret)

    @action(detail=False, permission_classes=[permissions.AllowAny], url_path='sync-detail')
    def update_order_details_by_download_product_total_file(self, reqest):
        delivery_date = self.request.query_params.get('delivery_date')
        orders = Order.objects.filter(delivery_date=delivery_date)
        ids = [order.id for order in orders]
        order_details = remote.get_order_details_by_order_ids(ids)
        to_updated_orders = process_csv_order_details(io.StringIO(order_details))

        ret = update_order_details(to_updated_orders)

        return Response(ret)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], url_path='update-details')
    def update_order_details_by_upload_product_total_file(self, request):
        """
        update order detail
        """
        # logger.info("---------")
        files: MultiValueDict = request.FILES
        if files and len(files) != 1:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        order_file = files.get("orderFile")

        # max size : 1M
        if order_file.size > 1 * 1024 * 1024:
            return Response("File is too big", status=status.HTTP_400_BAD_REQUEST)

        to_updated_orders = process_csv_order_details(TextIOWrapper(order_file, encoding="utf-8", newline=""))

        ret = update_order_details(to_updated_orders)

        return Response(ret)

        # f = TextIOWrapper(order_file, encoding="utf-8", newline="")
        # reader = csv.DictReader(f)
        # # logger.info(reader.fieldnames)
        #
        # orders = {}
        #
        # for x in reader:
        #     if "'STD_FREIGHT_BOX'" == x['Product Code']:
        #         continue
        #     if x['Order Number'] not in orders:
        #         if float(x['Quantity']) < 0:
        #             x['Delivery Run'] = 'No Run Assigned'
        #         orders[x['Order Number']] = {'products': [], 'run': x['Delivery Run']}
        #         # logger.info(x)
        #         # logger.info(orders[x['Order Number']])
        #     p = {
        #         'code': x['Product Code'].strip("'"),
        #         'group': x['Product Group'],
        #         'name': x['Product Name'],
        #         'qty': float(x['Quantity']),
        #         'qtyType': x['Qty Type'],
        #         'customerNotes': x['Customer Notes'],
        #         'supplierNotes': x['Supplier Notes'],
        #         'status': x['Product Status'],
        #     }
        #     orders[x['Order Number']]['products'].append(p)
        #
        # runs = {x.name: x for x in DeliveryRun.objects.all()}
        # ret = {'failure': {'cnt': 0, 'data': []}, 'success': {'cnt': 0}}
        # for k, v in orders.items():
        #     # logger.info(k + '=>' + json.dumps(v))
        #     try:
        #         order = Order.objects.get(order_number=k)
        #     except Exception as e:
        #         ret['failure']['cnt'] += 1
        #         ret['failure']['data'].append({'orderNo': k, 'msg': e.args})
        #         logger.error("update order products for %s failed" % k, e.args)
        #     else:
        #         order.products = v['products']
        #         order.delivery_run = runs[v['run']].code
        #         order.save()
        #         ret['success']['cnt'] += 1
        #
        # return Response(ret)

    @action(detail=False, permission_classes=[permissions.AllowAny], url_path='sync-delivery-proof')
    def update_order_delivery_proof(self, request):
        # logger.info("step1: get delivery proof page url")
        data = remote.get_recently_delivery_proof()
        ret = {'failure': {'cnt': 0, 'data': []}, 'duplicate': {'cnt': 0}, 'success': {'cnt': 0}}
        for order_no, v in data.items():
            try:
                order = Order.objects.get(order_number=order_no)
            except Exception as e:
                ret['failure']['cnt'] += 1
                ret['failure']['data'].append({'orderNo': order_no, 'msg': e.args})
                logger.error("update order products for %s failed" % order_no, e.args)
            else:
                if order.delivery_proof_url:
                    ret['duplicate']['cnt'] += 1
                else:
                    order.delivery_by = v['delivery_by']
                    order.delivery_at = datetime.datetime.fromisoformat(v['delivery_at'])
                    order.delivery_proof_url = v['url']
                    order.save()
                    ret['success']['cnt'] += 1

        return Response(ret)
