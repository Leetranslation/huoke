<template>
  <div class="dash">
    <!-- ===== Hero ===== -->
    <section class="hero">
      <div class="hero-glow"></div>
      <div class="hero-inner">
        <div class="hero-left">
          <div class="hero-badges">
            <span class="badge-live"><i class="pulse"></i>引擎运行正常</span>
            <span class="badge-sep">•</span>
            <span class="hero-meta">
              {{ campaigns.length }} 个任务 · {{ companies.length }} 家企业 · {{ contacts.length }} 位联系人
            </span>
          </div>
          <h1 class="hero-title">智能获客引擎 <span>/ 全景数据</span></h1>
          <p class="hero-sub">自动挖掘海外买家、生成个性化开发信、追踪投递效果与客户回复。</p>
        </div>
        <div class="hero-actions">
          <button class="btn-solid" @click="$router.push('/campaigns')">
            <svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14" /></svg>新建获客任务
          </button>
          <button class="btn-outline" @click="$router.push('/leads')">
            <svg viewBox="0 0 24 24"><path d="M16 20v-1.4a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4V20" /><circle cx="9.5" cy="7.6" r="3.3" /></svg>进入客户池
          </button>
          <button class="btn-outline" @click="$router.push('/campaigns')">
            <svg viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h10" /></svg>查看全部任务
          </button>
        </div>
      </div>
    </section>

    <!-- ===== 4 指标卡 ===== -->
    <section class="metrics">
      <div v-for="m in metrics" :key="m.label" class="metric">
        <div class="metric-top">
          <div class="metric-main">
            <div class="metric-label">{{ m.label }}</div>
            <div class="metric-value"><b>{{ m.value }}</b><span>{{ m.unit }}</span></div>
          </div>
          <span class="metric-badge" :class="'tone-' + m.tone">{{ m.badge }}</span>
        </div>
        <div class="metric-foot">
          <span class="foot-dot" :style="{ background: m.dot }"></span>
          <span class="foot-text">{{ m.foot }}</span>
        </div>
      </div>
    </section>

    <!-- ===== 主体 7/5 ===== -->
    <div class="dash-grid">
      <!-- 左栏 -->
      <div class="col-left">
        <!-- 国家分布 -->
        <section class="panel">
          <div class="panel-head">
            <div class="ph-left">
              <span class="ph-ico">
                <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" /><path d="M3 12h18" /><path d="M12 3a15 15 0 0 1 0 18a15 15 0 0 1 0-18" /></svg>
              </span>
              <div>
                <h2>全球目标客户分布</h2>
                <p>按国家聚合线索量与买家占比</p>
              </div>
            </div>
            <span class="chip-live">实时</span>
          </div>

          <div class="geo-list">
            <div v-for="g in geo" :key="g.name" class="geo-row">
              <div class="geo-top">
                <div class="geo-name-wrap">
                  <span class="geo-code">{{ g.code }}</span>
                  <span class="geo-name">{{ g.name }}</span>
                </div>
                <div class="geo-nums">
                  <span class="geo-count">{{ g.value }} 家</span>
                  <span class="geo-buyer">买家 {{ g.buyerPct }}%</span>
                </div>
              </div>
              <div class="geo-track"><i :style="{ width: g.pct + '%' }"></i></div>
            </div>
          </div>
          <div v-if="!geo.length" class="empty">暂无国家数据</div>
        </section>

        <!-- 最近任务 -->
        <section class="panel">
          <div class="panel-head">
            <div class="ph-left">
              <span class="ph-ico">
                <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8" /><circle cx="12" cy="12" r="2.6" /></svg>
              </span>
              <div>
                <h2>最近获客任务</h2>
                <p>流水线推进状态</p>
              </div>
            </div>
            <button class="link-btn" @click="$router.push('/campaigns')">全部历史 →</button>
          </div>

          <div class="task-list">
            <div v-for="t in recentTasks" :key="t.id" class="task-card" @click="$router.push('/campaigns/' + t.id)">
              <div class="task-top">
                <div class="task-name-wrap">
                  <span class="task-dot" :class="t.done ? 'done' : 'run'"></span>
                  <h3 class="task-name">{{ t.name }}</h3>
                </div>
                <div class="task-right">
                  <span class="task-status" :class="t.done ? 'st-done' : 'st-run'">{{ t.statusLabel }}</span>
                  <span class="task-time">{{ t.timeLabel }}</span>
                </div>
              </div>
              <div class="task-fields">
                <div>产品: <b>{{ t.product || '—' }}</b></div>
                <div>市场: <b>{{ t.market || '—' }}</b></div>
                <div>公司: <b class="mono">{{ t.companies }} 家</b></div>
                <div>联系人: <b class="mono">{{ t.contacts }} 位</b></div>
              </div>
              <div class="task-steps">
                <span v-for="(s, i) in t.steps" :key="i" class="step" :class="s"></span>
                <span class="step-label">{{ t.doneCount }}/5 步</span>
              </div>
            </div>
            <div v-if="!recentTasks.length" class="empty">暂无任务</div>
          </div>
        </section>
      </div>

      <!-- 右栏 -->
      <div class="col-right">
        <!-- AI 事件流 -->
        <section class="panel">
          <div class="panel-head">
            <div class="ph-left">
              <span class="ph-ico green">
                <svg viewBox="0 0 24 24"><rect x="6.5" y="6.5" width="11" height="11" rx="2" /><path d="M12 3v3.5M12 17.5V21M3 12h3.5M17.5 12H21" /></svg>
              </span>
              <div>
                <h2>AI 实时处理流水线</h2>
                <p>画像与开发信生成记录</p>
              </div>
            </div>
            <span class="pulse-dot"></span>
          </div>

          <div class="event-list">
            <div v-for="e in aiEvents" :key="e.id" class="event">
              <span class="event-ico" :class="e.tone">
                <svg v-if="e.tone === 'indigo'" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" /><path d="M3 12h18" /></svg>
                <svg v-else-if="e.tone === 'green'" viewBox="0 0 24 24"><path d="M12 3v18M3 12h18" /></svg>
                <svg v-else viewBox="0 0 24 24"><path d="M4 18V6l8 6 8-6v12" /></svg>
              </span>
              <div class="event-body">
                <div class="event-head">
                  <span class="event-tag" :class="e.tone">[{{ e.tag }}]</span>
                  <span class="event-time">{{ e.timeLabel }}</span>
                </div>
                <p class="event-text" v-html="e.text"></p>
              </div>
            </div>
            <div v-if="!aiEvents.length" class="empty">暂无 AI 处理记录</div>
          </div>
        </section>

        <!-- 高潜力推荐 -->
        <section class="panel">
          <div class="panel-head">
            <div class="ph-left">
              <span class="ph-ico">
                <svg viewBox="0 0 24 24"><path d="m12 3 2.6 5.6 6.1.8-4.5 4.2 1.2 6-5.4-3-5.4 3 1.2-6L3.3 9.4l6.1-.8z" /></svg>
              </span>
              <div>
                <h2>高潜力待触达买家</h2>
                <p>按 AI 匹配分排序</p>
              </div>
            </div>
            <button class="link-btn" @click="$router.push('/leads')">全部推荐 →</button>
          </div>

          <div class="lead-list">
            <div v-for="l in topLeads" :key="l.id" class="lead-card">
              <div class="lead-top">
                <div class="lead-main">
                  <div class="lead-name-row">
                    <span class="lead-name">{{ l.name }}</span>
                    <span class="lead-country">{{ l.country || '—' }}</span>
                  </div>
                  <span class="lead-contact">{{ l.contact }}</span>
                </div>
                <span class="lead-score" :class="{ high: l.score >= 80 }">{{ l.score }} 分</span>
              </div>
              <div class="lead-foot">
                <a v-if="l.website" :href="l.website" target="_blank" class="lead-site">{{ l.website }}</a>
                <span v-else class="lead-site muted">无官网</span>
                <button class="btn-mini" @click.stop="$router.push('/companies/' + l.id)">查看详情</button>
              </div>
            </div>
            <div v-if="!topLeads.length" class="empty">暂无已评分客户</div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { campaignApi, contactApi, emailApi, companyApi } from '../api'

