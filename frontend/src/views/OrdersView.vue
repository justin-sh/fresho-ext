<template>
	 <b-card
    title="Filters"
    tag="orders"
        class="mb-2"
  >
    <!-- <b-card-text>
      Some quick example text to build on the card title and make up the bulk of the card's content.
    </b-card-text> -->

     <div class="flex">
    <label for="example-datepicker">Delivery date</label>
    <b-form-datepicker 
    	id="example-datepicker" 
    	v-model="value" 
    	:date-format-options="{ year: 'numeric', month: 'short', day: '2-digit', weekday: 'short' }" 
    	class="mb-2"></b-form-datepicker>
    <p>Value: '{{ value }}'</p>
  </div>
  </b-card>

  <b-card title="Orders">
  </b-card>
</template>