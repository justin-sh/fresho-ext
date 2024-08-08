<template>
  <v-file-input
    v-model = "files"
    label="File input"
    show-size
    @input="uploadFile"
    @change="uploadFile"
  ></v-file-input>
</template>

<script lang="ts" setup>
import {ref} from "vue"
import {uploadOrderCsv} from '@/api'

const files = ref([])


async function uploadFile(f){
  console.log(f)
  console.log(f.name)
  await uploadOrderCsv(f)
  console.log(f.name + new Date)
}

</script>