const campaigns = ref([])
const companies = ref([])
const contacts = ref([])
const emails = ref([])

const COUNTRY_CODE = {
  'United States': 'US', USA: 'US', US: 'US',
  Germany: 'DE', Deutschland: 'DE',
  'United Kingdom': 'GB', UK: 'GB',
  Japan: 'JP',
  Australia: 'AU',
  France: 'FR',
  Italy: 'IT',
  Spain: 'ES',
  Netherlands: 'NL',
  Poland: 'PL',
  China: 'CN',
  India: 'IN',
  Canada: 'CA',
  Brazil: 'BR',
  Mexico: 'MX',
  Turkey: 'TR',
  'South Korea': 'KR',
  Korea: 'KR',
  Sweden: 'SE',
  Norway: 'NO',
  Denmark: 'DK',
  Switzerland: 'CH',
  Austria: 'AT',
  Belgium: 'BE',
  'Czech Republic': 'CZ',
  Vietnam: 'VN',
  Thailand: 'TH',
  Indonesia: 'ID',
  Malaysia: 'MY',
  Singapore: 'SG',
}

function codeOf(name) {
  if (!name) return '--'
  const k = Object.keys(COUNTRY_CODE).find((x) => x.toLowerCase() === String(name).toLowerCase())
  return k ? COUNTRY_CODE[k] : String(name).slice(0, 2).toUpperCase()
}

