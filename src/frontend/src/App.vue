<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { useStyleStore } from "@/stores/style.js";
import { mdiGithub, mdiThemeLightDark } from '@mdi/js'
import Icon from '@/components/IconCanvas.vue'
import NavBar from '@/components/NavBar.vue'
import NavBarItem from '@/components/NavBarItem.vue'
import NavBarItemLabel from '@/components/NavBarItemLabel.vue'
import LayoutBase from '@/layouts/LayoutBase.vue'
const styleStore = useStyleStore();
// import HelloWorld from './components/HelloWorld.vue'

// const ripple = new MDCRipple(document.querySelector('.foo-button'));

</script>

<template>
  <LayoutBase>
    <NavBar>
      <!-- <header>
      <img alt="Vue logo" class="logo" src="@/assets/satellit.ico" width="125" height="125" />
      <nav> -->
      <div class="flex justify-center w-screen">
        <div class="flex items-center space-x-5 text-neutral-500 dark:text-gray-300">
          <RouterLink to="/" class="hover:text-black dark:hover:text-gray-100">Home</RouterLink>
          <RouterLink to="/overview" class="hover:text-black dark:hover:text-gray-100">Overview
          </RouterLink>
          <RouterLink to="/classifying" class="hover:text-black dark:hover:text-gray-100">Classifying</RouterLink>
          <RouterLink to="/download" class="hover:text-black dark:hover:text-gray-100">Download</RouterLink>
          <RouterLink to="/models" class="hover:text-black dark:hover:text-gray-100">Models</RouterLink>
          <RouterLink to="/about" class="hover:text-black dark:hover:text-gray-100">About</RouterLink>
          <!-- <RouterLink to="/table" class="hover:text-black dark:hover:text-gray-100">Table View</RouterLink>
          <RouterLink to="/map" class="hover:text-black dark:hover:text-gray-100">Map View</RouterLink>
          <RouterLink to="/selectPolyFromTableView" class="hover:text-black dark:hover:text-gray-100">
            SelectPolyFromTableView</RouterLink> -->
          <!-- <RouterLink to="/sideBarView" class="hover:text-black dark:hover:text-gray-100">sideBarView</RouterLink> -->
        </div>
      </div>
      <div class="flex max-h-screen-menu items-stretch lg:ml-auto">
        <div class="flex items-center space-x-4">
          <div class="">
            <a href="https://github.com/Taraman12/Solarpark-detection" target="_blank" rel="noopener noreferrer">
              <Icon :path="mdiGithub" />
            </a>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input @click="styleStore.setDarkMode()" type="checkbox" value="" class="sr-only peer">
            <div
              class="w-11 h-6 bg-gray-100 peer-focus:outline-none  rounded-full peer dark:bg-gray-200 peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-gray-600">
            </div>
            <Icon :path="mdiThemeLightDark" />
          </label>
        </div>
      </div>
    </NavBar>
    <RouterView />
  </LayoutBase>
</template>

<!-- <style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}
</style> -->
