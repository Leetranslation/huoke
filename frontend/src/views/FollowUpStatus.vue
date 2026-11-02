<template>
  <div class="status">
    <!-- ===== 页头 ===== -->
    <div class="page-head">
      <div class="ph-left">
        <div class="kicker">
          <button class="crumb-link" @click="$router.push('/followup')">跟进看板</button>
          <span class="sep">/</span>
          <span class="crumb-cur">{{ stage.label }}</span>
        </div>
        <h1 class="page-title">
          <span class="title-dot" :style="{ background: stage.color }"></span>{{ stage.label }}
          <span class="title-count">{{ filtered.length }} 位客户</span>
        </h1>
        <p class="page-sub">{{ stage.desc }}</p>
      </div>
      <div class="ph-actions">
        <button class="btn-outline" :disabled="checking" @click="checkReplies">
          <svg viewBox="0 0 24 24"><path d="M3 12a9 9 0 1 0 3-6.7" /><path d="M3 4v5h5" /></svg>
          {{ checking ? '检查中...' : '立即查收回复' }}
        </button>
        <div class="search-wrap">
          <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></svg>
          <input v-model="keyword" placeholder="搜索公司 / 姓名 / 邮箱..." />
        </div>
      </div>
    </div>

    <!-- ===== 表格 ===== -->
    <div class="table-card">
      <div class="tc-head">
        <div class="tch-left">
          <span class="tch-title">客户明细</span>
          <span class="tch-badge">{{ filtered.length }} / {{ contacts.length }}</span>
        </div>
        <span class="tch-right">每 30 秒自动刷新 · 最后更新 {{ updatedAt }}</span>
      </div>

      <div class="table-scroll">
        <table>
          <thead>
            <tr>
              <th style="min-width: 170px">姓名 / 公司</th>
              <th style="min-width: 200px">邮箱</th>
              <th style="min-width: 110px">最近发送</th>
              <th style="min-width: 90px" class="ta-center">打开</th>
              <th style="min-width: 90px" class="ta-center">点击</th>
              <th style="min-width: 220px">最近回复</th>
              <th style="min-width: 70px" class="ta-right">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in filtered" :key="c.id">
              <td>
                <div class="person-cell">
                  <div class="p-avatar">{{ (c.name || '?').slice(0, 1).toUpperCase() }}</div>
                  <div class="p-info">
                    <span class="p-name">{{ c.name || '联系人' }}</span>
                    <span class="p-company">{{ c.company_name || '—' }}</span>
                  </div>
                </div>
              </td>
              <td><span class="mail">{{ c.email || '—' }}</span></td>
              <td><span class="date">{{ formatDate(c.last_sent_at) }}</span></td>
              <td class="ta-center">
                <span v-if="c.open_count" class="tele-badge emerald">{{ c.open_count }}</span>
                <span v-else class="dash">—</span>
              </td>
              <td class="ta-center">
                <span v-if="c.click_count" class="tele-badge indigo">{{ c.click_count }}</span>
                <span v-else class="dash">—</span>
              </td>
              <td>
                <span v-if="c.last_reply_subject" class="reply-text" :title="c.last_reply_subject">
                  {{ c.last_reply_subject }}
                </span>
                <span v-else class="dash">—</span>
              </td>
              <td class="ta-right">
                <button class="btn-mini" @click="$router.push('/companies/' + c.company_id)">详情</button>
              </td>
            </tr>
            <tr v-if="!filtered.length">
              <td colspan="7" class="empty">该阶段暂无客户</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { contactApi } from '../api'

const route = useRoute()
const keyword = ref('')
const contacts = ref([])
const checking = ref(false)
const updatedAt = ref('—')
let timer = null

const STAGES = {
  pending: { label: '待触达', desc: '还没发过开发信的客户', color: '#94a3b8' },
  qualified: { label: '已确认', desc: '人工确认为目标客户', color: '#6366f1' },
  contacted: { label: '跟进中', desc: '已发信，等待回复', color: '#4f46e5' },
  replied: { label: '已回复', desc: '客户已回信，需要人工跟进', color: '#0ea5e9' },
  completed: { label: '已完成', desc: '成交或闭环的客户', color: '#10b981' },
  terminated: { label: '已终止', desc: '拒绝 / 退订 / 邮箱无效', color: '#f43f5e' },
}

const stage = computed(
  () => STAGES[route.params.status] || { label: route.params.status, desc: '', color: '#94a3b8' }
)

const filtered = computed(() => {
  const k = keyword.value.trim().toLowerCase()
  if (!k) return contacts.value
  return contacts.value.filter(
    (c) =>
      (c.name || '').toLowerCase().includes(k) ||
      (c.company_name || '').toLowerCase().includes(k) ||
      (c.email || '').toLowerCase().includes(k)
  )
})

function formatDate(v) {
  if (!v) return '—'
  const d = new Date(v)
  const p = (n) => String(n).padStart(2, '0')
  return `${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

onMounted(() => {
  load()
  timer = setInterval(load, 30000)
})
onUnmounted(() => {
  if (timer) clearInterval(timer)
})

async function load() {
  const r = await contactApi.list()
  const data = r.data
  if (route.params.status === 'terminated') {
    contacts.value = data.filter((c) => ['rejected', 'unsubscribed', 'invalid'].includes(c.status))
  } else {
    contacts.value = data.filter((c) => c.status === route.params.status)
  }
  const d = new Date()
  updatedAt.value = `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')}`
}

