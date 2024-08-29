<template>
  <b-card
      title="Filters"
      tag="orders"
      class="mb-2"
  >
    <b-form inline>
      <div class="row">
        <div class="col-3">
          <label for="datepicker">Delivery date</label>
          <b-form-input
              type="date"
              id="datepicker"
              class="col-3"
              v-model="deliveryDate"
              :date-format-options="{ year: 'numeric', month: 'short', day: '2-digit', weekday: 'short' }">
          </b-form-input>
        </div>
      <!-- </div> -->
      <!-- <div class="row"> -->
        <div class="ml-3 align-content-center col">
          <label for="customer" class="justify-content-start">Customer</label>
          <b-form-input id="customer" v-model="customer"></b-form-input>
        </div>
        <div class="ml-3  col">
          <label for="product" class="justify-content-start">Product</label>
          <b-form-input id="product" v-model="product"></b-form-input>
        </div>
      </div>
      <div class="row">
        <div class="col">
          <label>State</label>
          <div class="d-flex">
            <b-form-checkbox-group v-model="status">
              <b-form-checkbox value="in_progress" switch>Process</b-form-checkbox>
              <b-form-checkbox value="submitted" switch>Submitted</b-form-checkbox>
              <b-form-checkbox value="accepted" switch>Accepted</b-form-checkbox>
              <b-form-checkbox value="invoiced" switch>Invoiced</b-form-checkbox>
              <b-form-checkbox value="paid" switch>Paid</b-form-checkbox>
              <b-form-checkbox value="cancelled" switch>Cancelled</b-form-checkbox>
            </b-form-checkbox-group>
            <b-form-checkbox v-model="credit" value="yes" uncheckedValue="no" switch>Credit</b-form-checkbox>
          </div>
        </div>
      </div>
    <div class="row">
      <div class="col">
          <label>Run</label>
          <div class="d-flex">
            <b-form-checkbox-group v-model="runs" class="run-group">
              <b-form-checkbox :value="r" checked v-for="r in order_run" switch>{{ (r+"").substr(0,5) }}</b-form-checkbox>
            </b-form-checkbox-group>
          </div>
      </div>
    </div>
    </b-form>

    <template #footer>
      <div class="row clear">
        <div class="col">
          <b-button variant="outline-primary"
                    size="sm"
                    :loading="init_loading"
                    @click.stop="initOrder2Server">
            S1: re-INIT Order
          </b-button>
          <b-button variant="outline-primary"
                    class="ms-2"
                    size="sm"
                    :loading="detail_syncing"
                    @click.stop="syncDetails">
            S2: Sync Detail
          </b-button>
          <b-button variant="outline-primary"
                    class="ms-2"
                    size="sm"
                    @click.stop="goDeptRepot">
            Dept Report
          </b-button>
          <b-button variant="outline-primary"
                    class="ms-2"
                    size="sm"
                    :loading="syncing_del_proof"
                    @click.stop="syncDeliveryProofs">
            Sync Delivery Proof
          </b-button>
        </div>
      </div>
    </template>
  </b-card>

  <b-card>
    <template #header>
      <div class="col-4 align-content-center">
        <span class="fw-bold fs-4">Orders </span>
        <span class="inline fw-light fs-6" v-if="!data_loading">(Total {{ orders.length }})</span>
      </div>
    </template>
    <b-table-simple striped hover>
      <b-thead>
        <b-tr>
          <b-td v-for="h in fields">
            {{ h['label'] }}
          </b-td>
          <b-td>Action</b-td>
        </b-tr>
      </b-thead>
      <b-tbody>
        <template v-for="order in orders">
          <b-tr>
            <b-td v-for="h in fields">
              <template v-if="h.key === 'order_number'">
                <a :href="'https://app.fresho.com/supplier/orders/'+order.id" target="_blank">
                  {{ order[h['key']] }}
                </a>
              </template>
              <template v-else>
                {{ order[h['key']] }}
              </template>
            </b-td>
            <b-td>
              <b-button size="sm" @click="order.detailsShowing=!order.detailsShowing" class="mr-2"
                        variant="light">
                {{ order.detailsShowing ? 'Hide' : 'Show' }} Details
              </b-button>
            </b-td>
          </b-tr>
          <b-tr v-if="order.detailsShowing">
            <b-td :colspan="fields.length+1">
              <b-card>
                <div class="row" v-for="p in order.products">
                  <div class="col-2">{{ p.group }}</div>
                  <div class="col">{{ p.name }}</div>
                  <div class="col-2">{{ p.qty }} {{ p.qtyType }}</div>
                  <div class="col-1">{{ p.status }}</div>
                </div>
                <div v-if="!order.products">No Products</div>
              </b-card>
            </b-td>
          </b-tr>
        </template>

        <b-tr v-if="data_loading">
          <b-td :colspan="fields.length+1" class="text-center">
            <b-spinner label="Loading..."></b-spinner>
          </b-td>
        </b-tr>
        <b-tr v-if="!data_loading && orders.length===0">
          <b-td :colspan="fields.length+1" class="text-center">
            No Orders.
          </b-td>
        </b-tr>
      </b-tbody>
    </b-table-simple>
  </b-card>
