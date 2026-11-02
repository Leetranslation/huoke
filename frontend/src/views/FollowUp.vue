<template>
  <div class="funnel">
    <!-- ===== 页头 ===== -->
    <div class="page-head">
      <div class="ph-left">
        <div class="kicker">
          <span class="k-badge">LIFECYCLE FUNNEL</span>
          <span class="live"><i class="pulse"></i>自动跟进引擎运行中</span>
        </div>
        <h1 class="page-title">跟进看板 <span>(Follow-up Board)</span></h1>
        <p class="page-sub">客户在各阶段的分布，点卡片查看该阶段客户与邮件追踪明细。</p>
      </div>
      <div class="ph-actions">
        <span class="scan-time">{{ lastScanText }}</span>
        <button class="btn-primary" :disabled="scanning" @click="runScan">
          <svg viewBox="0 0 24 24"><path d="M3 12a9 9 0 1 0 3-6.7" /><path d="M3 4v5h5" /></svg>
          {{ scanning ? '提交中...' : '立即扫描跟进' }}
        </button>
      </div>
    </div>

    <!-- ===== 4 指标 ===== -->
    <div class="stat-row">
      <div class="stat-card">
        <span class="sc-label">总客户</span>
        <div class="sc-main"><span class="sc-num">{{ total }}</span><span class="sc-unit">位联系人</span></div>
        <div class="sc-bar"><i class="indigo" style="width: 100%"></i></div>
      </div>
      <div class="stat-card">
        <span class="sc-label">进行中</span>
        <div class="sc-main"><span class="sc-num emerald">{{ activeCount }}</span><span class="sc-unit">待回复</span></div>
        <div class="sc-bar"><i class="emerald" :style="{ width: pct(activeCount) + '%' }"></i></div>
      </div>
      <div class="stat-card">
        <span class="sc-label">已回复</span>
        <div class="sc-main"><span class="sc-num sky">{{ repliedCount }}</span><span class="sc-unit">需跟进</span></div>
        <div class="sc-bar"><i class="sky" :style="{ width: pct(repliedCount) + '%' }"></i></div>
      </div>
      <div class="stat-card">
        <span class="sc-label">已终止</span>
        <div class="sc-main"><span class="sc-num rose">{{ closedCount }}</span><span class="sc-unit">拒绝/退订</span></div>
        <div class="sc-bar"><i class="rose" :style="{ width: pct(closedCount) + '%' }"></i></div>
      </div>
    </div>

    <!-- ===== 阶段卡片 ===== -->
    <div class="stage-grid">
      <div
        v-for="(col, i) in columns"
        :key="col.key"
        class="stage"
        :class="{ empty: !col.items.length }"
        @click="$router.push('/followup/' + col.key)"
      >
        <div class="stage-top">
          <span class="stage-idx">{{ String(i + 1).padStart(2, '0') }}</span>
          <span class="stage-pct">{{ pct(col.items.length) }}%</span>
        </div>
        <div class="stage-name-row">
          <span class="stage-dot" :style="{ background: col.color }"></span>
          <span class="stage-name">{{ col.label }}</span>
        </div>
        <div class="stage-num">{{ col.items.length }}</div>
        <div class="stage-desc">{{ col.desc }}</div>
        <div class="stage-track">
          <i :style="{ width: pct(col.items.length) + '%', background: col.color }"></i>
        </div>
        <div class="stage-link">查看客户 →</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { contactApi } from '../api'

const columns = ref([
  { key: 'pending', label: '待触达', desc: '还没发过开发信', color: '#94a3b8', items: [] },
  { key: 'qualified', label: '已确认', desc: '人工确认为目标客户', color: '#6366f1', items: [] },
  { key: 'contacted', label: '跟进中', desc: '已发信，等待回复', color: '#4f46e5', items: [] },
  { key: 'replied', label: '已回复', desc: '客户已回信', color: '#0ea5e9', items: [] },
  { key: 'completed', label: '已完成', desc: '成交或闭环', color: '#10b981', items: [] },
  { key: 'terminated', label: '已终止', desc: '拒绝 / 退订 / 无效', color: '#f43f5e', items: [] },
])

const TERMINATED = ['rejected', 'unsubscribed', 'invalid']
const scanning = ref(false)
const lastScan = ref(null)

const total = computed(() => columns.value.reduce((s, c) => s + c.items.length, 0))
const activeCount = computed(
  () =>
    (columns.value.find((c) => c.key === 'contacted')?.items.length || 0) +
    (columns.value.find((c) => c.key === 'qualified')?.items.length || 0)
)
const repliedCount = computed(
  () => columns.value.find((c) => c.key === 'replied')?.items.length || 0
)
const closedCount = computed(
  () => columns.value.find((c) => c.key === 'terminated')?.items.length || 0
)

