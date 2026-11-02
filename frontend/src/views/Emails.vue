<template>
  <div class="mail">
    <!-- ===== 页头 ===== -->
    <div class="page-head">
      <div class="ph-left">
        <div class="kicker">
          <span class="k-badge">OUTBOUND ENGINE</span>
          <span class="live"><i class="pulse"></i>投递通道正常</span>
        </div>
        <h1 class="page-title">智能邮件中心 <span>(Email Center)</span></h1>
        <p class="page-sub">AI 依据客户画像生成的个性化开发信，人工审核后发送，全程追踪打开与点击。</p>
      </div>
      <div class="ph-actions">
        <button class="btn-outline" @click="load">
          <svg viewBox="0 0 24 24"><path d="M3 12a9 9 0 1 0 3-6.7" /><path d="M3 4v5h5" /></svg>
          刷新追踪
        </button>
      </div>
    </div>

    <!-- ===== 4 指标卡 ===== -->
    <div class="stat-row">
      <div class="stat-card">
        <div class="sc-head">
          <span class="sc-label indigo"><i class="dot indigo"></i>邮件总送达量</span>
          <svg viewBox="0 0 24 24" class="sc-ico"><path d="m3 8 9 6 9-6" /><rect x="3" y="5" width="18" height="14" rx="2" /></svg>
        </div>
        <div class="sc-main"><span class="sc-num">{{ sentCount }}</span><span class="sc-unit">封已发送</span></div>
        <div class="sc-foot">总生成 {{ emails.length }} 封 · 待处理 {{ pendingCount }}</div>
      </div>

      <div class="stat-card">
        <div class="sc-head">
          <span class="sc-label emerald"><i class="dot emerald"></i>打开总次数 &amp; 穿透率</span>
          <svg viewBox="0 0 24 24" class="sc-ico emerald"><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12z" /><circle cx="12" cy="12" r="2.6" /></svg>
        </div>
        <div class="sc-main"><span class="sc-num emerald">{{ openRate }}%</span><span class="sc-unit">{{ openTotal }} 次打开</span></div>
        <div class="mini-track"><i class="emerald" :style="{ width: openRate + '%' }"></i></div>
      </div>

      <div class="stat-card">
        <div class="sc-head">
          <span class="sc-label indigo"><i class="dot indigo"></i>有效链接点击</span>
          <svg viewBox="0 0 24 24" class="sc-ico"><path d="M9 11a3 3 0 0 1 4.2 0l1.8 1.8a3 3 0 0 1-4.2 4.2L9.6 15.8" /><path d="M15 13a3 3 0 0 1-4.2 0L9 11.2a3 3 0 0 1 4.2-4.2l1.2 1.2" /></svg>
        </div>
        <div class="sc-main"><span class="sc-num indigo">{{ clickRate }}%</span><span class="sc-unit">{{ clickTotal }} 次点击</span></div>
        <div class="mini-track"><i class="indigo" :style="{ width: clickRate + '%' }"></i></div>
      </div>

      <div class="stat-card">
        <div class="sc-head">
          <span class="sc-label amber"><i class="dot amber"></i>真实客户回复</span>
          <svg viewBox="0 0 24 24" class="sc-ico amber"><path d="M20 14.5a2.5 2.5 0 0 1-2.5 2.5H8l-4 3V6.5A2.5 2.5 0 0 1 6.5 4h11A2.5 2.5 0 0 1 20 6.5z" /></svg>
        </div>
        <div class="sc-main"><span class="sc-num amber">{{ repliedCount }}</span><span class="sc-unit">封回复</span></div>
        <div class="sc-foot">已进入跟进看板「已回复」阶段</div>
      </div>
    </div>

    <!-- ===== 状态 Tabs ===== -->
    <div class="tabs-bar">
      <button
        v-for="t in tabs"
        :key="t.key"
        class="tab"
        :class="{ on: activeTab === t.key }"
        @click="activeTab = t.key"
      >
        <i class="tab-dot" :class="t.tone"></i>
        <span>{{ t.label }}</span>
        <span class="tab-count" :class="t.tone">{{ countOf(t.key) }}</span>
      </button>
    </div>

    <!-- ===== 主区：表格 + 详情 ===== -->
    <div class="main-grid">
      <!-- 表格 -->
      <div class="table-card">
        <div class="tc-head">
          <div class="tch-left">
            <svg viewBox="0 0 24 24" class="tch-ico"><circle cx="6" cy="18" r="2.2" /><circle cx="18" cy="6" r="2.2" /><path d="M6 15.8V9a3 3 0 0 1 3-3h6.8" /></svg>
            <span class="tch-title">邮件投递队列</span>
            <span class="tch-badge">Live</span>
          </div>
          <span class="tch-right">{{ filtered.length }} 封</span>
        </div>

        <div class="table-scroll">
          <table>
            <thead>
              <tr>
                <th style="min-width: 250px">邮件主题 &amp; 收件人</th>
                <th style="min-width: 100px">状态</th>
                <th style="min-width: 110px" class="ta-center">打开 / 点击</th>
                <th style="min-width: 160px" class="ta-right">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="e in filtered"
                :key="e.id"
                :class="{ selected: selected && selected.id === e.id }"
                @click="select(e)"
              >
                <td>
                  <div class="m-subject-row">
                    <span class="m-subject">{{ e.subject || '(无主题)' }}</span>
                  </div>
                  <div class="m-to">
                    <span>{{ e.company_name || '—' }}</span>
                    <span class="m-mail">{{ e.contact_email || '' }}</span>
                  </div>
                </td>
                <td>
                  <span class="st" :class="'st-' + e.status">{{ statusLabel(e.status) }}</span>
                </td>
                <td class="ta-center">
                  <div class="tele">
                    <span class="tele-item" :class="{ on: e.open_count }">
                      <svg viewBox="0 0 24 24"><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12z" /><circle cx="12" cy="12" r="2.4" /></svg>
                      {{ e.open_count || 0 }}
                    </span>
                    <span class="tele-item" :class="{ on: e.click_count }">
                      <svg viewBox="0 0 24 24"><path d="M9 11a3 3 0 0 1 4.2 0l1.8 1.8a3 3 0 0 1-4.2 4.2L9.6 15.8" /><path d="M15 13a3 3 0 0 1-4.2 0L9 11.2a3 3 0 0 1 4.2-4.2l1.2 1.2" /></svg>
                      {{ e.click_count || 0 }}
                    </span>
                  </div>
                </td>
                <td class="ta-right" @click.stop>
                  <div class="row-actions">
                    <button v-if="e.status === 'draft'" class="btn-act" @click="submit(e)">提交审核</button>
                    <template v-if="e.status === 'pending_approval'">
                      <button class="btn-act ghost" @click="reject(e)">打回</button>
                      <button class="btn-act primary" @click="approve(e)">批准</button>
                    </template>
                    <button v-if="e.status === 'approved'" class="btn-act primary" @click="send(e)">发送</button>
                    <button class="btn-act ghost" @click="select(e)">详情</button>
                  </div>
                </td>
              </tr>
              <tr v-if="!filtered.length">
                <td colspan="4" class="empty">该状态下暂无邮件</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 详情抽屉 -->
      <div class="detail">
        <template v-if="selected">
          <div class="d-head">
            <div>
              <div class="d-kicker">MAIL DETAIL</div>
              <h2>邮件详情与投递追踪</h2>
            </div>
            <span class="st" :class="'st-' + selected.status">{{ statusLabel(selected.status) }}</span>
          </div>

          <!-- 收件人 -->
          <div class="d-recipient">
            <span class="d-label">目标收件人</span>
            <div class="d-person">
              <div class="d-avatar">{{ (selected.company_name || '?').slice(0, 1).toUpperCase() }}</div>
              <div class="d-person-info">
                <span class="d-person-name">{{ selected.company_name || '未知公司' }}</span>
                <span class="d-person-mail">{{ selected.contact_email || '未绑定邮箱' }}</span>
              </div>
            </div>
          </div>

          <!-- 遥测 -->
          <div class="d-tele-grid">
            <div class="d-tele">
              <span class="d-label">打开追踪</span>
              <span class="d-tele-num emerald">{{ selected.open_count || 0 }} 次</span>
              <span class="d-tele-sub">{{ selected.open_count ? '客户已查看邮件' : '暂无打开记录' }}</span>
            </div>
            <div class="d-tele">
              <span class="d-label">链接点击</span>
              <span class="d-tele-num indigo">{{ selected.click_count || 0 }} 次</span>
              <span class="d-tele-sub">{{ selected.click_count ? '客户点了正文链接' : '暂无点击记录' }}</span>
            </div>
          </div>

          <!-- 状态时间轴 -->
          <div class="d-flow">
            <div class="d-flow-head">
              <span class="d-label">状态机流转</span>
              <span class="d-flow-sub">State Transition</span>
            </div>
            <div class="flow-steps">
              <template v-for="(s, i) in flowSteps" :key="s.key">
                <div class="flow-step">
                  <div class="flow-dot" :class="s.state">
                    <svg v-if="s.state === 'done'" viewBox="0 0 24 24"><path d="m5 12 4 4 10-10" /></svg>
                    <template v-else>{{ i + 1 }}</template>
                  </div>
                  <span class="flow-label" :class="s.state">{{ s.label }}</span>
                </div>
                <div v-if="i < flowSteps.length - 1" class="flow-line" :class="{ done: s.state === 'done' }"></div>
              </template>
            </div>
          </div>

          <!-- 主题 / 正文 -->
          <div class="d-field">
            <label>邮件主题 <span v-if="editable">（可修改）</span></label>
            <input v-if="editable" v-model="editSubject" class="inp" />
            <div v-else class="d-static">{{ selected.subject }}</div>
          </div>

          <div class="d-field">
            <label>
              邮件正文
              <span v-if="editable" class="editable-hint">· 草稿可编辑</span>
            </label>
            <textarea v-if="editable" v-model="editBody" class="inp textarea" rows="10"></textarea>
            <div v-else class="d-body">{{ selected.body }}</div>
          </div>

          <!-- 操作 -->
          <div class="d-actions">
            <button class="btn-outline" @click="selected = null">关闭</button>
            <template v-if="editable">
              <button class="btn-primary" :disabled="saving" @click="saveEdit">
                {{ saving ? '保存中...' : '保存修改' }}
              </button>
              <button class="btn-primary" @click="submit(selected)">提交审核</button>
            </template>
            <template v-if="selected.status === 'pending_approval'">
              <button class="btn-outline" @click="reject(selected)">打回</button>
              <button class="btn-primary" @click="approve(selected)">批准</button>
            </template>
            <button v-if="selected.status === 'approved'" class="btn-primary" @click="send(selected)">
              发送邮件
            </button>
          </div>
        </template>

        <div v-else class="d-empty">
          <svg viewBox="0 0 24 24"><rect x="3" y="5.4" width="18" height="13.2" rx="2.2" /><path d="m4.2 7.2 7.8 5.6 7.8-5.6" /></svg>
          <p>从左侧列表选择一封邮件查看详情</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { emailApi } from '../api'