// ---------- 指标 ----------
const metrics = computed(() => {
  const sentEmails = emails.value.filter((e) => e.status === 'sent')
  const opens = emails.value.reduce((s, e) => s + (e.open_count || 0), 0)
  const clicks = emails.value.reduce((s, e) => s + (e.click_count || 0), 0)
  const openRate = sentEmails.length ? Math.round((opens / sentEmails.length) * 100) : 0
  const clickRate = sentEmails.length ? Math.round((clicks / sentEmails.length) * 100) : 0
  const replied = contacts.value.filter((c) => c.status === 'replied').length

  const buyers = companies.value.filter((c) => c.identity === 'buyer').length
  const buyerPct = companies.value.length ? Math.round((buyers / companies.value.length) * 100) : 0

  const countries = new Set(companies.value.map((c) => c.country).filter(Boolean)).size
  const activeTasks = campaigns.value.filter((c) => c.status !== 'completed').length

  return [
    {
      label: '获客任务总数',
      value: campaigns.value.length,
      unit: '个',
      badge: `进行中 ${activeTasks}`,
      tone: 'indigo',
      foot: `覆盖 ${countries} 个国家`,
      dot: '#4f46e5',
    },
    {
      label: '挖掘客户总数',
      value: companies.value.length,
      unit: '家',
      badge: `买家 ${buyerPct}%`,
      tone: 'green',
      foot: `其中买家 ${buyers} 家`,
      dot: '#10b981',
    },
    {
      label: '邮件触达指标',
      value: sentEmails.length,
      unit: '封已发',
      badge: `${replied} 封回复`,
      tone: 'amber',
      foot: `打开 ${openRate}% · 点击 ${clickRate}%`,
      dot: '#f59e0b',
    },
    {
      label: '已提取联系人',
      value: contacts.value.length,
      unit: '位',
      badge: `${companies.value.length} 家公司`,
      tone: 'indigo',
      foot: `平均每家 ${companies.value.length ? (contacts.value.length / companies.value.length).toFixed(1) : 0} 位`,
      dot: '#6366f1',
    },
  ]
})

// ---------- 国家分布 ----------
const geo = computed(() => {
  const map = {}
  companies.value.forEach((c) => {
    const name = c.country || '未标注'
    if (!map[name]) map[name] = { total: 0, buyers: 0 }
    map[name].total++
    if (c.identity === 'buyer') map[name].buyers++
  })
  const entries = Object.entries(map).sort((a, b) => b[1].total - a[1].total).slice(0, 7)
  const max = Math.max(1, ...entries.map(([, v]) => v.total))
  return entries.map(([name, v]) => ({
    name,
    code: codeOf(name),
    value: v.total,
    buyerPct: v.total ? Math.round((v.buyers / v.total) * 100) : 0,
    pct: Math.round((v.total / max) * 100),
  }))
})

