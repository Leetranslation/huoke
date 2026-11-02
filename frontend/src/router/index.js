import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layout/MainLayout.vue'

const routes = [
  { path: '/login', component: () => import('../views/Login.vue') },
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '工作台' } },
      { path: 'campaigns', component: () => import('../views/Campaigns.vue'), meta: { title: '获客任务' } },
      { path: 'campaigns/:id', component: () => import('../views/CampaignDetail.vue'), meta: { title: '任务详情' } },
      { path: 'leads', component: () => import('../views/Leads.vue'), meta: { title: '客户池' } },
      { path: 'companies/:id', component: () => import('../views/CompanyDetail.vue'), meta: { title: '公司详情' } },
      { path: 'emails', component: () => import('../views/Emails.vue'), meta: { title: '邮件中心' } },
      { path: 'followup', component: () => import('../views/FollowUp.vue'), meta: { title: '跟进看板' } },
      { path: 'followup/:status', component: () => import('../views/FollowUpStatus.vue'), meta: { title: '跟进详情' } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