const emails = ref([])
const activeTab = ref('all')
const selected = ref(null)
const editSubject = ref('')
const editBody = ref('')
const saving = ref(false)

const tabs = [
  { key: 'all', label: '全部邮件', tone: 'indigo' },
  { key: 'draft', label: '草稿 Draft', tone: 'slate' },
  { key: 'pending_approval', label: '待审批 Pending', tone: 'amber' },
  { key: 'approved', label: '已批准 Approved', tone: 'indigo' },
  { key: 'sent', label: '已发送 Sent', tone: 'emerald' },
  { key: 'failed', label: '失败 Failed', tone: 'rose' },
]

const STATUS_LABEL = {
  draft: '草稿',
  pending_approval: '待审批',
  approved: '已批准',
  sending: '发送中',
  sent: '已发送',
  failed: '发送失败',
}

const sentCount = computed(() => emails.value.filter((e) => e.status === 'sent').length)
const pendingCount = computed(
  () => emails.value.filter((e) => ['draft', 'pending_approval', 'approved'].includes(e.status)).length
)
const openTotal = computed(() => emails.value.reduce((s, e) => s + (e.open_count || 0), 0))
const clickTotal = computed(() => emails.value.reduce((s, e) => s + (e.click_count || 0), 0))
const openRate = computed(() =>
  sentCount.value ? Math.round((openTotal.value / sentCount.value) * 100) : 0
)
const clickRate = computed(() =>
  sentCount.value ? Math.round((clickTotal.value / sentCount.value) * 100) : 0
)
const repliedCount = computed(
  () => emails.value.filter((e) => (e.last_event_at && e.click_count > 0)).length
)