const lastScanText = computed(() => {
  if (!lastScan.value) return '尚未扫描'
  const d = new Date(lastScan.value)
  const p = (n) => String(n).padStart(2, '0')
  return `最近扫描 ${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
})

function pct(n) {
  if (!total.value) return 0
  return Math.round((n / total.value) * 100)
}

onMounted(load)

async function load() {
  const [r, ls] = await Promise.allSettled([contactApi.list(), contactApi.lastScan()])
  if (r.status === 'fulfilled') {
    const data = r.value.data
    columns.value.forEach((col) => {
      if (col.key === 'terminated') {
        col.items = data.filter((c) => TERMINATED.includes(c.status))
      } else {
        col.items = data.filter((c) => c.status === col.key)
      }
    })
  }
  if (ls.status === 'fulfilled') lastScan.value = ls.value.data?.last_scan || null
}

async function runScan() {
  scanning.value = true
  try {
    const r = await contactApi.runFollowup()
    ElMessage.success(`已提交扫描任务（${(r.data.task_id || '').slice(0, 8)}）`)
    setTimeout(() => {
      load()
      scanning.value = false
    }, 6000)
  } catch (e) {
    ElMessage.error('提交失败：' + (e.response?.data?.detail || e.message))
    scanning.value = false
  }
}
</script>

<style scoped>
.funnel { display: flex; flex-direction: column; gap: 18px; }

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
.page-sub { font-size: 13px; color: #64748b; margin: 0; max-width: 640px; }
.ph-actions { display: flex; align-items: center; gap: 10px; flex: 0 0 auto; }
.scan-time { font-size: 11px; color: #94a3b8; font-variant-numeric: tabular-nums; }

.btn-primary {
  display: inline-flex; align-items: center; gap: 6px; height: 34px; padding: 0 14px;
  background: #4f46e5; border: 1px solid #4f46e5; border-radius: 8px; color: #fff;
  font-size: 12.5px; font-weight: 600; cursor: pointer; box-shadow: 0 1px 2px rgba(79,70,229,.25);
}
.btn-primary:hover:not(:disabled) { background: #4338ca; }
.btn-primary:disabled { background: #a5b4fc; cursor: not-allowed; }
.btn-primary svg { width: 14px; height: 14px; stroke: currentColor; fill: none; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }

.stat-row { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
.stat-card {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px 17px;
  display: flex; flex-direction: column; gap: 6px; box-shadow: 0 1px 3px rgba(15,23,42,.04);
}
.sc-label { font-size: 10.5px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: .06em; }
.sc-main { display: flex; align-items: baseline; gap: 6px; }
.sc-num { font-size: 25px; font-weight: 800; color: #0f172a; letter-spacing: -.03em; font-variant-numeric: tabular-nums; line-height: 1.1; }
.sc-num.emerald { color: #059669; }
.sc-num.sky { color: #0284c7; }
.sc-num.rose { color: #e11d48; }
.sc-unit { font-size: 11px; color: #94a3b8; }
.sc-bar { height: 4px; border-radius: 3px; background: #f1f5f9; overflow: hidden; }
.sc-bar i { display: block; height: 100%; border-radius: 3px; transition: width .7s; }
.sc-bar i.indigo { background: #4f46e5; }
.sc-bar i.emerald { background: #10b981; }
.sc-bar i.sky { background: #0ea5e9; }
.sc-bar i.rose { background: #f43f5e; }

.stage-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.stage {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px 18px;
  display: flex; flex-direction: column; gap: 7px; cursor: pointer;
  transition: all .16s;
}
.stage:hover { border-color: #4f46e5; box-shadow: 0 4px 16px rgba(79,70,229,.12); transform: translateY(-2px); }
.stage.empty { opacity: .58; }
.stage-top { display: flex; align-items: center; justify-content: space-between; }
.stage-idx { font-size: 10px; font-weight: 700; color: #cbd5e1; font-family: ui-monospace, monospace; }
.stage-pct { font-size: 10.5px; font-weight: 700; color: #4f46e5; font-variant-numeric: tabular-nums; }
.stage-name-row { display: flex; align-items: center; gap: 6px; }
.stage-dot { width: 7px; height: 7px; border-radius: 50%; flex: 0 0 7px; }
.stage-name { font-size: 13px; font-weight: 700; color: #0f172a; }
.stage-num { font-size: 32px; font-weight: 800; color: #0f172a; letter-spacing: -.035em; line-height: 1.05; font-variant-numeric: tabular-nums; }
.stage-desc { font-size: 11px; color: #94a3b8; }
.stage-track { height: 4px; border-radius: 3px; background: #f1f5f9; overflow: hidden; }
.stage-track i { display: block; height: 100%; border-radius: 3px; transition: width .7s; }
.stage-link { font-size: 11px; font-weight: 600; color: #4f46e5; padding-top: 8px; border-top: 1px solid #f8fafc; margin-top: 2px; }

@media (max-width: 1200px) {
  .stat-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .stage-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 700px) {
  .stat-row, .stage-grid { grid-template-columns: minmax(0, 1fr); }
}
</style>
