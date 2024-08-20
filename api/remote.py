import logging
import os
import time

import requests
from bs4 import BeautifulSoup as BS
from requests.cookies import create_cookie

logger = logging.getLogger(__file__)


def new_client():
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


class RemoteClient():
    _client = None

    @property
    def client(self):
        if self._client:
            return self._client
        self._client = new_client()
        return self._client


client = RemoteClient().client


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
    rv = client.get(url, params=params).json()
    if 'error' in rv:
        raise Exception("No login information. Plz check the env config.")
    return rv


def get_order_details_by_order_ids(ids):
    # step 1: submit job
    # result: {"job_id":"955c715dd02a9b5f9a3c860d"}

    # get fresho-app-csrf-token
    rv = client.get('https://app.fresho.com/api/v1/companies/b181ee08-2214-46ec-ad1e-926a2bbfb8fb').json()
    csrf_token = client.cookies.get('fresho-app-csrf-token')

    url1 = 'https://app.fresho.com/api/v1/my/suppliers/reports'
    params = {
        "type": "product-totals-by-customer-batch",
        "args": {
            "selected_order_ids": ids,  # ["461309ec-43ed-4ade-b88c-2c92e3040414"],
            "pagination": True,
            "supplied_statuses": ["supplied"],
            "format": "CSV"  # PDF CSV
        }
    }

    ret1 = client.post(url1, json=params, headers={'x-csrf-token': csrf_token}).json()

    # step 2: get job result
    # result: {
    #     "result": {
    #         "result_code": "OK",
    #         "result_data": {
    #             "report": {
    #                 "temporary_url": "https://s3.ap-southeast-2.amazonaws.com/public.temp-document-storage.prd.fresho-app/2024-08-17-utc/2a390520-dc25-40e2-9e03-008c6a281264_house-of-carnivore-pty-ltd_product_totals_by_customer.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256\u0026X-Amz-Credential=AKIASYIRAQ3FR36Z6DSG%2F20240817%2Fap-southeast-2%2Fs3%2Faws4_request\u0026X-Amz-Date=20240817T000914Z\u0026X-Amz-Expires=86400\u0026X-Amz-SignedHeaders=host\u0026X-Amz-Signature=dc69dd71262db37bec01bbe2155504fc2b8f669ecf9702ed9c8cb5d56ea2103d",
    #                 "download_filename": "house-of-carnivore-pty-ltd_product_totals_by_customer.csv"
    #             }
    #         }
    #     },
    #     "jid": "a93bd20153f433bc797c307b",
    #     "update_time": "1723853354",
    #     "worker": "AsyncJobs::Reports::ReportWorker",
    #     "status": "complete",  working
    #     "args": "[{\"type\":\"product-totals-by-customer-batch\",\"args\":{\"selected_order_ids\":[\"461309ec-43ed-4ade-b88c-2c92e3040414\"],\"pagination\":true,\"supplied_statuses\":[\"supplied\"],\"format\":\"CSV\"},\"selling_company_id\":\"b181ee08-2214-46ec-ad1e-926a2bbfb8fb\"}]"
    # }
    ret2 = {"status": "working", "result": {"result_data": {"report": {"temporary_url": ''}}}}
    loop_max_cnt = 0
    while ret2['status'] == 'working' and loop_max_cnt < 10:
        time.sleep(0.08)
        loop_max_cnt += 1
        url2 = 'https://app.fresho.com/api/v1/public/jobs/' + ret1['job_id']
        ret2 = client.get(url2).json()
        logger.debug(ret2)

    # step3 : read csv file
    file_url = ret2['result']['result_data']['report']['temporary_url']
    r = requests.get(file_url)
    r.encoding = 'utf-8'

    # logger.debug(r.text)
    return r.text


def get_order_delivery_url():
    url0 = 'https://app.fresho.com/companies/b181ee08-2214-46ec-ad1e-926a2bbfb8fb/selling/deliveries'
    rv0 = client.get(url0).text
    bs = BS(rv0, 'lxml')
    url = bs.select_one('a[data-fresho-item="view-recent-pods"]').attrs['href']
    # logger.info(url)
    return 'https://app.fresho.com' + url


def get_recently_delivery_proof():
    url = get_order_delivery_url()
    rv = client.get(url).text
    bs = BS(rv, 'lxml')
    pods = bs.select('div.test-recent-deliveries-table tbody>tr')
    data = {}
    for pod in pods:
        h = pod.select_one('a')
        proof_url = h.attrs['href'].strip()
        order_no = h.string.strip()[1:]
        delivery_by = pod.select_one('td[data-title="Delivered By"]').string.strip()
        delivery_proof = pod.select_one('td[data-title="Proof Collected"]').string.strip()
        delivery_at = pod.select_one('span.test-timestamp').attrs['data-timestamp'].strip()
        data[order_no] = {'url': proof_url,
                          'delivery_by': delivery_by,
                          'delivery_proof': delivery_proof,
                          'delivery_at': delivery_at}
        # logger.info('%s %s %s %s' % (proof_url, order_no, delivery_by, delivery_at))
    return data