const filtered = computed(() =>
  activeTab.value === 'all'
    ? emails.value
    : emails.value.filter((e) => e.status === activeTab.value)
)

const editable = computed(() => selected.value && selected.value.status === 'draft')

const FLOW = [
  { key: 'draft', label: '起草' },
  { key: 'pending_approval', label: '待审批' },
  { key: 'approved', label: '已批准' },
  { key: 'sent', label: '发送投递' },
]

const flowSteps = computed(() => {
  const order = ['draft', 'pending_approval', 'approved', 'sending', 'sent']
  const cur = selected.value ? order.indexOf(selected.value.status) : -1
  return FLOW.map((f, i) => {
    let state = 'todo'
    if (i < cur) state = 'done'
    else if (i === cur) state = 'active'
    return { ...f, state }
  })
})

function statusLabel(s) {
  return STATUS_LABEL[s] || s
}
function countOf(key) {
  return key === 'all' ? emails.value.length : emails.value.filter((e) => e.status === key).length
}
function select(e) {
  selected.value = e
  editSubject.value = e.subject
  editBody.value = e.body
}

async function load() {
  const r = await emailApi.list()
  emails.value = r.data
  if (selected.value) {
    const fresh = emails.value.find((x) => x.id === selected.value.id)
    if (fresh) select(fresh)
  }
}

