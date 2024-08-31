<template>
  <b-card title="Filters" class="mb-2 filters">
    <b-form inline>
      <div class="row">
        <div class="col-3">
          <label for="datepicker">Delivery date</label>
          <b-form-input type="date" id="datepicker" class="col-3" v-model="deliveryDate"
            :date-format-options="{ year: 'numeric', month: 'short', day: '2-digit', weekday: 'short' }">
          </b-form-input>
        </div>
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
              <b-form-checkbox :value="r" :key="r" checked v-for="r in order_run" switch>{{ (r + "").substring(0, 5)
                }}</b-form-checkbox>
            </b-form-checkbox-group>
          </div>
        </div>
      </div>
    </b-form>

    <template #footer>
      <div class="row clear">
        <div class="col">
          <b-button variant="outline-primary" size="sm" :loading="init_loading" @click.stop="initOrder2Server">
            S1: re-INIT Order
          </b-button>
          <b-button variant="outline-primary" class="ms-2" size="sm" :loading="detail_syncing"
            @click.stop="syncDetails">
            S2: Sync Detail
          </b-button>
          <b-button variant="outline-primary" class="ms-2" size="sm" @click.stop="goDeptRepot">
            Dept Report
          </b-button>
          <b-button variant="outline-primary" class="ms-2" size="sm" :loading="syncing_del_proof"
            @click.stop="syncDeliveryProofs">
            Sync Delivery Proof
          </b-button>
        </div>
      </div>
    </template>
  </b-card>

  <b-card class="orders">
    <template #header>
      <div class="col align-content-center" ref="tableHeaderRefEl">
        <span class="fw-bold fs-4">Orders </span>
        <span class="inline fw-light fs-6" v-if="!data_loading">(Total {{ orders_backup.length }})</span>
      </div>

      <BFormRadioGroup v-model="page_size" :options="page_size_options" class="ms-3 align-content-center"
        value-field="item" text-field="name" />
    </template>
    <template #footer>
      <b-pagination v-model="currentPage" :total-rows="orders.length" :per-page="page_size" limit="7"
        @update:model-value="goTableHead" aria-controls="ordertable"></b-pagination>
    </template>

    <b-table id="ordertable" striped hover :current-page="currentPage" :per-page="page_size" :items="orders"
      :fields="fields">
      <template #cell(order_number)="row">
        <a :href="'https://app.fresho.com/supplier/orders/' + row.item.id" target="_blank">
          {{ row.value }}
        </a>
      </template>
      <template #cell(show_details)="row">
        <b-button size="sm" @click="row.toggleDetails" class="mr-2" variant="light">
          {{ row.detailsShowing ? 'Hide' : 'Show' }} Details
        </b-button>
      </template>
      <template #row-details="row">
        <b-card>
          <div class="row" v-for="p in row.item.products" :key="p.name">
            <div class="col-2">{{ p.group }}</div>
            <div class="col">{{ p.name }}</div>
            <div class="col-2">{{ p.qty }} {{ p.qtyType }}</div>
            <div class="col-1">{{ p.status }}</div>
          </div>
          <div v-if="!row.item.products">No Products</div>
        </b-card>
      </template>
    </b-table>
  </b-card>
</template>

<script lang="ts" setup>
import { ref, shallowRef, watch } from "vue";
import { CanceledError } from "axios";
import { getOrdersWithFilters, initOrders, syncOrderDetails, syncOrderDeliveryProofs } from '@/api'

import { formatInTimeZone, toDate } from "date-fns-tz";
import { onBeforeRouteLeave, useRouter } from "vue-router";

const router = useRouter()

const localTZ = Intl.DateTimeFormat().resolvedOptions().timeZone

const deliveryDate = shallowRef(formatInTimeZone(new Date(), localTZ, "yyyy-MM-dd"))
const customer = shallowRef('')
const product = shallowRef('')
const status = shallowRef(['submitted', 'accepted', 'invoiced', 'paid'])
const credit = shallowRef('no')
const order_run = ['ED', 'EE', 'RM1', 'CT', 'S', 'N', 'LE', 'RM2', 'W', 'PU', 'CA', 'EA', '~NR']
const runs = shallowRef([])

const orders = shallowRef([])
let orders_backup = []

const fields = [
  { key: 'order_number', label: 'Order#', sortable: true },
  { key: 'delivery_date_md', label: 'Date', sortable: true },
  { key: 'receiving_company_name', label: 'Customer', sortable: true },
  { key: 'state', label: 'State', sortable: true },
  { key: 'delivery_by', label: 'By', sortable: true },
  { key: 'delivery_at_hm', label: 'At', sortable: true },
  { key: 'delivery_proof', label: 'Proof', sortable: true },
  { key: 'show_details', label: 'Action' },
]

const init_loading = shallowRef(false)
const detail_syncing = shallowRef(false)
const syncing_del_proof = shallowRef(false)
const data_loading = shallowRef(false)

const currentPage = shallowRef(1)
const page_size = shallowRef(30)
const page_size_options = [
  { item: 30, name: '30' },
  { item: 50, name: '50' },
  { item: 999, name: 'all' }
]


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
      { signal: abortController.signal }
    )).data


    orders.value = data.map(function (x) {
      x.detailsShowing = false
      x.delivery_date_md = formatInTimeZone(new Date(x.delivery_date), localTZ, "MM-dd")
      x.delivery_at_hm = x.delivery_at ? formatInTimeZone(new Date(x.delivery_at), localTZ, "HH:mm") : ''
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
  router.push({ name: 'dept-report' })
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
  runs_old = runs_old || []
  if (runs_new.toString() !== runs_old.toString()) {
    const _s = new Date().getTime()
    let x = runs_new.length === 0 ? orders_backup : orders_backup.filter((o) => runs.value.includes(o.delivery_run))
    console.log("filter data in js:" + (new Date().getTime() - _s))
    orders.value = x
    setTimeout(() => {
      console.log("update page:" + (new Date().getTime() - _s))
    }, 0);
  } else {
    console.log('loading data')
    await loading_data()
  }
}, { immediate: true })

const tableHeaderRefEl = ref<HTMLElement | null>(null)
const goTableHead = (page: number) => {
  console.log(page)
  tableHeaderRefEl.value?.scrollIntoView({ behavior: 'smooth' })
}

</script>
<style scoped>
tbody tr {
  cursor: pointer;
}

.text-right {
  text-align: right;
}

:deep(.card-header) {
  display: flex;
}

.card-header ul {
  margin-bottom: 0;
}

.orders :deep(.card-footer) {
  display: flex;
  justify-content: center;
}

.card-footer ul {
  margin-bottom: 0;
}
</style>