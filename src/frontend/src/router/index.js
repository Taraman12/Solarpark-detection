import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue')
    },
    {
      path: '/testview',
      name: 'testview',
      component: () => import('../views/TestView.vue')
    },
    {
      path: '/table',
      name: 'table',
      component: () => import('../views/TableView.vue')
    },
    {
      path: '/map',
      name: 'map',
      component: () => import('../views/MapView.vue')
    },
    {
      path: '/mapWithPoly',
      name: 'mapWithPoly',
      component: () => import('../views/MapWithPolyView.vue')
    },
    {
      path: '/selectPolyFromTableView',
      name: 'selectPolyFromTableView',
      component: () => import('../views/SelectPolyFromTableView.vue')
    },
    {
      path: '/modelsView',
      name: 'modelsView',
      component: () => import('../views/ModelsView.vue')
    },
  ]
})

export default router
