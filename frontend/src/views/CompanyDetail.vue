<template>
  <div v-if="company" class="company">
    <!-- ===== 顶部操作条 ===== -->
    <div class="top-actions">
      <div class="crumbs">
        <button class="back-btn" @click="$router.push('/campaigns/' + company.campaign_id)">
          <svg viewBox="0 0 24 24"><path d="M19 12H5" /><path d="m11 6-6 6 6 6" /></svg>
          返回获客任务
        </button>
        <span class="sep">/</span>
        <button class="crumb-link" @click="$router.push('/leads')">客户池</button>
        <span class="sep">/</span>
        <span class="crumb-cur">{{ company.name }} 360° 档案</span>
      </div>
      <div class="top-right">
        <button class="btn-primary" :disabled="generating" @click="generateAll">
          <svg viewBox="0 0 24 24"><path d="m12 3 1.8 4.4L18 9l-4.2 1.6L12 15l-1.8-4.4L6 9l4.2-1.6z" /><path d="M18 15.5l.9 2.1 2.1.9-2.1.9-.9 2.1-.9-2.1-2.1-.9 2.1-.9z" /></svg>
          {{ generating ? '生成中...' : '为全部决策人生成开发信' }}
        </button>
      </div>
    </div>

    <!-- ===== 企业概览 ===== -->
    <section class="hero">
      <div class="hero-left">
        <div class="co-logo">{{ (company.name || '?').slice(0, 1).toUpperCase() }}</div>
        <div class="hero-info">
          <div class="hero-title-row">
            <h1>{{ company.name }}</h1>
            <span v-if="company.profile?.name_zh" class="name-zh">{{ company.profile.name_zh }}</span>
            <span class="ident-tag" :class="identClass(company.identity)">{{ identLabel(company.identity) }}</span>
            <span v-if="company.source" class="src-tag">{{ company.source }}</span>
          </div>
          <div class="meta-row">
            <span class="meta-item"><span class="flag">{{ flagOf(company.country) }}</span>{{ company.country || '未标注' }}</span>
            <span class="sep-dot">•</span>
            <span class="meta-item">{{ company.industry || '未分类行业' }}</span>
            <span class="sep-dot">•</span>
            <a v-if="company.website" :href="company.website" target="_blank" class="site-link">
              <svg viewBox="0 0 24 24"><path d="M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1.5 1.5" /><path d="M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1.5-1.5" /></svg>
              {{ shortUrl(company.website) }}
            </a>
            <span v-else class="meta-item muted">无官网</span>
          </div>
        </div>
      </div>

      <div class="score-box">
        <div class="score-text">
          <span class="score-label">AI 综合匹配指数</span>
          <span class="score-desc" :class="scoreClass(company.match_score)">{{ scoreLabel(company.match_score) }}</span>
        </div>
        <div class="score-ring">
          <svg viewBox="0 0 36 36">
            <circle cx="18" cy="18" r="15.9155" class="ring-bg" />
            <circle
              cx="18"
              cy="18"
              r="15.9155"
              class="ring-fg"
              :class="scoreClass(company.match_score)"
              :stroke-dasharray="(company.match_score || 0) + ', 100'"
            />
          </svg>
          <span class="score-num">{{ Math.round(company.match_score || 0) }}</span>
        </div>
      </div>
    </section>

    <!-- ===== 12 栅格主体 ===== -->
    <div class="main-grid">
      <!-- 左列 -->
      <div class="col-left">
        <!-- 板块一：基本档案 -->
        <section class="panel">
          <div class="panel-head">
            <div class="ph-title">
              <span class="bar indigo"></span>
              <h2>板块一 · 公司基本档案</h2>
            </div>
            <span class="ident-pill" :class="identClass(company.identity)">{{ identLabel(company.identity) }}</span>
          </div>

          <div class="kv-grid">
            <div class="kv">
              <span class="kv-k">公司名称</span>
              <span class="kv-v">{{ company.name }}</span>
            </div>
            <div class="kv">
              <span class="kv-k">所属国家</span>
              <span class="kv-v">{{ company.country || '未标注' }}</span>
            </div>
            <div class="kv">
              <span class="kv-k">细分行业</span>
              <span class="kv-v">{{ company.industry || '—' }}</span>
            </div>
            <div class="kv">
              <span class="kv-k">企业规模</span>
              <span class="kv-v">{{ company.profile?.size || '未收录' }}</span>
            </div>
            <div class="kv">
              <span class="kv-k">线索来源</span>
              <span class="kv-v">{{ company.source || '—' }}</span>
            </div>
            <div class="kv">
              <span class="kv-k">关联联系人</span>
              <span class="kv-v">{{ contacts.length }} 位</span>
            </div>
          </div>

          <div v-if="company.description" class="desc-box">{{ company.description }}</div>
          <div v-if="company.identity_reason" class="reason-box">
            <span class="reason-label">身份判定依据</span>
            <span class="reason-text">{{ company.identity_reason }}</span>
          </div>
        </section>

        <!-- 板块二：AI 画像 -->
        <section class="panel">
          <div class="panel-head">
            <div class="ph-title">
              <span class="bar emerald"></span>
              <h2>板块二 · AI 深度画像</h2>
            </div>
            <span class="ai-pill">
              <svg viewBox="0 0 24 24"><path d="M12 3v3.5M12 17.5V21M3 12h3.5M17.5 12H21" /><circle cx="12" cy="12" r="3.6" /></svg>
              AI 驱动分析
            </span>
          </div>

          <template v-if="hasProfile">
            <div class="sub-block">
              <div class="sub-title">
                <svg viewBox="0 0 24 24"><circle cx="6" cy="6" r="2.2" /><circle cx="18" cy="6" r="2.2" /><circle cx="12" cy="18" r="2.2" /><path d="M6 8.2v1.6a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V8.2M12 11.8v4" /></svg>
                业务描述与产业链定位
              </div>
              <div class="sub-body">{{ company.profile.business_description || '—' }}</div>
            </div>

            <div class="sub-block">
              <div class="sub-title">
                <svg viewBox="0 0 24 24"><path d="M4 18V6M10 18V10M16 18v-4M22 18V8" /></svg>
                核心需求信号
              </div>
              <div class="signals">
                <div v-for="(s, i) in company.profile.demand_signals || []" :key="i" class="signal">
                  <span class="signal-dot"></span>
                  <span>{{ s }}</span>
                </div>
                <div v-if="!(company.profile.demand_signals || []).length" class="empty-line">暂无需求信号</div>
              </div>
            </div>

            <div class="sub-block">
              <div class="sub-title">
                <svg viewBox="0 0 24 24"><path d="m12 3 2.6 5.6 6.1.8-4.5 4.2 1.2 6-5.4-3-5.4 3 1.2-6L3.3 9.4l6.1-.8z" /></svg>
                为什么值得跟进
              </div>
              <div class="match-reason">{{ company.profile.match_reason || '—' }}</div>
            </div>
          </template>

          <div v-else class="empty-state">
            尚未生成画像。回到任务详情页点击「AI 画像评分」。
          </div>
        </section>

        <!-- 板块四：客户回复 -->
        <section class="panel" v-if="replies.length">
          <div class="panel-head">
            <div class="ph-title">
              <span class="bar amber"></span>
              <h2>客户真实回复</h2>
            </div>
            <span class="reply-count">{{ replies.length }} 封</span>
          </div>

          <div class="reply-list">
            <div v-for="r in replies" :key="r.id" class="reply-item">
              <div class="reply-head">
                <span class="reply-subject">{{ r.subject }}</span>
                <span class="reply-date">{{ formatDate(r.date) }}</span>
              </div>
              <span class="reply-from">{{ r.from }}</span>
              <div class="reply-body">{{ cleanBody(r.body) }}</div>
            </div>
          </div>
        </section>
      </div>

      <!-- 右列 -->
      <div class="col-right">
        <!-- 板块三：决策人 -->
        <section class="panel">
          <div class="panel-head">
            <div class="ph-title">
              <span class="bar indigo"></span>
              <h2>板块三 · 决策人网络</h2>
            </div>
            <span class="count-pill">{{ contacts.length }}</span>
          </div>

          <div class="contact-list">
            <div v-for="c in contacts" :key="c.id" class="contact-card">
              <div class="cc-head">
                <div class="cc-avatar">{{ (c.name || '?').slice(0, 1).toUpperCase() }}</div>
                <div class="cc-info">
                  <div class="cc-name-row">
                    <span class="cc-name">{{ c.name || '联系人' }}</span>
                    <span v-if="c.is_decision_maker" class="dm-tag">决策人</span>
                  </div>
                  <span class="cc-title">{{ c.title || '职位未标注' }}</span>
                </div>
              </div>
              <div class="cc-mail">
                <svg viewBox="0 0 24 24"><rect x="3" y="5.4" width="18" height="13.2" rx="2.2" /><path d="m4.2 7.2 7.8 5.6 7.8-5.6" /></svg>
                <span>{{ c.email }}</span>
              </div>
              <div class="cc-actions">
                <span class="cc-status" :class="'cs-' + c.status">{{ contactStatusLabel(c.status) }}</span>
                <button class="btn-mini" @click="generateOne(c)">生成开发信</button>
              </div>
            </div>
            <div v-if="!contacts.length" class="empty-state small">暂无联系人</div>
          </div>
        </section>

        <!-- 右侧小结 -->
        <section class="panel">
          <div class="panel-head">
            <div class="ph-title">
              <span class="bar slate"></span>
              <h2>触达概览</h2>
            </div>
          </div>
          <div class="mini-stats">
            <div class="ms">
              <span class="ms-k">已发邮件</span>
              <span class="ms-v">{{ sentCount }}</span>
            </div>
            <div class="ms">
              <span class="ms-k">打开次数</span>
              <span class="ms-v emerald">{{ openTotal }}</span>
            </div>
            <div class="ms">
              <span class="ms-k">点击次数</span>
              <span class="ms-v indigo">{{ clickTotal }}</span>
            </div>
            <div class="ms">
              <span class="ms-k">客户回复</span>
              <span class="ms-v amber">{{ replies.length }}</span>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { companyApi, contactApi, emailApi } from '../api'

