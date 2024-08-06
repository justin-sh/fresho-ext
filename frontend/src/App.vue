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
          </b-navbar-nav>

          <!-- Right aligned nav items -->
          <b-navbar-nav class="ml-auto">
            <!--            <b-nav-form>-->
            <!--              <b-form-input size="sm" class="mr-sm-2" placeholder="Search"></b-form-input>-->
            <!--              <b-button size="sm" class="my-2 my-sm-0" type="submit">Search</b-button>-->
            <!--            </b-nav-form>-->

            <b-nav-item-dropdown right>
              <!-- Using 'button-content' slot -->
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
    <!--    <img alt="Vue logo" class="logo" src="@/assets/logo.svg" width="125" height="125"/>-->

    <!--     <div class="wrapper">
          <HelloWorld msg="You did it!"/>

          <nav>
            <RouterLink to="/">Home</RouterLink>
            <RouterLink to="/about">About</RouterLink>
          </nav>
        </div> -->
  </header>

  <div class="container">
    <RouterView/>
  </div>
  <footer>

  </footer>
</template>

<script setup lang="ts">
import {RouterLink, RouterView} from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
</script>
