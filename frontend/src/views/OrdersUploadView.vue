<template>
  <v-file-input
    v-model = "files"
    label="File input"
    show-size
  ></v-file-input>
</template>

<script type="ts" setup>
import {ref} from 'vue'

const files = ref([])
</script>