async function checkReplies() {
  checking.value = true
  try {
    await contactApi.checkReplies()
    ElMessage.success('已提交查收任务，稍后自动刷新')
    setTimeout(() => {
      load()
      checking.value = false
    }, 6000)
  } catch (e) {
    ElMessage.error('失败：' + (e.response?.data?.detail || e.message))
    checking.value = false
  }
}
</script>

<style scoped>
.status { display: flex; flex-direction: column; gap: 16px; }

.page-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; flex-wrap: wrap; }
.ph-left { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.kicker { display: flex; align-items: center; gap: 6px; font-size: 11px; }
.crumb-link { background: none; border: 0; color: #4f46e5; font-size: 11px; font-weight: 600; cursor: pointer; padding: 0; }
.crumb-link:hover { color: #4338ca; }
.sep { color: #cbd5e1; }
.crumb-cur { color: #64748b; font-weight: 600; }

.page-title { display: flex; align-items: center; gap: 8px; font-size: 23px; font-weight: 700; color: #0f172a; margin: 0; letter-spacing: -.025em; }
.title-dot { width: 9px; height: 9px; border-radius: 50%; }
.title-count {
  font-size: 11px; font-weight: 700; color: #4f46e5; background: #eef2ff;
  border: 1px solid #e0e7ff; padding: 2px 8px; border-radius: 999px;
}
.page-sub { font-size: 13px; color: #64748b; margin: 0; }

.ph-actions { display: flex; align-items: center; gap: 8px; flex: 0 0 auto; }
.btn-outline {
  display: inline-flex; align-items: center; gap: 6px; height: 34px; padding: 0 13px;
  background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; color: #334155;
  font-size: 12.5px; font-weight: 600; cursor: pointer; white-space: nowrap;
}
.btn-outline:hover:not(:disabled) { background: #f8fafc; border-color: #cbd5e1; }
.btn-outline:disabled { opacity: .6; cursor: not-allowed; }
.btn-outline svg { width: 13px; height: 13px; stroke: currentColor; fill: none; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }

.search-wrap { position: relative; }
.search-wrap svg {
  position: absolute; left: 10px; top: 50%; transform: translateY(-50%);
  width: 14px; height: 14px; stroke: #94a3b8; fill: none; stroke-width: 1.9; stroke-linecap: round; stroke-linejoin: round;
}
.search-wrap input {
  height: 34px; width: 230px; padding: 0 11px 0 31px; background: #fff;
  border: 1px solid #e2e8f0; border-radius: 8px; font-size: 12px; color: #0f172a; outline: none;
}
.search-wrap input::placeholder { color: #94a3b8; }
.search-wrap input:focus { border-color: #4f46e5; box-shadow: 0 0 0 3px rgba(79,70,229,.1); }

.table-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(15,23,42,.04); }
.tc-head { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; }
.tch-left { display: flex; align-items: center; gap: 8px; }
.tch-title { font-size: 12.5px; font-weight: 700; color: #0f172a; }
.tch-badge { font-size: 10px; font-weight: 700; color: #4f46e5; background: #eef2ff; border: 1px solid #e0e7ff; padding: 1px 7px; border-radius: 999px; }
.tch-right { font-size: 10.5px; color: #94a3b8; }

.table-scroll { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 12px; }
thead th {
  background: #f8fafc; color: #94a3b8; font-size: 10px; font-weight: 700; text-transform: uppercase;
  letter-spacing: .05em; text-align: left; padding: 9px 14px; border-bottom: 1px solid #e2e8f0; white-space: nowrap;
}
tbody td { padding: 11px 14px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
tbody tr:last-child td { border-bottom: 0; }
tbody tr:hover { background: #f8fafc; }
.ta-center { text-align: center; }
.ta-right { text-align: right; }

.person-cell { display: flex; align-items: center; gap: 9px; }
.p-avatar {
  width: 30px; height: 30px; flex: 0 0 30px; border-radius: 999px; display: grid; place-items: center;
  background: #eef2ff; border: 1px solid #e0e7ff; color: #4338ca; font-size: 11px; font-weight: 700;
}
.p-info { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.p-name { font-size: 12px; font-weight: 600; color: #0f172a; }
.p-company { font-size: 10.5px; color: #94a3b8; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 150px; }

.mail { font-size: 11px; color: #4f46e5; font-family: ui-monospace, monospace; }
.date { font-size: 11px; color: #94a3b8; font-variant-numeric: tabular-nums; }
.tele-badge { display: inline-block; min-width: 22px; padding: 1px 6px; border-radius: 999px; font-size: 10.5px; font-weight: 700; font-variant-numeric: tabular-nums; }
.tele-badge.emerald { background: #ecfdf5; color: #047857; border: 1px solid #d1fae5; }
.tele-badge.indigo { background: #eef2ff; color: #4338ca; border: 1px solid #e0e7ff; }
.dash { color: #cbd5e1; font-size: 11px; }
.reply-text {
  display: inline-block; max-width: 210px; font-size: 11.5px; color: #4338ca;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.btn-mini {
  height: 25px; padding: 0 9px; border-radius: 5px; background: #4f46e5; border: 1px solid #4f46e5;
  color: #fff; font-size: 10.5px; font-weight: 600; cursor: pointer;
}
.btn-mini:hover { background: #4338ca; }
.empty { text-align: center; padding: 28px 0; color: #94a3b8; font-size: 12px; }
</style>
