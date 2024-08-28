<template>

  <b-card
      title="Filters"
      class="mb-2 filters">
    <div class="row">
      <div class="col">
          <label>Run</label>
          <div class="d-flex">
            <b-form-checkbox-group v-model="runs" class="run-group">
              <b-form-checkbox :value="r" checked v-for="r in ordered_run" switch>{{ (r+"").substr(0,5) }}</b-form-checkbox>
            </b-form-checkbox-group>
          </div>
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
          </div>
      </div>
    </div>
  </b-card>

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
import {ref, watch, reactive} from "vue";
import {useRoute, useRouter} from "vue-router";

import {toDate} from 'date-fns-tz'

const router = useRouter()
const route = useRoute()

const orders = route.meta.orders
const ordered_run = route.meta.ordered_run


const status=ref(["accepted"])
const runs=ref(ordered_run)

const deptOrders = reactive({})


watch([status, runs], ([]) => {
  deptOrders["BAND SAW"] = {}
  deptOrders["BONING"] = {}
  deptOrders["FROZEN PRODUCTS"] = {}
  deptOrders["HOT POT"] = {}
  deptOrders["SLICING BEEF"] = {}
  deptOrders["SLICING CHICKEN"] = {}
  orders?.forEach((order) => {
  if(status.value.includes(order.state) && runs.value.includes(order.delivery_run)){
    const run = order.delivery_run
    order.products?.forEach((p) => {
      const pg = p.group.toUpperCase()
      if (pg in deptOrders) {
        deptOrders[pg][run] = deptOrders[pg][run] || {}
        deptOrders[pg][run][p.name] = deptOrders[pg][run][p.name] || {'cus_order': [], total: 0}
        deptOrders[pg][run][p.name]['cus_order'].push({c: `F${order.order_number} - ${order.receiving_company_name}`, p: p})
      }
      })
    }
    })
}, {immediate: true})

</script>

<style scoped>
@media print {
  .pagebreak {
    clear: both;
    break-after: page;
    font-size: 0.75rem;
  }

  .filters{
    display: none;
  }

}

</style>