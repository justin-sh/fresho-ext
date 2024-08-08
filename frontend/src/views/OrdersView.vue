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
        <b-form-datepicker
            id="datepicker"
            v-model="deliveryDate"
            :date-format-options="{ year: 'numeric', month: 'short', day: '2-digit', weekday: 'short' }">

        </b-form-datepicker>
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

  <b-card title="Orders">
    <b-card v-if="orders.length===0">
      <b-card-text>
        No orders. Would you please upload orders? or <b-button variant="outline-primary">Primary</b-button>
      </b-card-text>
      <b-form-file
          accept="text/csv"
          @input="readOrderFile"
          placeholder="Choose a order CSV file or drop it here..."
          drop-placeholder="Drop file here..."></b-form-file>

<!--      <div class="mt-3">Selected file: {{ orderFile ? orderFile.name : '' }}</div>-->
    </b-card>
  </b-card>
</template>

<script lang="ts" setup>
import {ref, watchEffect} from "vue";
import {CanceledError} from "axios";
import {uploadOrderCsv} from '@/api'

import {formatInTimeZone} from "date-fns-tz";

const localTZ = Intl.DateTimeFormat().resolvedOptions().timeZone

const deliveryDate = ref(formatInTimeZone(new Date(), localTZ, "yyyy-MM-dd"))
console.log(deliveryDate.value)
const customer = ref('')
const product = ref('')

const orders = ref([])

let abortController: AbortController | null = null;
watchEffect(async () => {

  if (abortController != null) {
    abortController.abort()
  }

  try {
    abortController = new AbortController()
    const url = `/v1/orders?date=${deliveryDate.value}&pn=${product.value}&cn=${customer.value}`
    console.log(url)
    // const data = (await http.get(url, {signal: abortController.signal})).data

    // orders.value = data.sort((o1, o2) => (o2.deliveryDate + (o2.deliveryAt || '')).localeCompare(o1.deliveryDate + (o1.deliveryAt || '')))
    // orders.value = orders.value.

  } catch (e) {
    if (!(e instanceof CanceledError)) {
      console.error(e)
    }
  } finally {
    abortController = null
  }
})

const readOrderFile = async (file: File | null) => {
  if (file === null) {
    console.log("no file selected")
    return
  }

  console.log(file.name)
  console.log(file.size)

  await uploadOrderCsv(file)
}
</script>