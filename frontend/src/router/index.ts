import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/FileConverter.vue'),
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/History.vue'),
  },
  {
    path: '/active',
    name: 'ActiveTasks',
    component: () => import('@/views/ActiveTasks.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