// ---------- 最近任务 ----------
const recentTasks = computed(() => {
  return campaigns.value.slice(0, 3).map((c) => {
    const cos = companies.value.filter((x) => x.campaign_id === c.id)
    const companyIds = new Set(cos.map((x) => x.id))
    const cs = contacts.value.filter((x) => companyIds.has(x.company_id))
    const em = emails.value.filter((x) => companyIds.has(x.company_id))
    const profiled = cos.filter((x) => x.profile && Object.keys(x.profile).length).length

    const steps = [
      cos.length > 0,                              // 已爬取线索
      profiled > 0,                                // 已画像
      cs.length > 0,                               // 已提取联系人
      em.filter((x) => x.status === 'approved' || x.status === 'sent').length > 0, // 已生成/批邮件
      em.filter((x) => x.status === 'sent').length > 0, // 已发送
    ]
    const doneCount = steps.filter(Boolean).length
    const done = doneCount === 5

    return {
      id: c.id,
      name: c.name,
      product: c.product_name,
      market: (c.target_market || []).join(' / '),
      companies: cos.length,
      contacts: cs.length,
      steps: steps.map((s) => (s ? 'on' : 'off')),
      doneCount,
      done,
      statusLabel: done ? '已完成' : doneCount > 0 ? '进行中' : '待启动',
      timeLabel: (c.created_at || '').slice(5, 10).replace('-', '/'),
    }
  })
})

// ---------- AI 事件流 ----------
const aiEvents = computed(() => {
  const events = []
  const profiled = companies.value
    .filter((c) => c.profile && Object.keys(c.profile).length)
    .slice(0, 6)
  profiled.slice(0, 2).forEach((c) => {
    const reason = (c.profile.match_reason || '').slice(0, 60)
    events.push({
      id: 'p' + c.id,
      tag: 'AI 画像评分',
      tone: 'green',
      timeLabel: '已完成',
      text: `${c.name} 匹配分 <b>${c.match_score}</b>${reason ? '，' + reason : ''}`,
    })
  })
  emails.value.slice(0, 2).forEach((e) => {
    events.push({
      id: 'e' + e.id,
      tag: '开发信生成',
      tone: 'amber',
      timeLabel: e.status === 'sent' ? '已发送' : '待处理',
      text: `《${(e.subject || '').slice(0, 32)}》→ ${e.contact_email || e.company_name || ''}`,
    })
  })
  if (!events.length) {
    const withDna = campaigns.value.filter((c) => c.dna)
    withDna.slice(0, 2).forEach((c) => {
      events.push({
        id: 'd' + c.id,
        tag: 'AI 官网分析',
        tone: 'indigo',
        timeLabel: '已生成',
        text: `${c.name}：核心产品 <b>${c.dna?.product_name || c.product_name}</b>，目标客户 ${(c.dna?.customer_types || []).length} 类`,
      })
    })
  }
  return events.slice(0, 4)
})

// ---------- 高潜力 ----------
const topLeads = computed(() => {
  return companies.value
    .filter((c) => (c.match_score || 0) > 0)
    .sort((a, b) => b.match_score - a.match_score)
    .slice(0, 3)
    .map((c) => {
      const cs = contacts.value.filter((x) => x.company_id === c.id)
      const first = cs[0]
      return {
        id: c.id,
        name: c.name,
        country: c.country,
        website: c.website,
        score: c.match_score,
        contact: first ? `${first.title || '联系人'}: ${first.email}` : '暂无联系人',
      }
    })
})

onMounted(async () => {
  const [c, co, ct, e] = await Promise.all([
    campaignApi.list(),
    companyApi.list(),
    contactApi.list(),
    emailApi.list(),
  ])
  campaigns.value = c.data
  companies.value = co.data
  contacts.value = ct.data
  emails.value = e.data
})
</script>