async function saveEdit() {
  saving.value = true
  try {
    await emailApi.update(selected.value.id, { subject: editSubject.value, body: editBody.value })
    ElMessage.success('已保存')
    await load()
  } catch (e) {
    ElMessage.error('保存失败：' + (e.response?.data?.detail || e.message))
  } finally {
    saving.value = false
  }
}

async function submit(e) {
  await emailApi.submit(e.id)
  ElMessage.success('已提交审核')
  await load()
}
async function approve(e) {
  await emailApi.approve(e.id)
  ElMessage.success('已批准')
  await load()
}
async function reject(e) {
  await emailApi.reject(e.id)
  ElMessage.success('已打回')
  await load()
}
async function send(e) {
  const r = await emailApi.send(e.id)
  if (r.data.ok) ElMessage.success('已发送')
  else ElMessage.error('发送失败：' + (r.data.message || ''))
  await load()
}

onMounted(load)
</script>

<style scoped>
.mail { display: flex; flex-direction: column; gap: 16px; }

.page-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; flex-wrap: wrap; }
.ph-left { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.kicker { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.k-badge {
  font-size: 10px; font-weight: 700; letter-spacing: .06em; color: #4f46e5;
  background: #eef2ff; border: 1px solid #e0e7ff; padding: 2px 8px; border-radius: 999px;
}
.live { display: inline-flex; align-items: center; gap: 5px; font-size: 11px; color: #059669; font-weight: 500; }
.pulse { width: 6px; height: 6px; border-radius: 50%; background: #10b981; animation: pl 2s infinite; }
@keyframes pl {
  0% { box-shadow: 0 0 0 0 rgba(16,185,129,.5); }
  70% { box-shadow: 0 0 0 6px rgba(16,185,129,0); }
  100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); }
}
.page-title { font-size: 23px; font-weight: 700; color: #0f172a; margin: 0; letter-spacing: -.025em; }
.page-title span { font-size: 15px; font-weight: 500; color: #64748b; }
.page-sub { font-size: 13px; color: #64748b; margin: 0; max-width: 680px; }

.btn-primary, .btn-outline {
  display: inline-flex; align-items: center; gap: 6px; height: 34px; padding: 0 14px;
  border-radius: 8px; font-size: 12.5px; font-weight: 600; cursor: pointer; white-space: nowrap;
}
.btn-primary { background: #4f46e5; border: 1px solid #4f46e5; color: #fff; box-shadow: 0 1px 2px rgba(79,70,229,.25); }
.btn-primary:hover:not(:disabled) { background: #4338ca; }
.btn-primary:disabled { background: #a5b4fc; cursor: not-allowed; }
.btn-outline { background: #fff; border: 1px solid #e2e8f0; color: #334155; }
.btn-outline:hover { background: #f8fafc; border-color: #cbd5e1; }
.btn-outline svg { width: 14px; height: 14px; stroke: currentColor; fill: none; stroke-width: 1.9; stroke-linecap: round; stroke-linejoin: round; }

/* 指标 */
.stat-row { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
.stat-card {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px 17px;
  display: flex; flex-direction: column; gap: 9px; box-shadow: 0 1px 3px rgba(15,23,42,.04);
}
.sc-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.sc-label { display: inline-flex; align-items: center; gap: 5px; font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; }
.sc-label.indigo { color: #4338ca; }
.sc-label.emerald { color: #047857; }
.sc-label.amber { color: #b45309; }
.dot { width: 6px; height: 6px; border-radius: 50%; }
.dot.indigo { background: #4f46e5; }
.dot.emerald { background: #10b981; }
.dot.amber { background: #f59e0b; }
.sc-ico { width: 17px; height: 17px; stroke: #6366f1; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.sc-ico.emerald { stroke: #10b981; }
.sc-ico.amber { stroke: #f59e0b; }
.sc-main { display: flex; align-items: baseline; gap: 6px; }
.sc-num { font-size: 26px; font-weight: 800; color: #0f172a; letter-spacing: -.03em; font-variant-numeric: tabular-nums; line-height: 1.1; }
.sc-num.emerald { color: #059669; }
.sc-num.indigo { color: #4f46e5; }
.sc-num.amber { color: #d97706; }
.sc-unit { font-size: 11.5px; color: #64748b; font-weight: 600; }
.sc-foot { font-size: 10.5px; color: #94a3b8; }
.mini-track { height: 5px; border-radius: 3px; background: #f1f5f9; overflow: hidden; }
.mini-track i { display: block; height: 100%; border-radius: 3px; transition: width .7s; }
.mini-track i.emerald { background: #10b981; }
.mini-track i.indigo { background: #4f46e5; }

/* Tabs */
.tabs-bar {
  display: flex; flex-wrap: wrap; gap: 6px; padding: 6px;
  background: #fff; border: 1px solid #e2e8f0; border-radius: 10px;
}
.tab {
  display: inline-flex; align-items: center; gap: 6px; height: 30px; padding: 0 11px;
  border-radius: 7px; border: 1px solid transparent; background: transparent;
  color: #64748b; font-size: 12px; font-weight: 500; cursor: pointer; transition: all .15s;
}
.tab:hover { background: #f8fafc; color: #0f172a; }
.tab.on { background: #eef2ff; border-color: #e0e7ff; color: #4338ca; font-weight: 600; }
.tab-dot { width: 6px; height: 6px; border-radius: 50%; }
.tab-count {
  font-size: 10px; font-weight: 700; padding: 0 5px; border-radius: 999px;
  min-width: 18px; text-align: center; font-variant-numeric: tabular-nums;
}
.tab-dot.slate, .tab-count.slate { background: #f1f5f9; color: #64748b; }
.tab-dot.slate { background: #94a3b8; }
.tab-count.amber { background: #fffbeb; color: #b45309; }
.tab-dot.amber { background: #f59e0b; }
.tab-count.indigo { background: #eef2ff; color: #4338ca; }
.tab-dot.indigo { background: #4f46e5; }
.tab-count.emerald { background: #ecfdf5; color: #047857; }
.tab-dot.emerald { background: #10b981; }
.tab-count.rose { background: #fef2f2; color: #b91c1c; }
.tab-dot.rose { background: #f43f5e; }

/* 主栅格 */
.main-grid { display: grid; grid-template-columns: minmax(0, 7fr) minmax(0, 5fr); gap: 16px; align-items: start; }

.table-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(15,23,42,.04); }
.tc-head { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; }
.tch-left { display: flex; align-items: center; gap: 8px; }
.tch-ico { width: 16px; height: 16px; stroke: #4f46e5; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.tch-title { font-size: 12.5px; font-weight: 700; color: #0f172a; }
.tch-badge {
  font-size: 9.5px; font-weight: 700; letter-spacing: .05em; text-transform: uppercase;
  color: #4338ca; background: #eef2ff; border: 1px solid #e0e7ff; padding: 1px 6px; border-radius: 4px;
}
.tch-right { font-size: 11px; color: #94a3b8; }
.table-scroll { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 12px; }
thead th {
  background: #f8fafc; color: #94a3b8; font-size: 10px; font-weight: 700; text-transform: uppercase;
  letter-spacing: .05em; text-align: left; padding: 9px 13px; border-bottom: 1px solid #e2e8f0; white-space: nowrap;
}
tbody td { padding: 11px 13px; border-bottom: 1px solid #f1f5f9; vertical-align: top; }
tbody tr:last-child td { border-bottom: 0; }
tbody tr { cursor: pointer; transition: background .12s; }
tbody tr:hover { background: #f8fafc; }
tbody tr.selected { background: #eef2ff; }
.ta-center { text-align: center; }
.ta-right { text-align: right; }

.m-subject-row { display: flex; align-items: center; gap: 6px; }
.m-subject { font-size: 12px; font-weight: 600; color: #0f172a; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 240px; }
.m-to { display: flex; flex-direction: column; gap: 1px; margin-top: 3px; font-size: 10.5px; color: #64748b; }
.m-mail { color: #94a3b8; font-family: ui-monospace, monospace; }

.st { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 999px; font-size: 10px; font-weight: 600; white-space: nowrap; }
.st-draft { background: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; }
.st-pending_approval { background: #fffbeb; color: #b45309; border: 1px solid #fde68a; }
.st-approved { background: #eef2ff; color: #4338ca; border: 1px solid #e0e7ff; }
.st-sending { background: #f0f9ff; color: #0284c7; border: 1px solid #e0f2fe; }
.st-sent { background: #ecfdf5; color: #047857; border: 1px solid #d1fae5; }
.st-failed { background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }

.tele { display: inline-flex; align-items: center; gap: 8px; }
.tele-item { display: inline-flex; align-items: center; gap: 3px; font-size: 10.5px; color: #cbd5e1; font-variant-numeric: tabular-nums; font-weight: 600; }
.tele-item.on { color: #334155; }
.tele-item svg { width: 12px; height: 12px; stroke: currentColor; fill: none; stroke-width: 1.9; stroke-linecap: round; stroke-linejoin: round; }

.row-actions { display: flex; align-items: center; justify-content: flex-end; gap: 5px; flex-wrap: wrap; }
.btn-act {
  height: 25px; padding: 0 9px; border-radius: 5px; font-size: 10.5px; font-weight: 600;
  background: #f8fafc; border: 1px solid #e2e8f0; color: #475569; cursor: pointer; white-space: nowrap;
}
.btn-act:hover { background: #f1f5f9; border-color: #cbd5e1; }
.btn-act.primary { background: #4f46e5; border-color: #4f46e5; color: #fff; }
.btn-act.primary:hover { background: #4338ca; }
.btn-act.ghost { background: #fff; }

/* 详情 */
.detail {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px;
  box-shadow: 0 1px 3px rgba(15,23,42,.04); display: flex; flex-direction: column; gap: 13px;
  position: sticky; top: 76px;
}
.d-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }
.d-kicker { font-size: 9.5px; font-weight: 700; letter-spacing: .08em; color: #94a3b8; text-transform: uppercase; margin-bottom: 2px; }
.d-head h2 { font-size: 15px; font-weight: 700; color: #0f172a; margin: 0; letter-spacing: -.01em; }
.d-label { font-size: 9.5px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: .06em; }

.d-recipient { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 9px; padding: 12px; display: flex; flex-direction: column; gap: 8px; }
.d-person { display: flex; align-items: center; gap: 9px; }
.d-avatar {
  width: 34px; height: 34px; flex: 0 0 34px; border-radius: 999px; display: grid; place-items: center;
  background: #eef2ff; border: 1px solid #e0e7ff; color: #4338ca; font-size: 12px; font-weight: 700;
}
.d-person-info { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.d-person-name { font-size: 12.5px; font-weight: 600; color: #0f172a; }
.d-person-mail { font-size: 10.5px; color: #4f46e5; font-family: ui-monospace, monospace; overflow: hidden; text-overflow: ellipsis; }

.d-tele-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 9px; }
.d-tele {
  background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 9px; padding: 10px 12px;
  display: flex; flex-direction: column; gap: 2px;
}
.d-tele-num { font-size: 18px; font-weight: 700; font-variant-numeric: tabular-nums; }
.d-tele-num.emerald { color: #059669; }
.d-tele-num.indigo { color: #4f46e5; }
.d-tele-sub { font-size: 9.5px; color: #94a3b8; }

.d-flow { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 9px; padding: 12px; display: flex; flex-direction: column; gap: 10px; }
.d-flow-head { display: flex; align-items: center; justify-content: space-between; }
.d-flow-sub { font-size: 9px; color: #b6c0cf; }
.flow-steps { display: flex; align-items: flex-start; }
.flow-step { display: flex; flex-direction: column; align-items: center; gap: 4px; flex: 0 0 auto; }
.flow-dot {
  width: 22px; height: 22px; border-radius: 999px; display: grid; place-items: center;
  font-size: 10px; font-weight: 700;
}
.flow-dot.done { background: #10b981; color: #fff; }
.flow-dot.active { background: #4f46e5; color: #fff; box-shadow: 0 0 0 3px rgba(79,70,229,.18); }
.flow-dot.todo { background: #e2e8f0; color: #94a3b8; }
.flow-dot svg { width: 11px; height: 11px; stroke: currentColor; fill: none; stroke-width: 2.6; stroke-linecap: round; stroke-linejoin: round; }
.flow-label { font-size: 9px; color: #94a3b8; white-space: nowrap; }
.flow-label.done { color: #047857; font-weight: 600; }
.flow-label.active { color: #4338ca; font-weight: 700; }
.flow-line { flex: 1; height: 2px; background: #e2e8f0; margin: 10px 4px 0; border-radius: 2px; }
.flow-line.done { background: #10b981; }

.d-field { display: flex; flex-direction: column; gap: 5px; }
.d-field label { font-size: 9.5px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: .06em; }
.editable-hint { color: #4f46e5; text-transform: none; letter-spacing: 0; font-weight: 600; }
.inp {
  width: 100%; height: 34px; padding: 0 11px; background: #fff; border: 1px solid #cbd5e1;
  border-radius: 7px; font-size: 12px; color: #0f172a; outline: none; transition: all .15s; font-family: inherit;
}
.inp:focus { border-color: #4f46e5; box-shadow: 0 0 0 3px rgba(79,70,229,.1); }
.textarea { height: auto; min-height: 260px; padding: 11px; line-height: 1.75; resize: vertical; }
.d-static { font-size: 12.5px; color: #0f172a; font-weight: 600; padding: 8px 0; }
.d-body {
  font-size: 12px; color: #334155; line-height: 1.8; white-space: pre-wrap;
  background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px;
  max-height: 260px; overflow-y: auto;
}

.d-actions { display: flex; justify-content: flex-end; gap: 8px; padding-top: 12px; border-top: 1px solid #f1f5f9; flex-wrap: wrap; }

.d-empty {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 10px; padding: 60px 20px; color: #cbd5e1; font-size: 12px;
}
.d-empty svg { width: 36px; height: 36px; stroke: currentColor; fill: none; stroke-width: 1.5; stroke-linecap: round; stroke-linejoin: round; }

.empty { text-align: center; padding: 28px 0; color: #94a3b8; font-size: 12px; }

@media (max-width: 1300px) {
  .stat-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .main-grid { grid-template-columns: minmax(0, 1fr); }
  .detail { position: static; }
}
@media (max-width: 700px) {
  .stat-row { grid-template-columns: minmax(0, 1fr); }
}
</style>
