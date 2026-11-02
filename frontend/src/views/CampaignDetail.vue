<template>
  <div v-if="campaign" class="detail">
    <!-- ===== 顶部 ===== -->
    <div class="top-bar">
      <button class="back-btn" @click="$router.push('/campaigns')">
        <svg viewBox="0 0 24 24"><path d="M19 12H5" /><path d="m11 6-6 6 6 6" /></svg>
        返回任务列表
      </button>
      <div class="head-row">
        <div class="head-left">
          <div class="kicker">
            <span class="k-badge">TASK PIPELINE</span>
            <span class="st" :class="taskState.cls"><i class="st-dot"></i>{{ taskState.label }}</span>
          </div>
          <h1 class="title">{{ campaign.name }}</h1>
          <div class="meta">
            <span class="meta-item"><b>产品</b>{{ campaign.product_name || '—' }}</span>
            <span class="sep-dot">·</span>
            <span class="meta-item">
              <b>官网</b>
              <a v-if="campaign.website" :href="campaign.website" target="_blank" class="site">{{ shortUrl(campaign.website) }}</a>
              <span v-else class="muted">未配置</span>
            </span>
            <span class="sep-dot">·</span>
            <span class="meta-item"><b>市场</b>{{ (campaign.target_market || []).join(' / ') || '未指定' }}</span>
          </div>
        </div>
        <div class="head-stats">
          <div class="hs">
            <span class="hs-v">{{ companies.length }}</span>
            <span class="hs-k">线索</span>
          </div>
          <div class="hs">
            <span class="hs-v">{{ contactsCount }}</span>
            <span class="hs-k">联系人</span>
          </div>
          <div class="hs">
            <span class="hs-v">{{ profiledCount }}</span>
            <span class="hs-k">已画像</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== 5 步流水线 ===== -->
    <section class="pipeline">
      <div class="pl-head">
        <div class="ph-title">
          <span class="bar"></span>
          <div>
            <h2>AI 五步获客流水线</h2>
            <p>按顺序执行，每步都会自动落库，可随时中断或重跑</p>
          </div>
        </div>
        <span class="pl-progress">{{ doneSteps }}/5 已完成</span>
      </div>

      <div class="steps">
        <div v-for="(s, i) in steps" :key="s.key" class="step" :class="{ done: s.done, active: s.active }">
          <div class="step-top">
            <div class="step-idx" :class="{ done: s.done, active: s.active }">
              <svg v-if="s.done" viewBox="0 0 24 24"><path d="m5 12 4 4 10-10" /></svg>
              <template v-else>{{ i + 1 }}</template>
            </div>
            <span class="step-name">{{ s.name }}</span>
          </div>
          <p class="step-desc">{{ s.desc }}</p>
          <button
            class="step-btn"
            :class="{ primary: s.active, done: s.done }"
            :disabled="s.loading"
            @click="s.run"
          >
            {{ s.loading ? '执行中...' : s.done ? '重新执行' : s.btn }}
          </button>
          <div v-if="i < steps.length - 1" class="step-line"></div>
        </div>
      </div>
    </section>

    <!-- ===== 企业 DNA ===== -->
    <section v-if="hasDna" class="panel">
      <div class="panel-head">
        <div class="ph-title">
          <span class="bar emerald"></span>
          <h2>企业 DNA（AI 官网分析结果）</h2>
        </div>
        <span class="chip-ok">
          <svg viewBox="0 0 24 24"><path d="m5 12 4 4 10-10" /></svg>已分析
        </span>
      </div>

      <div class="dna-grid">
        <div class="dna-item">
          <span class="dna-k">核心产品</span>
          <span class="dna-v">{{ campaign.dna.product_name || '—' }}</span>
        </div>
        <div class="dna-item">
          <span class="dna-k">产品品类</span>
          <span class="dna-v">{{ campaign.dna.product_category || '—' }}</span>
        </div>
        <div class="dna-item wide">
          <span class="dna-k">价值主张</span>
          <span class="dna-v">{{ campaign.dna.value_proposition || '—' }}</span>
        </div>
      </div>

      <div v-if="customerTypes.length" class="dna-block">
        <span class="dna-k">目标客户类型（搜索向量）</span>
        <div class="type-list">
          <div v-for="t in customerTypes" :key="t.name" class="type-card">
            <span class="type-name">{{ t.name }}</span>
            <div class="type-kws">
              <span v-for="k in t.keywords || []" :key="k" class="kw">{{ k }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="(campaign.dna.exclude_rules || []).length" class="dna-block">
        <span class="dna-k">同行排除规则</span>
        <div class="excl-list">
          <span v-for="r in campaign.dna.exclude_rules" :key="r" class="excl">{{ r }}</span>
        </div>
      </div>
    </section>

    <!-- ===== 线索表格 ===== -->
    <div class="table-card">
      <div class="tc-head">
        <div class="tch-left">
          <span class="tch-title">客户线索</span>
          <span class="tch-badge">{{ companies.length }} 条</span>
        </div>
        <span class="tch-right">按匹配分倒序</span>
      </div>

      <div class="table-scroll">
        <table>
          <thead>
            <tr>
              <th style="min-width: 220px">公司名称</th>
              <th style="min-width: 100px">身份</th>
              <th style="min-width: 110px">国家</th>
              <th style="min-width: 140px">行业</th>
              <th style="min-width: 140px">匹配分</th>
              <th style="min-width: 90px" class="ta-right">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in companies" :key="c.id">
              <td>
                <div class="co-cell">
                  <div class="co-logo">{{ (c.name || '?').slice(0, 1).toUpperCase() }}</div>
                  <span class="co-name" @click="$router.push('/companies/' + c.id)">{{ c.name }}</span>
                </div>
              </td>
              <td>
                <span class="ident" :class="identClass(c.identity)">
                  <i class="ident-dot"></i>{{ identLabel(c.identity) }}
                </span>
              </td>
              <td><span class="cell-txt">{{ c.country || '—' }}</span></td>
              <td><span class="cell-txt ellipsis">{{ c.industry || '—' }}</span></td>
              <td>
                <div class="score-cell">
                  <div class="ring">
                    <svg viewBox="0 0 36 36">
                      <circle cx="18" cy="18" r="15.9155" class="ring-bg" />
                      <circle
                        cx="18" cy="18" r="15.9155"
                        class="ring-fg"
                        :class="scoreClass(c.match_score)"
                        :stroke-dasharray="(c.match_score || 0) + ', 100'"
                      />
                    </svg>
                    <span class="ring-num">{{ Math.round(c.match_score || 0) }}</span>
                  </div>
                  <span class="score-lv" :class="scoreClass(c.match_score)">{{ scoreLabel(c.match_score) }}</span>
                </div>
              </td>
              <td class="ta-right">
                <button class="btn-mini" @click="$router.push('/companies/' + c.id)">详情</button>
              </td>
            </tr>
            <tr v-if="!companies.length">
              <td colspan="6" class="empty">暂无线索，先执行上面的「AI 分析官网」再「爬取线索」</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ===== 爬取弹窗 ===== -->
    <div v-if="crawlDialog" class="overlay" @click.self="crawlDialog = false">
      <div class="modal">
        <div class="modal-head">
          <div class="mh-left">
            <span class="bar"></span>
            <div>
              <h3>爬取潜在买家</h3>
              <p>按「目标客户类型」搜索，不搜产品名（避免找到同行）</p>
            </div>
          </div>
          <button class="icon-btn" @click="crawlDialog = false">
            <svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18" /></svg>
          </button>
        </div>

        <div class="modal-body">
          <div class="field">
            <label>数据源</label>
            <select v-model="crawlSource" class="inp">
              <option value="tavily">Tavily 搜索（推荐：AI 优化，能命中公司官网）</option>
              <option value="deepseek">DeepSeek Search（旧版：噪声大，多文章/招聘页）</option>
              <option value="europages">Europages 爬虫（有反爬，常失败）</option>
            </select>
          </div>
          <div class="field">
            <label>爬取数量（每类）</label>
            <input v-model.number="crawlCount" class="inp" type="number" min="1" max="20" />
          </div>
          <div class="tip">
            <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" /><path d="M12 8v5M12 16.5v.5" /></svg>
            按企业 DNA 的客户类型分别搜索，每类约 0.005 元
          </div>
        </div>

        <div class="modal-foot">
          <button class="btn-outline" @click="crawlDialog = false">取消</button>
          <button class="btn-primary" :disabled="crawling" @click="doCrawl">
            {{ crawling ? '爬取中...' : '开始爬取' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { campaignApi, contactApi } from '../api'

const route = useRoute()
const campaign = ref(null)
const companies = ref([])
const contactsAll = ref([])
const importing = ref(false)
const profiling = ref(false)
const extracting = ref(false)
const analyzing = ref(false)
const crawling = ref(false)
const crawlDialog = ref(false)
const crawlCount = ref(5)
const crawlSource = ref('tavily')

const hasDna = computed(() => campaign.value?.dna?.product_name)
const customerTypes = computed(() =>
  (campaign.value?.dna?.customer_types || []).map((t) =>
    typeof t === 'string' ? { name: t, keywords: [] } : t
  )
)
const profiledCount = computed(
  () => companies.value.filter((c) => c.profile && Object.keys(c.profile).length).length
)
const companyIds = computed(() => new Set(companies.value.map((c) => c.id)))
const contactsCount = computed(
  () => contactsAll.value.filter((c) => companyIds.value.has(c.company_id)).length
)
const doneSteps = computed(() => steps.value.filter((s) => s.done).length)

const taskState = computed(() => {
  const d = doneSteps.value
  if (d >= 4) return { label: '联系人就绪', cls: 'st-done' }
  if (d >= 1) return { label: '推进中', cls: 'st-run' }
  return { label: '待启动', cls: 'st-idle' }
})

const steps = computed(() => [
  {
    key: 'dna',
    name: 'AI 分析官网',
    desc: '抓取官网生成企业 DNA：产品、客户类型、排除规则',
    done: !!hasDna.value,
    active: !hasDna.value,
    btn: '开始分析',
    loading: analyzing.value,
    run: analyzeDna,
  },
  {
    key: 'crawl',
    name: '爬取线索',
    desc: '按客户类型批量搜索目标企业并判定身份',
    done: companies.value.length > 0,
    active: hasDna.value && companies.value.length === 0,
    btn: '爬取线索',
    loading: crawling.value,
    run: () => (crawlDialog.value = true),
  },
  {
    key: 'profile',
    name: 'AI 画像评分',
    desc: '逐家分析业务、需求信号与匹配分',
    done: profiledCount.value > 0,
    active: companies.value.length > 0 && profiledCount.value === 0,
    btn: '开始画像',
    loading: profiling.value,
    run: profileAll,
  },
  {
    key: 'contacts',
    name: '提取联系人',
    desc: '从官网与搜索引擎抓取决策人邮箱',
    done: contactsCount.value > 0,
    active: profiledCount.value > 0 && contactsCount.value === 0,
    btn: '提取联系人',
    loading: extracting.value,
    run: extractContacts,
  },
  {
    key: 'email',
    name: '生成开发信',
    desc: '为联系人批量生成个性化开发信草稿',
    done: false,
    active: contactsCount.value > 0,
    btn: '去邮件中心',
    loading: false,
    run: () => (window.location.hash = '#/leads'),
  },
])

function shortUrl(u) {
  return (u || '').replace(/^https?:\/\//, '').replace(/\/$/, '')
}
function identLabel(v) {
  return { buyer: '买家', competitor: '同行', irrelevant: '无关', unknown: '不明' }[v] || '不明'
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
  if (n >= 90) return '极强'
  if (n >= 70) return '较强'
  if (n >= 40) return '一般'
  if (n > 0) return '弱'
  return '未评分'
}

onMounted(load)

async function load() {
  const [cr, ct, camps] = await Promise.all([
    campaignApi.companies(route.params.id),
    contactApi.list(),
    campaignApi.list(),
  ])
  companies.value = cr.data
  contactsAll.value = ct.data
  campaign.value = camps.data.find((c) => c.id === Number(route.params.id))
}

async function analyzeDna() {
  analyzing.value = true
  try {
    const r = await campaignApi.analyzeDna(route.params.id)
    campaign.value.dna = r.data
    ElMessage.success('企业 DNA 分析完成')
    await load()
  } catch (e) {
    ElMessage.error('分析失败：' + (e.response?.data?.detail || e.message))
  } finally {
    analyzing.value = false
  }
}

async function doCrawl() {
  crawling.value = true
  try {
    const r = await campaignApi.crawl(route.params.id, '', crawlCount.value, crawlSource.value)
    crawlDialog.value = false
    ElMessage.success(`爬取完成，新增 ${r.data.length} 家企业`)
    await load()
  } catch (e) {
    ElMessage.error('爬取失败：' + (e.response?.data?.detail || e.message))
  } finally {
    crawling.value = false
  }
}

async function extractContacts() {
  extracting.value = true
  try {
    const r = await campaignApi.extractContacts(route.params.id)
    ElMessage.success(`提取完成：新增 ${r.data.created} 位联系人`)
    await load()
  } catch (e) {
    ElMessage.error('提取失败：' + (e.response?.data?.detail || e.message))
  } finally {
    extracting.value = false
  }
}

async function profileAll() {
  profiling.value = true
  try {
    await campaignApi.profile(route.params.id)
    ElMessage.success('画像完成')
    await load()
  } catch (e) {
    ElMessage.error('画像失败：' + (e.response?.data?.detail || e.message))
  } finally {
    profiling.value = false
  }
}

// 避免未使用告警
void importing
</script>

<style scoped>
.detail { display: flex; flex-direction: column; gap: 16px; }

/* 顶部 */
.top-bar { display: flex; flex-direction: column; gap: 12px; }
.back-btn {
  align-self: flex-start; display: inline-flex; align-items: center; gap: 5px;
  height: 30px; padding: 0 11px; background: #eef2ff; border: 1px solid #e0e7ff;
  border-radius: 7px; color: #4338ca; font-size: 12px; font-weight: 600; cursor: pointer;
}
.back-btn:hover { background: #e0e7ff; }
.back-btn svg { width: 13px; height: 13px; stroke: currentColor; fill: none; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }

.head-row { display: flex; align-items: flex-start; justify-content: space-between; gap: 24px; flex-wrap: wrap; }
.head-left { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.kicker { display: flex; align-items: center; gap: 9px; }
.k-badge {
  font-size: 10px; font-weight: 700; letter-spacing: .06em; color: #4f46e5;
  background: #eef2ff; border: 1px solid #e0e7ff; padding: 2px 8px; border-radius: 999px;
}
.title { font-size: 22px; font-weight: 700; color: #0f172a; margin: 0; letter-spacing: -.025em; }
.meta { display: flex; align-items: center; gap: 7px; flex-wrap: wrap; font-size: 12px; color: #64748b; }
.meta-item b { font-weight: 600; color: #94a3b8; margin-right: 4px; font-size: 11px; }
.sep-dot { color: #cbd5e1; }
.site { color: #4f46e5; font-family: ui-monospace, monospace; font-size: 11.5px; }
.site:hover { text-decoration: underline; }
.muted { color: #cbd5e1; }

.head-stats { display: flex; gap: 10px; flex-shrink: 0; }
.hs {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 16px;
  display: flex; flex-direction: column; align-items: center; gap: 1px; min-width: 76px;
}
.hs-v { font-size: 20px; font-weight: 800; color: #0f172a; font-variant-numeric: tabular-nums; letter-spacing: -.02em; }
.hs-k { font-size: 10px; color: #94a3b8; font-weight: 600; }

/* 流水线 */
.pipeline { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 20px; box-shadow: 0 1px 3px rgba(15,23,42,.04); display: flex; flex-direction: column; gap: 14px; }
.pl-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; padding-bottom: 12px; border-bottom: 1px solid #f1f5f9; }
.ph-title { display: flex; align-items: flex-start; gap: 9px; }
.bar { width: 3px; height: 17px; border-radius: 2px; background: #4f46e5; flex: 0 0 3px; margin-top: 2px; }
.bar.emerald { background: #10b981; }
.ph-title h2 { font-size: 14px; font-weight: 700; color: #0f172a; margin: 0; }
.ph-title p { font-size: 11px; color: #94a3b8; margin: 2px 0 0; }
.pl-progress { font-size: 11px; font-weight: 700; color: #4f46e5; background: #eef2ff; border: 1px solid #e0e7ff; padding: 2px 9px; border-radius: 999px; white-space: nowrap; }

.steps { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; }
.step {
  position: relative; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 9px;
  padding: 12px; display: flex; flex-direction: column; gap: 6px;
}
.step.done { background: #f0fdf4; border-color: #d1fae5; }
.step.active { background: #eef2ff; border-color: #c7d2fe; }
.step-top { display: flex; align-items: center; gap: 6px; }
.step-idx {
  width: 20px; height: 20px; flex: 0 0 20px; border-radius: 999px; display: grid; place-items: center;
  background: #e2e8f0; color: #64748b; font-size: 10px; font-weight: 700;
}
.step-idx.done { background: #10b981; color: #fff; }
.step-idx.active { background: #4f46e5; color: #fff; }
.step-idx svg { width: 11px; height: 11px; stroke: currentColor; fill: none; stroke-width: 2.6; stroke-linecap: round; stroke-linejoin: round; }
.step-name { font-size: 11.5px; font-weight: 700; color: #0f172a; }
.step-desc { font-size: 10px; color: #94a3b8; line-height: 1.5; flex: 1; margin: 0; }
.step-btn {
  height: 26px; border-radius: 6px; border: 1px solid #e2e8f0; background: #fff;
  color: #475569; font-size: 10.5px; font-weight: 600; cursor: pointer; white-space: nowrap;
}
.step-btn:hover:not(:disabled) { background: #f1f5f9; }
.step-btn.primary { background: #4f46e5; border-color: #4f46e5; color: #fff; }
.step-btn.primary:hover:not(:disabled) { background: #4338ca; }
.step-btn.done { background: #fff; border-color: #d1fae5; color: #047857; }
.step-btn:disabled { opacity: .55; cursor: not-allowed; }
.step-line { display: none; }

/* DNA */
.panel { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 20px; box-shadow: 0 1px 3px rgba(15,23,42,.04); display: flex; flex-direction: column; gap: 13px; }
.panel-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding-bottom: 12px; border-bottom: 1px solid #f1f5f9; }
.chip-ok {
  display: inline-flex; align-items: center; gap: 4px; font-size: 10px; font-weight: 700;
  color: #047857; background: #ecfdf5; border: 1px solid #d1fae5; padding: 2px 8px; border-radius: 999px;
}
.chip-ok svg { width: 11px; height: 11px; stroke: currentColor; fill: none; stroke-width: 2.6; stroke-linecap: round; stroke-linejoin: round; }

.dna-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
.dna-item { background: #f8fafc; border: 1px solid #f1f5f9; border-radius: 8px; padding: 10px 12px; display: flex; flex-direction: column; gap: 3px; }
.dna-item.wide { grid-column: span 3; }
.dna-k { font-size: 10px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: .05em; }
.dna-v { font-size: 12px; color: #0f172a; font-weight: 600; line-height: 1.6; }
.dna-block { display: flex; flex-direction: column; gap: 7px; }
.type-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 9px; }
.type-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 12px; display: flex; flex-direction: column; gap: 6px; }
.type-name { font-size: 12px; font-weight: 700; color: #0f172a; }
.type-kws { display: flex; flex-wrap: wrap; gap: 4px; }
.kw { font-size: 9.5px; padding: 1px 6px; background: #eef2ff; color: #4338ca; border: 1px solid #e0e7ff; border-radius: 4px; font-family: ui-monospace, monospace; }
.excl-list { display: flex; flex-wrap: wrap; gap: 5px; }
.excl { font-size: 10.5px; padding: 2px 8px; background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; border-radius: 999px; }

/* 表格 */
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
tbody td { padding: 10px 14px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
tbody tr:last-child td { border-bottom: 0; }
tbody tr:hover { background: #f8fafc; }
.ta-right { text-align: right; }

.co-cell { display: flex; align-items: center; gap: 9px; }
.co-logo {
  width: 28px; height: 28px; flex: 0 0 28px; border-radius: 8px; display: grid; place-items: center;
  background: #eef2ff; border: 1px solid #e0e7ff; color: #4f46e5; font-size: 11px; font-weight: 700;
}
.co-name { font-size: 12px; font-weight: 600; color: #0f172a; cursor: pointer; }
.co-name:hover { color: #4f46e5; }
.cell-txt { font-size: 11.5px; color: #475569; }
.ellipsis { display: inline-block; max-width: 130px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.ident { display: inline-flex; align-items: center; gap: 4px; padding: 2px 7px; border-radius: 999px; font-size: 10px; font-weight: 600; }
.ident-dot { width: 4px; height: 4px; border-radius: 50%; background: currentColor; }
.id-buyer { background: #ecfdf5; color: #047857; border: 1px solid #d1fae5; }
.id-comp { background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }
.id-irr { background: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; }
.id-unk { background: #fffbeb; color: #b45309; border: 1px solid #fef3c7; }

.score-cell { display: flex; align-items: center; gap: 7px; }
.ring { position: relative; width: 28px; height: 28px; flex: 0 0 28px; }
.ring svg { width: 28px; height: 28px; transform: rotate(-90deg); }
.ring-bg { fill: none; stroke: #f1f5f9; stroke-width: 3.5; }
.ring-fg { fill: none; stroke-width: 3.5; stroke-linecap: round; }
.ring-fg.sc-high { stroke: #10b981; }
.ring-fg.sc-mid { stroke: #4f46e5; }
.ring-fg.sc-low { stroke: #94a3b8; }
.ring-fg.sc-none { stroke: #cbd5e1; }
.ring-num { position: absolute; inset: 0; display: grid; place-items: center; font-size: 9px; font-weight: 700; color: #334155; font-variant-numeric: tabular-nums; }
.score-lv { font-size: 10px; font-weight: 600; }
.score-lv.sc-high { color: #047857; }
.score-lv.sc-mid { color: #4f46e5; }
.score-lv.sc-low, .score-lv.sc-none { color: #94a3b8; }

.btn-mini { height: 25px; padding: 0 9px; border-radius: 5px; background: #4f46e5; border: 1px solid #4f46e5; color: #fff; font-size: 10.5px; font-weight: 600; cursor: pointer; }
.btn-mini:hover { background: #4338ca; }
.empty { text-align: center; padding: 28px 0; color: #94a3b8; font-size: 12px; }

/* 弹窗 */
.overlay { position: fixed; inset: 0; background: rgba(15,23,42,.45); display: grid; place-items: center; z-index: 100; padding: 20px; }
.modal { background: #fff; border-radius: 14px; width: 480px; max-width: 100%; box-shadow: 0 20px 40px rgba(15,23,42,.2); }
.modal-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; padding: 18px 20px 14px; border-bottom: 1px solid #f1f5f9; }
.mh-left { display: flex; align-items: flex-start; gap: 9px; }
.modal-head h3 { font-size: 14px; font-weight: 700; color: #0f172a; margin: 0; }
.modal-head p { font-size: 11px; color: #94a3b8; margin: 2px 0 0; }
.icon-btn { width: 26px; height: 26px; border: 0; background: transparent; color: #94a3b8; cursor: pointer; border-radius: 6px; display: grid; place-items: center; }
.icon-btn:hover { background: #f1f5f9; }
.icon-btn svg { width: 14px; height: 14px; stroke: currentColor; fill: none; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
.modal-body { padding: 16px 20px; display: flex; flex-direction: column; gap: 13px; }
.field { display: flex; flex-direction: column; gap: 5px; }
.field label { font-size: 11px; font-weight: 600; color: #334155; }
.inp { height: 36px; padding: 0 11px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 7px; font-size: 12px; color: #0f172a; outline: none; }
.inp:focus { background: #fff; border-color: #4f46e5; box-shadow: 0 0 0 3px rgba(79,70,229,.1); }
.tip { display: flex; align-items: flex-start; gap: 6px; font-size: 10.5px; color: #94a3b8; line-height: 1.6; }
.tip svg { width: 13px; height: 13px; stroke: currentColor; fill: none; stroke-width: 1.9; flex: 0 0 13px; margin-top: 1px; }
.modal-foot { display: flex; justify-content: flex-end; gap: 8px; padding: 13px 20px; border-top: 1px solid #f1f5f9; }

.btn-primary, .btn-outline {
  display: inline-flex; align-items: center; gap: 6px; height: 32px; padding: 0 13px;
  border-radius: 7px; font-size: 12px; font-weight: 600; cursor: pointer; white-space: nowrap;
}
.btn-primary { background: #4f46e5; border: 1px solid #4f46e5; color: #fff; }
.btn-primary:hover:not(:disabled) { background: #4338ca; }
.btn-primary:disabled { background: #a5b4fc; cursor: not-allowed; }
.btn-outline { background: #fff; border: 1px solid #e2e8f0; color: #334155; }
.btn-outline:hover { background: #f8fafc; }

.st { display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 999px; font-size: 10px; font-weight: 600; }
.st-dot { width: 4px; height: 4px; border-radius: 50%; background: currentColor; }
.st-run { background: #ecfdf5; color: #047857; border: 1px solid #d1fae5; }
.st-done { background: #eef2ff; color: #4338ca; border: 1px solid #e0e7ff; }
.st-idle { background: #f8fafc; color: #94a3b8; border: 1px solid #e2e8f0; }

@media (max-width: 1200px) {
  .steps { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .dna-grid { grid-template-columns: 1fr 1fr; }
  .dna-item.wide { grid-column: span 2; }
}
@media (max-width: 700px) {
  .steps { grid-template-columns: minmax(0, 1fr); }
}
</style>
