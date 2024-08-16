import os

import requests
from requests.cookies import create_cookie


def remote_client():
    session = requests.session()
    c = create_cookie('_capsule-digital-template_session', os.environ.get('FRESHO_COOKIE'))

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Connection": "keep-alive",
    }
    session.headers.update(headers)
    session.cookies.set_cookie(c)

    return session


_client = remote_client()


def get_all_orders_by_date(delivery_date, per_page=200):
    """
    delivery_date : format yyyy-MM-dd
    """
    url = 'https://app.fresho.com/api/v1/my/suppliers/supplier_orders'

    # logger.info(request.GET['delivery_date'])
    params = {'page': 1,
              'per_page': per_page,
              'q[order_state]': 'all',
              'q[receiving_company_id]': '',
              'q[delivery_run_code]': '',
              'q[delivery_date]': delivery_date,
              'sort': '-delivery_date,-submitted_at,-order_number',
              }
    url = 'https://app.fresho.com/api/v1/my/suppliers/supplier_orders'
    return _client.get(url, params=params).json()