const route = useRoute()
const router = useRouter()
const company = ref(null)
const contacts = ref([])
const replies = ref([])
const emails = ref([])
const generating = ref(false)

const hasProfile = computed(
  () => company.value && company.value.profile && Object.keys(company.value.profile).length > 0
)
const sentCount = computed(() => emails.value.filter((e) => e.status === 'sent').length)
const openTotal = computed(() => emails.value.reduce((s, e) => s + (e.open_count || 0), 0))
const clickTotal = computed(() => emails.value.reduce((s, e) => s + (e.click_count || 0), 0))

const FLAGS = {
  'United States': '🇺🇸', USA: '🇺🇸', Germany: '🇩🇪', 'United Kingdom': '🇬🇧', UK: '🇬🇧',
  Japan: '🇯🇵', Australia: '🇦🇺', France: '🇫🇷', Italy: '🇮🇹', Spain: '🇪🇸',
  Netherlands: '🇳🇱', Poland: '🇵🇱', China: '🇨🇳', India: '🇮🇳', Canada: '🇨🇦',
  Brazil: '🇧🇷', Mexico: '🇲🇽', Turkey: '🇹🇷', 'South Korea': '🇰🇷', Sweden: '🇸🇪',
  Norway: '🇳🇴', Denmark: '🇩🇰', Switzerland: '🇨🇭', Austria: '🇦🇹', Belgium: '🇧🇪',
}

