<template>
	<b-card>
      <b-card-text>
        Upload orders:

      <b-button variant="outline-primary" :loading="init_loading" @click.stop="uploadOrderDetail2Server">Upload</b-button>      </b-card-text>
      <b-form-file
          accept="text/csv"
          @update:model-value="readOrderFile"
          placeholder="Choose a order CSV file or drop it here..."
          drop-placeholder="Drop file here...">
      </b-form-file>

    </b-card>
</template>

<script lang="ts" setup>
import { ref } from "vue"
import {uploadOrdersCsv} from '@/api'

const init_loading = ref(false)

let detailFile = null;

const uploadOrderDetail2Server = async () => {
  init_loading.value = true
  // await initOrders(deliveryDate.value)
  console.log(detailFile.name)
  console.log(detailFile.size)
  await uploadOrdersCsv(detailFile)
  init_loading.value = false
}

const readOrderFile = async (file: File | null) => {
  if (file === null) {
    console.log("no file selected")
    return
  }

  console.log(file.name)
  console.log(file.size)

  detailFile = file
}
</script>