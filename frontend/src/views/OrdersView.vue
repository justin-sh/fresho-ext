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
      <div class="flex justify-content-center">
        <label for="datepicker" class="justify-content-start">Delivery date</label>
        <b-form-input
            type="date"
            id="datepicker"
            v-model="deliveryDate"
            :date-format-options="{ year: 'numeric', month: 'short', day: '2-digit', weekday: 'short' }">

        </b-form-input>
      </div>
      <div class="ml-3 align-content-center">
        <label for="customer" class="justify-content-start">Customer</label>
        <b-form-input id="customer" v-model="customer"></b-form-input>
      </div>
      <div class="ml-3">
        <label for="product" class="justify-content-start">Product</label>
        <b-form-input id="product" v-model="product"></b-form-input>
      </div>
    </b-form>
  </b-card>

  <b-card>
    <b-card-title>
      Orders
      <b-button variant="outline-primary"
                v-if="orders.length>0"
                :loading="init_loading"
                @click.stop="initOrder2Server">
        re-INIT Order
      </b-button>
    </b-card-title>
    <!--    <b-card>-->
    <div v-if="orders.length===0">
      No orders. Would you please upload orders? or
      <b-button variant="outline-primary" :loading="init_loading" @click.stop="initOrder2Server">INIT Order</b-button>
    </div>
    <!--      <b-form-file-->
    <!--          accept="text/csv"-->
    <!--          @update:model-value="readOrderFile"-->
    <!--          placeholder="Choose a order CSV file or drop it here..."-->
    <!--          drop-placeholder="Drop file here..."></b-form-file>-->
    <!--    </b-card>-->
    <!--    https://bootstrap-vue.org/docs/components/table#complete-example -->
    <b-table v-if="orders.length>0"
             :busy="loading_data"
             striped hover
             :items="orders"
             :fields="fields">
      <template #cell(order_number)="row">
        <a :href="'https://app.fresho.com/supplier/orders/'+row.item.id" target="_blank"> {{ row.value }}</a>
      </template>
      <template #cell(show_details)="row">
        <b-button size="sm" @click="row.toggleDetails" class="mr-2" variant="outline-info">
          {{ row.detailsShowing ? 'Hide' : 'Show'}} Details
        </b-button>
      </template>
      <template #row-details="row">
        <b-card>
          <b-row class="mb-2" v-for="p in row.item.products">
            <b-col>{{ p.group }}</b-col>
            <b-col sm="5" class="text-sm-right">{{ p.name }}</b-col>
            <b-col>{{ p.qty }} {{ p.qtyType}}</b-col>
            <b-col>{{ p.status }}</b-col>
          </b-row>

          <b-button size="sm" @click="row.toggleDetails" variant="outline-info">Hide Details</b-button>
        </b-card>
      </template>
    </b-table>
  </b-card>
</template>

<script lang="ts" setup>
import {ref, watchEffect} from "vue";
import {CanceledError} from "axios";
import {getOrdersWithFilters, initOrders, uploadOrdersCsv} from '@/api'

import {formatInTimeZone} from "date-fns-tz";

const localTZ = Intl.DateTimeFormat().resolvedOptions().timeZone

const deliveryDate = ref(formatInTimeZone(new Date(), localTZ, "yyyy-MM-dd"))
// console.log(deliveryDate.value)
const customer = ref('')
const product = ref('')

const orders = ref([])

const fields = [
  {key: 'order_number', label: 'Order#', sortable:true},
  {key: 'receiving_company_name', label: 'Customer', sortable:true},
  {key: 'delivery_run', label: 'Run', sortable:true},
  {key: 'delivery_date', sortable:true},
  {key: 'show_details', label: 'Action'},
]

const init_loading = ref(false)
const loading_data = ref(false)

let abortController: AbortController | null = null;
watchEffect(async () => {

  if (abortController != null) {
    abortController.abort()
  }

  try {
    loading_data.value = true
    abortController = new AbortController()

    const data = (await getOrdersWithFilters({
          delivery_date: deliveryDate.value,
          customer: customer.value,
          product: product.value,
        },
        {signal: abortController.signal}
    )).data

    orders.value = data

  } catch (e) {
    if (!(e instanceof CanceledError)) {
      console.error(e)
    }
  } finally {
    abortController = null
    loading_data.value = false
  }
})

const initOrder2Server = async () => {
  init_loading.value = true
  await initOrders(deliveryDate.value)
  init_loading.value = false
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

const gotoFresho = function (item) {
  // console.log(item['id'])
  // console.log(item.id)

  const url = 'https://app.fresho.com/supplier/orders/' + item.id// + '?company_id=9d10a274-72c3-43a6-92b3-87cde4703ea4&mode=sell'
  window.open(url, '_blank')
}
</script>
<style scoped>
tr {
  cursor: pointer;
}
</style>