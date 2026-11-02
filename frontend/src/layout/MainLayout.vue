<template>
  <div class="app">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-mark">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round">
            <circle cx="12" cy="12" r="7" opacity=".9" />
            <circle cx="12" cy="12" r="2.4" />
            <path d="M12 2.4v2.2M12 19.4v2.2M2.4 12h2.2M19.4 12h2.2" />
          </svg>
        </div>
        <div class="brand-text">
          <strong>远洋获客</strong>
          <span>AI SDR</span>
        </div>
      </div>

      <nav class="nav">
        <div class="nav-label">主控台</div>
        <div
          v-for="item in nav"
          :key="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
          @click="$router.push(item.path)"
        >
          <span v-html="item.icon"></span>
          <span>{{ item.label }}</span>
        </div>
      </nav>

      <div class="sidebar-foot">
        <div class="user">
          <div class="user-avatar">张</div>
          <div class="user-info">
            <strong>张明</strong>
            <span>海外营销部 · 管理员</span>
          </div>
        </div>
      </div>
    </aside>

    <main class="main">
      <header class="topbar">
        <div class="crumbs">
          <span>智能获客系统</span>
          <span class="sep">›</span>
          <span class="cur">{{ pageTitle }}</span>
        </div>
        <div class="topbar-right">
          <button class="btn btn-primary" @click="$router.push('/campaigns')">
            <svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14" /></svg>
            新建任务
          </button>
        </div>
      </header>

      <div class="page-body">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isActive = (p) => route.path === p || route.path.startsWith(p + '/')

const pageTitle = computed(() => route.meta?.title || '工作台')

const nav = [
  {
    path: '/dashboard',
    label: '工作台',
    icon: '<svg viewBox="0 0 24 24"><rect x="3.5" y="3.5" width="7" height="7" rx="1.6"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.6"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.6"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.6"/></svg>',
  },
  {
    path: '/campaigns',
    label: '获客任务',
    icon: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="2.6"/><path d="M12 2.4v2.6M12 19v2.6M2.4 12h2.6M19 12h2.6"/></svg>',
  },
  {
    path: '/leads',
    label: '客户池',
    icon: '<svg viewBox="0 0 24 24"><path d="M16 20v-1.4a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4V20"/><circle cx="9.5" cy="7.6" r="3.3"/><path d="M17.2 11.2a3 3 0 1 0 0-6"/><path d="M21 20v-1.2a3.6 3.6 0 0 0-2.6-3.4"/></svg>',
  },
  {
    path: '/emails',
    label: '智能邮件中心',
    icon: '<svg viewBox="0 0 24 24"><rect x="3" y="5.4" width="18" height="13.2" rx="2.2"/><path d="m4.2 7.2 7.8 5.6 7.8-5.6"/></svg>',
  },
  {
    path: '/followup',
    label: '跟进看板',
    icon: '<svg viewBox="0 0 24 24"><path d="M4 19V5"/><path d="M4 19h16"/><path d="m7 15 4-4 3 3 5-6"/></svg>',
  },
]
</script>
