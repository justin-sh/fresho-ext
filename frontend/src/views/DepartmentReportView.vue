<template>
  <table class="w-100 mt-2 pagebreak" v-for="(v,k) in deptOrders">
    <caption class="caption-top fw-bold">{{ k }}</caption>
    <template v-for="run in ordered_run">
      <tr v-if="run in v">
        <td colspan="4" class="fw-bold pt-2">Run: {{ run }}</td>
      </tr>
      <template v-for="(pv,pk) in v[run]">
        <tr class="border fw-bold">
          <td colspan="4">{{ pk }}</td>
        </tr>
        <tr class="border" v-for="c in pv['cus_order']">
          <td class="border col-6">{{ c.c + ' - ' + run }}</td>
          <td class="border col fw-bold">{{ c.p.qty }}</td>
          <td class="border col">{{ c.p.qtyType }}</td>
          <td class="border col">
            <span v-if="c.p.supplierNotes" class="fw-bold">supplier:</span>{{ c.p.supplierNotes }}
            <span v-if="c.p.customerNotes" class="fw-bold">customer:</span>{{ c.p.customerNotes }}
          </td>
        </tr>
      </template>
    </template>
  </table>
</template>

<script setup lang="ts">
import {useRoute, useRouter} from "vue-router";

import {toDate} from 'date-fns-tz'

const router = useRouter()
const route = useRoute()

const orders = route.meta.orders
const ordered_run = route.meta.ordered_run
const deptOrders = {
  "BAND SAW": {},  // {"CT":{product_name:[{}]}}
  "BONING": {},
  "FROZEN PRODUCTS": {},
  "HOT POT": {},
  "SLICING BEEF": {},
  "SLICING CHICKEN": {},
}

console.log(orders)
const order_date = orders && orders.length > 0 ? toDate(orders[0].delivery_date) : new Date
orders?.forEach((order) => {
  const run = order.delivery_run
  order.products?.forEach((p) => {
    const pg = p.group.toUpperCase()
    if (pg in deptOrders) {
      deptOrders[pg][run] = deptOrders[pg][run] || {}
      deptOrders[pg][run][p.name] = deptOrders[pg][run][p.name] || {'cus_order': [], total: 0}
      deptOrders[pg][run][p.name]['cus_order'].push({c: `F${order.order_number} - ${order.receiving_company_name}`, p: p})
    }
  })
})

</script>

<style scoped>
@media print {
  .pagebreak {
    clear: both;
    break-after: page;
    font-size: 0.75rem;
  }

}
</style>