<template>
  <b-card
      title="Filters"
      tag="orders"
      class="mb-2"
  >
    <!-- <b-card-text>
      Some quick example text to build on the card title and make up the bulk of the card's content.
    </b-card-text> -->
    <b-form inline>
      <div class="flex justify-content-center col-sm-4 col-lg-2">
        <label for="datepicker" class="justify-content-start">Delivery date</label>
        <b-form-input
            type="date"
            id="datepicker"
            class="col-3"
            v-model="deliveryDate"
            :date-format-options="{ year: 'numeric', month: 'short', day: '2-digit', weekday: 'short' }">

        </b-form-input>
      </div>
      <div class="ml-3 align-content-center  col-md-4">
        <label for="customer" class="justify-content-start">Customer</label>
        <b-form-input id="customer" v-model="customer"></b-form-input>
      </div>
      <div class="ml-3  col-md-4">
        <label for="product" class="justify-content-start">Product</label>
        <b-form-input id="product" v-model="product"></b-form-input>
      </div>
    </b-form>
    <template #footer>
      <b-button variant="outline-primary"
                v-if="orders.length>0"
                :loading="init_loading"
                @click.stop="initOrder2Server">
        S1: re-INIT Order
      </b-button>
      <b-button variant="outline-primary"
                class="ms-2"
                v-if="orders.length>0"
                :loading="detail_syncing"
                @click.stop="syncDetails">
        S2: Sync Detail
      </b-button>
    </template>
  </b-card>

  <b-card>
    <b-card-title>
      Orders
      <span class="ms-2 inline fw-light fs-6">Total Count: {{ orders.length }}</span>
    </b-card-title>
    <div v-if="orders.length===0">
      No orders. Would you please upload orders? or
      <b-button variant="outline-primary" :loading="init_loading" @click.stop="initOrder2Server">INIT Order</b-button>
    </div>
    <b-table-simple v-if="orders.length>0"
                    striped hover
                    :items="orders"
                    :fields="fields">
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
                        variant="outline-primary">
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
                  <div class="col-1">{{ p.qty }} {{ p.qtyType }}</div>
                  <div class="col-1">{{ p.status }}</div>
                </div>
                <div v-if="!order.products">No Products</div>
              </b-card>
            </b-td>
          </b-tr>
        </template>
      </b-tbody>

      <!--      <template #row-details="row">-->
      <!--        <b-card>-->
      <!--          <b-row class="mb-2" v-for="p in row.item.products">-->
      <!--            <b-col>{{ p.group }}</b-col>-->
      <!--            <b-col sm="5" class="text-sm-right">{{ p.name }}</b-col>-->
      <!--            <b-col>{{ p.qty }} {{ p.qtyType }}</b-col>-->
      <!--            <b-col>{{ p.status }}</b-col>-->
      <!--          </b-row>-->

      <!--          <b-button size="sm" @click="" variant="outline-info">Hide Details</b-button>-->
      <!--        </b-card>-->
      <!--      </template>-->
    </b-table-simple>
  </b-card>
</template>

<script lang="ts" setup>
import {ref, watch} from "vue";
import {CanceledError} from "axios";
import {getOrdersWithFilters, initOrders, uploadOrdersCsv, syncOrderDetails} from '@/api'

import {formatInTimeZone} from "date-fns-tz";

const localTZ = Intl.DateTimeFormat().resolvedOptions().timeZone

const deliveryDate = ref(formatInTimeZone(new Date(), localTZ, "yyyy-MM-dd"))
const customer = ref('')
const product = ref('')

const orders = ref([])

const fields = [
  {key: 'order_number', label: 'Order#', sortable: true},
  {key: 'receiving_company_name', label: 'Customer', sortable: true},
  {key: 'state', label: 'State', sortable: true},
  {key: 'delivery_run', label: 'Run', sortable: true},
  {key: 'delivery_date', label: 'Date', sortable: true},
  // {key: 'show_details', label: 'Action'},
]

const init_loading = ref(false)
const detail_syncing = ref(false)

let abortController: AbortController | null = null;

const loading_data = async () => {

  if (abortController != null) {
    abortController.abort()
  }

  try {
    abortController = new AbortController()

    const data = (await getOrdersWithFilters({
          delivery_date: deliveryDate.value,
          customer: customer.value,
          product: product.value,
        },
        {signal: abortController.signal}
    )).data


    orders.value = data.map(function (x) {
      x.detailsShowing = false
      return x
    })

  } catch (e) {
    if (!(e instanceof CanceledError)) {
      console.error(e)
    }
  } finally {
    abortController = null
  }
}
const initOrder2Server = async () => {
  init_loading.value = true
  await initOrders(deliveryDate.value)
  init_loading.value = false
}
const syncDetails = async () => {
  detail_syncing.value = true
  await syncOrderDetails(deliveryDate.value)
  detail_syncing.value = false
}

const readOrderFile = async (file: File | null) => {
  if (file === null) {
    console.log("no file selected")
    return
  }

  console.log(file.name)
  console.log(file.size)

  await uploadOrdersCsv(file)
}

watch([deliveryDate, customer, product], async ([]) => {
  await loading_data()
}, {immediate: true})

</script>
<style scoped>
tbody tr {
  cursor: pointer;
}
</style>