<style scoped>
.dash { display: flex; flex-direction: column; gap: 16px; }

/* ===== Hero ===== */
.hero {
  position: relative; overflow: hidden; background: #fff;
  border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px 24px;
  box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
}
.hero-glow {
  position: absolute; right: -60px; top: -60px; width: 320px; height: 320px; border-radius: 50%;
  background: radial-gradient(circle, rgba(99,102,241,.16), rgba(16,185,129,.10) 55%, transparent 70%);
  pointer-events: none;
}
.hero-inner {
  position: relative; display: flex; align-items: center; justify-content: space-between;
  gap: 24px; flex-wrap: wrap;
}
.hero-left { display: flex; flex-direction: column; gap: 8px; min-width: 0; }
.hero-badges { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.badge-live {
  display: inline-flex; align-items: center; gap: 6px; padding: 3px 9px; border-radius: 999px;
  background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0;
  font-size: 11px; font-weight: 600;
}
.pulse {
  width: 6px; height: 6px; border-radius: 50%; background: #10b981;
  box-shadow: 0 0 0 0 rgba(16,185,129,.6); animation: pl 2s infinite;
}
@keyframes pl {
  0% { box-shadow: 0 0 0 0 rgba(16,185,129,.5); }
  70% { box-shadow: 0 0 0 6px rgba(16,185,129,0); }
  100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); }
}
.badge-sep { color: #cbd5e1; }
.hero-meta { font-size: 11.5px; color: #64748b; font-variant-numeric: tabular-nums; }
.hero-title {
  font-size: 23px; font-weight: 700; letter-spacing: -0.025em; color: #0f172a; margin: 0;
}
.hero-title span { font-size: 15px; font-weight: 400; color: #4f46e5; }
.hero-sub { font-size: 13px; color: #475569; margin: 0; }
.hero-actions { display: flex; gap: 8px; flex-wrap: wrap; }

.btn-solid, .btn-outline {
  display: inline-flex; align-items: center; gap: 6px; height: 34px; padding: 0 14px;
  border-radius: 8px; font-size: 12.5px; font-weight: 600; cursor: pointer; white-space: nowrap;
  transition: all .15s;
}
.btn-solid { background: #4f46e5; border: 1px solid #4f46e5; color: #fff; box-shadow: 0 1px 2px rgba(79,70,229,.25); }
.btn-solid:hover { background: #4338ca; }
.btn-outline { background: #fff; border: 1px solid #e2e8f0; color: #334155; box-shadow: 0 1px 2px rgba(15,23,42,.03); }
.btn-outline:hover { background: #f8fafc; border-color: #cbd5e1; color: #0f172a; }
.btn-solid svg, .btn-outline svg {
  width: 14px; height: 14px; stroke: currentColor; fill: none; stroke-width: 1.8;
  stroke-linecap: round; stroke-linejoin: round;
}

/* ===== 指标卡 ===== */
.metrics { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
.metric {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px 18px;
  box-shadow: 0 1px 3px rgba(15,23,42,.04); display: flex; flex-direction: column; gap: 12px;
}
.metric-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; }
.metric-main { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.metric-label {
  font-size: 10.5px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: .06em;
}
.metric-value { display: flex; align-items: baseline; gap: 5px; }
.metric-value b {
  font-size: 25px; font-weight: 700; color: #0f172a; letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums; line-height: 1.15;
}
.metric-value span { font-size: 11.5px; color: #64748b; }
.metric-badge {
  padding: 2px 7px; border-radius: 999px; font-size: 10.5px; font-weight: 600; white-space: nowrap;
  font-variant-numeric: tabular-nums;
}
.tone-indigo { background: #eef2ff; color: #4338ca; border: 1px solid #c7d2fe; }
.tone-green { background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; }
.tone-amber { background: #fffbeb; color: #b45309; border: 1px solid #fde68a; }
.metric-foot {
  display: flex; align-items: center; gap: 6px; padding-top: 10px; border-top: 1px solid #f1f5f9;
  font-size: 11.5px; color: #64748b;
}
.foot-dot { width: 6px; height: 6px; border-radius: 50%; flex: 0 0 6px; }
.foot-text { font-variant-numeric: tabular-nums; }

/* ===== 主体 ===== */
.dash-grid { display: grid; grid-template-columns: minmax(0, 7fr) minmax(0, 5fr); gap: 16px; align-items: start; }
.col-left, .col-right { display: flex; flex-direction: column; gap: 16px; min-width: 0; }

.panel {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 20px;
  box-shadow: 0 1px 3px rgba(15,23,42,.04); display: flex; flex-direction: column; gap: 14px;
}
.panel-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.ph-left { display: flex; align-items: flex-start; gap: 10px; }
.ph-ico {
  width: 30px; height: 30px; flex: 0 0 30px; border-radius: 8px; display: grid; place-items: center;
  background: #eef2ff; color: #4f46e5;
}
.ph-ico.green { background: #ecfdf5; color: #059669; }
.ph-ico svg { width: 16px; height: 16px; stroke: currentColor; fill: none; stroke-width: 1.7; stroke-linecap: round; stroke-linejoin: round; }
.panel-head h2 { font-size: 14px; font-weight: 700; color: #0f172a; margin: 0; letter-spacing: -0.01em; }
.panel-head p { font-size: 11.5px; color: #64748b; margin: 2px 0 0; }
.chip-live {
  font-size: 10.5px; font-weight: 600; color: #047857; background: #ecfdf5;
  border: 1px solid #a7f3d0; padding: 2px 7px; border-radius: 5px; white-space: nowrap;
}
.link-btn {
  background: none; border: 0; color: #4f46e5; font-size: 11.5px; font-weight: 600;
  cursor: pointer; padding: 0; white-space: nowrap;
}
.link-btn:hover { color: #4338ca; }
.pulse-dot {
  width: 8px; height: 8px; border-radius: 50%; background: #10b981; flex: 0 0 8px; margin-top: 6px;
}

/* 国家分布 */
.geo-list { display: flex; flex-direction: column; gap: 2px; }
.geo-row { padding: 7px 6px; border-radius: 7px; transition: background .15s; }
.geo-row:hover { background: #f8fafc; }
.geo-top { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 5px; }
.geo-name-wrap { display: flex; align-items: center; gap: 7px; min-width: 0; }
.geo-code {
  width: 24px; height: 17px; display: grid; place-items: center; flex: 0 0 24px;
  background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 3px;
  font-size: 9.5px; font-weight: 700; color: #475569; font-family: ui-monospace, monospace;
}
.geo-name { font-size: 12.5px; font-weight: 600; color: #0f172a; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.geo-nums { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.geo-count { font-size: 11.5px; color: #334155; font-weight: 500; font-variant-numeric: tabular-nums; }
.geo-buyer {
  font-size: 10px; font-weight: 600; color: #047857; background: #ecfdf5;
  border: 1px solid #a7f3d0; padding: 1px 5px; border-radius: 4px;
}
.geo-track { height: 6px; border-radius: 4px; background: #f1f5f9; overflow: hidden; }
.geo-track i { display: block; height: 100%; border-radius: 4px; background: #4f46e5; transition: width .7s ease; }

/* 任务卡 */
.task-list { display: flex; flex-direction: column; gap: 10px; }
.task-card {
  background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 9px; padding: 12px 14px;
  display: flex; flex-direction: column; gap: 9px; cursor: pointer; transition: all .15s;
}
.task-card:hover { background: #f1f5f9; border-color: #cbd5e1; }
.task-top { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.task-name-wrap { display: flex; align-items: center; gap: 7px; min-width: 0; }
.task-dot { width: 7px; height: 7px; border-radius: 50%; flex: 0 0 7px; }
.task-dot.run { background: #10b981; }
.task-dot.done { background: #4f46e5; }
.task-name { font-size: 12.5px; font-weight: 600; color: #0f172a; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.task-right { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.task-status { font-size: 10px; font-weight: 600; padding: 2px 7px; border-radius: 999px; }
.st-run { background: #ecfdf5; color: #047857; border: 1px solid #a7f3d0; }
.st-done { background: #eef2ff; color: #4338ca; border: 1px solid #c7d2fe; }
.task-time { font-size: 10.5px; color: #94a3b8; font-family: ui-monospace, monospace; }
.task-fields {
  display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px;
  font-size: 11px; color: #64748b;
}
.task-fields b { color: #0f172a; font-weight: 600; }
.task-fields .mono { font-family: ui-monospace, monospace; }
.task-steps { display: flex; align-items: center; gap: 4px; }
.step { flex: 1; height: 4px; border-radius: 3px; background: #e2e8f0; }
.step.on { background: #10b981; }
.step-label { font-size: 10px; color: #64748b; font-family: ui-monospace, monospace; padding-left: 4px; white-space: nowrap; }

/* AI 事件 */
.event-list { display: flex; flex-direction: column; gap: 8px; }
.event { display: flex; gap: 9px; padding: 10px 11px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; }
.event-ico { width: 22px; height: 22px; flex: 0 0 22px; display: grid; place-items: center; border-radius: 6px; }
.event-ico.indigo { background: #eef2ff; color: #4f46e5; }
.event-ico.green { background: #ecfdf5; color: #059669; }
.event-ico.amber { background: #fffbeb; color: #d97706; }
.event-ico svg { width: 12px; height: 12px; stroke: currentColor; fill: none; stroke-width: 1.9; stroke-linecap: round; stroke-linejoin: round; }
.event-body { min-width: 0; flex: 1; }
.event-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 3px; }
.event-tag { font-size: 10px; font-weight: 700; letter-spacing: .02em; }
.event-tag.indigo { color: #4338ca; }
.event-tag.green { color: #047857; }
.event-tag.amber { color: #b45309; }
.event-time { font-size: 10px; color: #94a3b8; font-family: ui-monospace, monospace; }
.event-text { font-size: 11.5px; color: #334155; line-height: 1.6; margin: 0; }
.event-text :deep(b) { color: #0f172a; font-weight: 600; }

/* 高潜力 */
.lead-list { display: flex; flex-direction: column; gap: 9px; }
.lead-card {
  background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 9px; padding: 11px 13px;
  display: flex; flex-direction: column; gap: 8px; transition: all .15s;
}
.lead-card:hover { background: #f1f5f9; border-color: #cbd5e1; }
.lead-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }
.lead-main { min-width: 0; display: flex; flex-direction: column; gap: 3px; }
.lead-name-row { display: flex; align-items: center; gap: 6px; min-width: 0; }
.lead-name { font-size: 12.5px; font-weight: 600; color: #0f172a; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.lead-country {
  font-size: 9.5px; color: #475569; background: #f1f5f9; border: 1px solid #e2e8f0;
  border-radius: 3px; padding: 1px 5px; white-space: nowrap; flex-shrink: 0;
}
.lead-contact { font-size: 10.5px; color: #64748b; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.lead-score {
  font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 999px; flex-shrink: 0;
  background: #eef2ff; color: #4338ca; border: 1px solid #c7d2fe; font-variant-numeric: tabular-nums;
}
.lead-score.high { background: #ecfdf5; color: #047857; border-color: #a7f3d0; }
.lead-foot { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.lead-site {
  font-size: 10.5px; color: #4f46e5; font-family: ui-monospace, monospace;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.lead-site.muted { color: #94a3b8; }
.btn-mini {
  height: 26px; padding: 0 10px; border-radius: 6px; background: #4f46e5; border: 1px solid #4f46e5;
  color: #fff; font-size: 11px; font-weight: 600; cursor: pointer; white-space: nowrap;
}
.btn-mini:hover { background: #4338ca; }

.empty { text-align: center; padding: 18px 0; font-size: 12px; color: #94a3b8; }

@media (max-width: 1200px) {
  .metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .dash-grid { grid-template-columns: minmax(0, 1fr); }
}
@media (max-width: 700px) {
  .metrics { grid-template-columns: minmax(0, 1fr); }
  .task-fields { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
</style>