</template>

<script lang="ts" setup>
import {ref, shallowRef, watch} from "vue";
import {CanceledError} from "axios";
import {getOrdersWithFilters, initOrders, syncOrderDetails, syncOrderDeliveryProofs} from '@/api'

import {formatInTimeZone, toDate} from "date-fns-tz";
import {onBeforeRouteLeave, useRouter} from "vue-router";

const router = useRouter()

const localTZ = Intl.DateTimeFormat().resolvedOptions().timeZone

const deliveryDate = shallowRef(formatInTimeZone(new Date(), localTZ, "yyyy-MM-dd"))
const customer = shallowRef('')
const product = shallowRef('')
const status = shallowRef(['submitted', 'accepted', 'invoiced', 'paid'])
const credit = shallowRef('no')
const order_run = ['ED', 'EE', 'RM1', 'CT', 'S', 'N', 'LE', 'RM2', 'W', 'PU', 'CA', 'EA', '~NR']
const runs=shallowRef(order_run)

const orders = shallowRef([])
let orders_backup = []

const fields = [
  {key: 'order_number', label: 'Order#', sortable: true},
  {key: 'delivery_date_md', label: 'Date', sortable: true},
  {key: 'receiving_company_name', label: 'Customer', sortable: true},
  {key: 'state', label: 'State', sortable: true},
  {key: 'delivery_by', label: 'By', sortable: true},
  {key: 'delivery_at_hm', label: 'At', sortable: true},
  {key: 'delivery_proof', label: 'Proof', sortable: true},
  // {key: 'show_details', label: 'Action'},
]

const init_loading = shallowRef(false)
const detail_syncing = shallowRef(false)
const syncing_del_proof = shallowRef(false)
const data_loading = shallowRef(false)

let abortController: AbortController | null = null;

const loading_data = async () => {

  data_loading.value = true
  orders.value = []
  orders_backup = orders.value
  if (abortController != null) {
    abortController.abort()
  }

  try {
    abortController = new AbortController()

    const data = (await getOrdersWithFilters({
          delivery_date: deliveryDate.value,
          customer: customer.value,
          product: product.value,
          status: status.value,
          credit: credit.value,
        },
        {signal: abortController.signal}
    )).data


    orders.value = data.map(function (x) {
      x.detailsShowing = false
      x.delivery_date_md = formatInTimeZone(new Date(x.delivery_date), localTZ, "MM-dd")
      x.delivery_at_hm = x.delivery_at?formatInTimeZone(new Date(x.delivery_at), localTZ, "HH:mm"):''
      return x
    })

    orders_backup = orders.value

  } catch (e) {
    if (!(e instanceof CanceledError)) {
      console.error(e)
    }
  } finally {
    abortController = null
    data_loading.value = false
  }
}
const initOrder2Server = async () => {
  init_loading.value = true
  await initOrders(deliveryDate.value)
  init_loading.value = false
  await loading_data()
}
const syncDetails = async () => {
  detail_syncing.value = true
  await syncOrderDetails(deliveryDate.value)
  detail_syncing.value = false
  await loading_data()
}
const syncDeliveryProofs = async () => {
  syncing_del_proof.value = true
  await syncOrderDeliveryProofs()
  syncing_del_proof.value = false
  await loading_data()
}

const goDeptRepot = () => {
  router.push({name: 'dept-report'})
}

onBeforeRouteLeave((to, before) => {
  if (to.name == 'dept-report') {
    to.meta.orders = orders.value

    const weedDay = toDate(deliveryDate.value).getDay()
    if ([2, 4].includes(weedDay)) {
      to.meta.ordered_run = ['ED', 'EE', 'RM1', 'CT', 'S', 'N', 'LE', 'RM2', 'W', 'PU', 'CA', 'EA', '~NR']
    } else {
      to.meta.ordered_run = ['ED', 'EE', 'RM1', 'S', 'CT', 'N', 'LE', 'RM2', 'W', 'PU', 'CA', 'EA', '~NR']
    }
  }
})

watch([deliveryDate, customer, product, status, credit, runs], async ([deliveryDate_new, customer_new, product_new, status_new, credit_new, runs_new],
  [deliveryDate2, customer2, product2, status2, credit2, runs_old]) => {
   if(runs_old&&runs_new!=runs_old){
      const _s = new Date().getTime()
      let x = orders_backup.filter((o)=>runs.value.includes(o.delivery_run))
      console.log(new Date().getTime() - _s)
      console.log(x.length)
      orders.value = x
    }else{
      await loading_data()
    }
}, {immediate: true})

</script>
<style scoped>
tbody tr {
  cursor: pointer;
}

.text-right {
  text-align: right;
}
</style>