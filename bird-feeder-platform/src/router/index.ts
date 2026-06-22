import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/components/Layout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('@/views/Dashboard.vue')
    },
    {
      path: '/devices',
      redirect: '/manage/devices'
    },
    {
      path: '/events',
      redirect: '/manage/events'
    },
    {
      path: '/history',
      redirect: '/manage/history'
    },
    {
      path: '/statistics',
      redirect: '/manage/statistics'
    },
    {
      path: '/config',
      redirect: to => ({ path: '/manage/config', query: to.query })
    },
    {
      path: '/logs',
      redirect: '/manage/logs'
    },
    {
      path: '/manage',
      component: Layout,
      redirect: '/manage/devices',
      children: [
        {
          path: 'devices',
          name: 'Devices',
          component: () => import('@/views/Devices.vue')
        },
        {
          path: 'events',
          name: 'Events',
          component: () => import('@/views/BirdEvents.vue')
        },
        {
          path: 'history',
          name: 'History',
          component: () => import('@/views/History.vue')
        },
        {
          path: 'statistics',
          name: 'Statistics',
          component: () => import('@/views/Statistics.vue')
        },
        {
          path: 'config',
          name: 'Config',
          component: () => import('@/views/Config.vue')
        },
        {
          path: 'logs',
          name: 'Logs',
          component: () => import('@/views/Logs.vue')
        }
      ]
    }
  ]
})

export default router