function flagOf(n) {
  return FLAGS[n] || '🌐'
}
function shortUrl(u) {
  return (u || '').replace(/^https?:\/\//, '').replace(/\/$/, '')
}
function identLabel(v) {
  return { buyer: '核心买家 Target Buyer', competitor: '同行 Competitor', irrelevant: '无关', unknown: '待判定' }[v] || '待判定'
}
function identClass(v) {
  return { buyer: 'id-buyer', competitor: 'id-comp', irrelevant: 'id-irr' }[v] || 'id-unk'
}
function scoreClass(s) {
  const n = s || 0
  if (n >= 90) return 'sc-high'
  if (n >= 70) return 'sc-mid'
  if (n >= 40) return 'sc-low'
  return 'sc-none'
}
function scoreLabel(s) {
  const n = s || 0
  if (n >= 90) return '极高匹配 / 优先触达'
  if (n >= 70) return '较强匹配'
  if (n >= 40) return '一般匹配'
  if (n > 0) return '弱匹配'
  return '未评分'
}
function contactStatusLabel(s) {
  return {
    pending: '待触达', qualified: '已确认', contacted: '跟进中',
    replied: '已回复', completed: '已完成', rejected: '已拒绝',
    unsubscribed: '已退订', invalid: '邮箱无效',
  }[s] || s
}
function formatDate(v) {
  if (!v) return ''
  const d = new Date(v)
  if (isNaN(d)) return v
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}
function cleanBody(body) {
  // 去掉引用的原始邮件部分
  const cut = ['---Original---', '------------------ Original', 'On '].map((k) => body.indexOf(k)).filter((i) => i > 0)
  const idx = cut.length ? Math.min(...cut) : -1
  return (idx > 0 ? body.slice(0, idx) : body).trim()
}

async function load() {
  const r = await companyApi.get(route.params.id)
  company.value = r.data
  const [cr, rr, er] = await Promise.all([
    contactApi.list(),
    companyApi.replies(company.value.id),
    emailApi.list(),
  ])
  contacts.value = cr.data.filter((c) => c.company_id === company.value.id)
  replies.value = rr.data
  emails.value = er.data.filter((e) => e.company_id === company.value.id)
}

async function generateOne(c) {
  generating.value = true
  try {
    await emailApi.generate(company.value.id, c.id)
    ElMessage.success('已生成开发信草稿')
    router.push('/emails')
  } catch (e) {
    ElMessage.error('生成失败：' + (e.response?.data?.detail || e.message))
  } finally {
    generating.value = false
  }
}

async function generateAll() {
  if (!contacts.value.length) {
    ElMessage.warning('该公司还没有联系人，先去任务详情页提取联系人')
    return
  }
  generating.value = true
  let ok = 0
  try {
    for (const c of contacts.value) {
      try {
        await emailApi.generate(company.value.id, c.id)
        ok++
      } catch (e) {
        /* 单个失败继续 */
      }
    }
    ElMessage.success(`已生成 ${ok} 封开发信草稿`)
    router.push('/emails')
  } finally {
    generating.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.company { display: flex; flex-direction: column; gap: 16px; }

/* 顶部操作条 */
.top-actions { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }
.crumbs { display: flex; align-items: center; gap: 8px; font-size: 12px; }
.back-btn {
  display: inline-flex; align-items: center; gap: 5px; height: 30px; padding: 0 11px;
  background: #eef2ff; border: 1px solid #e0e7ff; border-radius: 7px;
  color: #4338ca; font-size: 12px; font-weight: 600; cursor: pointer;
}
.back-btn:hover { background: #e0e7ff; }
.back-btn svg { width: 13px; height: 13px; stroke: currentColor; fill: none; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
.sep { color: #cbd5e1; }
.crumb-link { background: none; border: 0; color: #64748b; font-size: 12px; cursor: pointer; padding: 0; }
.crumb-link:hover { color: #0f172a; }
.crumb-cur { color: #0f172a; font-weight: 600; }

.btn-primary {
  display: inline-flex; align-items: center; gap: 6px; height: 34px; padding: 0 14px;
  background: #4f46e5; border: 1px solid #4f46e5; border-radius: 8px; color: #fff;
  font-size: 12.5px; font-weight: 600; cursor: pointer; box-shadow: 0 1px 2px rgba(79,70,229,.25);
}
.btn-primary:hover:not(:disabled) { background: #4338ca; }
.btn-primary:disabled { background: #a5b4fc; cursor: not-allowed; }
.btn-primary svg { width: 14px; height: 14px; stroke: currentColor; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }

/* Hero */
.hero {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px 22px;
  display: flex; align-items: center; justify-content: space-between; gap: 22px; flex-wrap: wrap;
  box-shadow: 0 1px 3px rgba(15,23,42,.04);
}
.hero-left { display: flex; align-items: flex-start; gap: 16px; min-width: 0; }
.co-logo {
  width: 56px; height: 56px; flex: 0 0 56px; border-radius: 13px; display: grid; place-items: center;
  background: linear-gradient(135deg, #6366f1, #4f46e5); color: #fff; font-size: 22px; font-weight: 700;
  box-shadow: 0 3px 10px rgba(79,70,229,.25);
}
.hero-info { display: flex; flex-direction: column; gap: 7px; min-width: 0; }
.hero-title-row { display: flex; align-items: center; gap: 9px; flex-wrap: wrap; }
.hero-title-row h1 { font-size: 22px; font-weight: 700; color: #0f172a; margin: 0; letter-spacing: -.025em; }
.name-zh { font-size: 13px; color: #64748b; font-weight: 500; }
.ident-tag, .src-tag { font-size: 10.5px; font-weight: 600; padding: 2px 8px; border-radius: 999px; }
.id-buyer { background: #ecfdf5; color: #047857; border: 1px solid #d1fae5; }
.id-comp { background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }
.id-irr { background: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; }
.id-unk { background: #fffbeb; color: #b45309; border: 1px solid #fef3c7; }
.src-tag { background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; font-family: ui-monospace, monospace; }
.meta-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; font-size: 12px; color: #64748b; }
.meta-item { display: inline-flex; align-items: center; gap: 4px; }
.meta-item.muted { color: #cbd5e1; }
.flag { font-size: 13px; }
.sep-dot { color: #cbd5e1; }
.site-link { display: inline-flex; align-items: center; gap: 4px; color: #4f46e5; font-family: ui-monospace, monospace; font-size: 11.5px; }
.site-link:hover { text-decoration: underline; }
.site-link svg { width: 12px; height: 12px; stroke: currentColor; fill: none; stroke-width: 1.9; stroke-linecap: round; stroke-linejoin: round; }

.score-box {
  display: flex; align-items: center; gap: 14px; padding: 12px 18px;
  background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 11px; flex-shrink: 0;
}
.score-text { display: flex; flex-direction: column; align-items: flex-end; gap: 2px; }
.score-label { font-size: 10px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: .06em; }
.score-desc { font-size: 11.5px; font-weight: 700; }
.score-desc.sc-high { color: #047857; }
.score-desc.sc-mid { color: #4f46e5; }
.score-desc.sc-low, .score-desc.sc-none { color: #94a3b8; }
.score-ring { position: relative; width: 54px; height: 54px; }
.score-ring svg { width: 54px; height: 54px; transform: rotate(-90deg); }
.ring-bg { fill: none; stroke: #e2e8f0; stroke-width: 3.2; }
.ring-fg { fill: none; stroke-width: 3.6; stroke-linecap: round; transition: stroke-dasharray .7s; }
.ring-fg.sc-high { stroke: #10b981; }
.ring-fg.sc-mid { stroke: #4f46e5; }
.ring-fg.sc-low { stroke: #94a3b8; }
.ring-fg.sc-none { stroke: #cbd5e1; }
.score-num {
  position: absolute; inset: 0; display: grid; place-items: center;
  font-size: 16px; font-weight: 800; color: #0f172a; font-variant-numeric: tabular-nums;
}

/* 栅格 */
.main-grid { display: grid; grid-template-columns: minmax(0, 8fr) minmax(0, 4fr); gap: 16px; align-items: start; }
.col-left, .col-right { display: flex; flex-direction: column; gap: 16px; min-width: 0; }

.panel { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 20px; box-shadow: 0 1px 3px rgba(15,23,42,.04); display: flex; flex-direction: column; gap: 14px; }
.panel-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding-bottom: 12px; border-bottom: 1px solid #f1f5f9; }
.ph-title { display: flex; align-items: center; gap: 9px; }
.bar { width: 3px; height: 17px; border-radius: 2px; }
.bar.indigo { background: #4f46e5; }
.bar.emerald { background: #10b981; }
.bar.amber { background: #f59e0b; }
.bar.slate { background: #94a3b8; }
.ph-title h2 { font-size: 14px; font-weight: 700; color: #0f172a; margin: 0; }
.ident-pill, .count-pill, .reply-count {
  font-size: 10.5px; font-weight: 700; padding: 2px 9px; border-radius: 999px;
}
.count-pill, .reply-count { background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; }
.ai-pill {
  display: inline-flex; align-items: center; gap: 4px; font-size: 10px; font-weight: 700;
  color: #4338ca; background: #eef2ff; border: 1px solid #e0e7ff; padding: 2px 8px; border-radius: 999px;
}
.ai-pill svg { width: 11px; height: 11px; stroke: currentColor; fill: none; stroke-width: 2; }

.kv-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
.kv { background: #f8fafc; border: 1px solid #f1f5f9; border-radius: 8px; padding: 10px 12px; display: flex; flex-direction: column; gap: 3px; }
.kv-k { font-size: 10px; color: #94a3b8; font-weight: 600; }
.kv-v { font-size: 12px; color: #0f172a; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.desc-box { font-size: 12px; color: #475569; line-height: 1.75; background: #f8fafc; border: 1px solid #f1f5f9; border-radius: 8px; padding: 12px 14px; }
.reason-box { display: flex; flex-direction: column; gap: 4px; padding: 11px 14px; background: #fffbeb; border: 1px solid #fef3c7; border-radius: 8px; }
.reason-label { font-size: 10px; font-weight: 700; color: #b45309; text-transform: uppercase; letter-spacing: .05em; }
.reason-text { font-size: 11.5px; color: #78350f; line-height: 1.65; }

.sub-block { display: flex; flex-direction: column; gap: 7px; }
.sub-title { display: flex; align-items: center; gap: 6px; font-size: 11.5px; font-weight: 700; color: #334155; }
.sub-title svg { width: 14px; height: 14px; stroke: #4f46e5; fill: none; stroke-width: 1.9; stroke-linecap: round; stroke-linejoin: round; }
.sub-body { font-size: 12px; color: #475569; line-height: 1.8; background: #f8fafc; border: 1px solid #f1f5f9; border-radius: 8px; padding: 12px 14px; }

.signals { display: flex; flex-direction: column; gap: 6px; }
.signal {
  display: flex; align-items: flex-start; gap: 7px; font-size: 11.5px; color: #334155;
  background: #f8fafc; border: 1px solid #f1f5f9; border-radius: 7px; padding: 8px 11px; line-height: 1.6;
}
.signal-dot { width: 5px; height: 5px; border-radius: 50%; background: #10b981; flex: 0 0 5px; margin-top: 6px; }
.match-reason { font-size: 12px; color: #1d4ed8; line-height: 1.75; background: #eef2ff; border: 1px solid #e0e7ff; border-radius: 8px; padding: 12px 14px; }

.empty-line { font-size: 11.5px; color: #94a3b8; padding: 8px 0; }
.empty-state { text-align: center; padding: 30px 20px; color: #94a3b8; font-size: 12px; line-height: 1.7; }
.empty-state.small { padding: 20px; }

/* 客户回复 */
.reply-list { display: flex; flex-direction: column; gap: 10px; }
.reply-item { border: 1px solid #e2e8f0; border-radius: 9px; padding: 12px 14px; display: flex; flex-direction: column; gap: 5px; background: #f8fafc; }
.reply-head { display: flex; align-items: baseline; justify-content: space-between; gap: 10px; }
.reply-subject { font-size: 12.5px; font-weight: 700; color: #0f172a; }
.reply-date { font-size: 10px; color: #94a3b8; white-space: nowrap; font-variant-numeric: tabular-nums; }
.reply-from { font-size: 11px; color: #4f46e5; font-family: ui-monospace, monospace; }
.reply-body {
  font-size: 12px; color: #334155; line-height: 1.8; white-space: pre-wrap;
  background: #fff; border: 1px solid #f1f5f9; border-radius: 7px; padding: 11px 13px; margin-top: 3px;
}

/* 决策人 */
.contact-list { display: flex; flex-direction: column; gap: 10px; }
.contact-card { border: 1px solid #e2e8f0; border-radius: 9px; padding: 12px; display: flex; flex-direction: column; gap: 8px; background: #f8fafc; }
.cc-head { display: flex; align-items: center; gap: 9px; }
.cc-avatar {
  width: 32px; height: 32px; flex: 0 0 32px; border-radius: 999px; display: grid; place-items: center;
  background: #eef2ff; border: 1px solid #e0e7ff; color: #4338ca; font-size: 12px; font-weight: 700;
}
.cc-info { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.cc-name-row { display: flex; align-items: center; gap: 5px; }
.cc-name { font-size: 12.5px; font-weight: 600; color: #0f172a; }
.dm-tag { font-size: 9px; font-weight: 700; color: #b45309; background: #fffbeb; border: 1px solid #fef3c7; padding: 0 5px; border-radius: 3px; }
.cc-title { font-size: 10.5px; color: #64748b; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cc-mail { display: flex; align-items: center; gap: 5px; font-size: 10.5px; color: #4f46e5; font-family: ui-monospace, monospace; overflow: hidden; }
.cc-mail span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cc-mail svg { width: 12px; height: 12px; stroke: currentColor; fill: none; stroke-width: 1.9; flex: 0 0 12px; }
.cc-actions { display: flex; align-items: center; justify-content: space-between; gap: 8px; padding-top: 7px; border-top: 1px solid #e2e8f0; }
.cc-status { font-size: 9.5px; font-weight: 600; padding: 1px 6px; border-radius: 4px; }
.cs-pending { background: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; }
.cs-qualified { background: #eef2ff; color: #4338ca; border: 1px solid #e0e7ff; }
.cs-contacted { background: #f0f9ff; color: #0284c7; border: 1px solid #e0f2fe; }
.cs-replied { background: #ecfdf5; color: #047857; border: 1px solid #d1fae5; }
.cs-completed { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
.cs-rejected, .cs-unsubscribed, .cs-invalid { background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }
.btn-mini {
  height: 25px; padding: 0 9px; border-radius: 5px; background: #4f46e5; border: 1px solid #4f46e5;
  color: #fff; font-size: 10.5px; font-weight: 600; cursor: pointer; white-space: nowrap;
}
.btn-mini:hover { background: #4338ca; }

.mini-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 9px; }
.ms { background: #f8fafc; border: 1px solid #f1f5f9; border-radius: 8px; padding: 10px 12px; display: flex; flex-direction: column; gap: 2px; }
.ms-k { font-size: 10px; color: #94a3b8; font-weight: 600; }
.ms-v { font-size: 18px; font-weight: 700; color: #0f172a; font-variant-numeric: tabular-nums; }
.ms-v.emerald { color: #059669; }
.ms-v.indigo { color: #4f46e5; }
.ms-v.amber { color: #d97706; }

@media (max-width: 1300px) {
  .main-grid { grid-template-columns: minmax(0, 1fr); }
}
@media (max-width: 760px) {
  .kv-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>
