<template>
  <header>
    <div>
      <b-navbar toggleable="md" type="dark" variant="info">
        <b-navbar-brand>Fresho Ext</b-navbar-brand>

        <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

        <b-collapse id="nav-collapse" is-nav>
          <b-navbar-nav>
            <b-nav-item :to="{name:'home'}">
              Home
            </b-nav-item>
            <b-nav-item :to="{name:'orders'}">
              Orders
            </b-nav-item>
            <b-nav-item :to="{name:'files-upload'}">
              Files Upload
            </b-nav-item>
          </b-navbar-nav>


          <b-navbar-nav class="ml-auto">
            <b-nav-item-dropdown right>
              <template #button-content>
                <em>User</em>
              </template>
              <b-dropdown-item href="#">Profile</b-dropdown-item>
              <b-dropdown-item href="#">Sign Out</b-dropdown-item>
            </b-nav-item-dropdown>
          </b-navbar-nav>
        </b-collapse>
      </b-navbar>
    </div>
  </header>

  <div class="container">
    <RouterView/>
  </div>
  <footer>
    <div class="d-flex bg-info bg-gradient mt-2 p-2 justify-content-center">Fresho Extension @Justin</div>
  </footer>
</template>

<script setup lang="ts">
import {RouterView} from 'vue-router'
</script>

<style scoped>
@media print {
  .container {
    max-width: 100% !important;
  }
}
</style>