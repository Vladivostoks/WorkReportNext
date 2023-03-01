import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import MainView from '@/views/MainView.vue'
import InfoTable from '@/components/MainView/Body/InfoTable.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView
    },
    {
      path: '/items',
      name: 'items',
      component: MainView,
      // props: (route)=>{return route.params;},
      children: [
        { path: ':tableMode', component: InfoTable}, 
      ]
    },
  ]
})

export default router
