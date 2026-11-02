<template>
  <div class="pool">
    <!-- ===== 页头 ===== -->
    <div class="pool-head">
      <div class="ph-left">
        <div class="kicker">
          <span>CRM DATABASE</span>
          <span class="k-sep">•</span>
          <span class="k-badge">{{ companies.length }} ENTERPRISES IDENTIFIED</span>
        </div>
        <h1 class="pool-title">全球高意向客户池 <span>(Customer Pool)</span></h1>
        <p class="pool-sub">汇聚全网已清洗的 B2B 目标客户，多维筛选与批量触达枢纽。</p>
      </div>
      <div class="ph-actions">
        <button class="btn-outline" @click="$router.push('/emails')">
          <svg viewBox="0 0 24 24"><rect x="3" y="5.4" width="18" height="13.2" rx="2.2" /><path d="m4.2 7.2 7.8 5.6 7.8-5.6" /></svg>
          前往邮件中心
        </button>
      </div>
    </div>

    <!-- ===== 4 指标卡 ===== -->
    <div class="stat-row">
      <div class="stat-card">
        <div class="sc-left">
          <span class="sc-label">入库客户总额</span>
          <span class="sc-num">{{ companies.length }}</span>
          <span class="sc-foot green">覆盖 {{ countryCount }} 个国家</span>
        </div>
        <div class="sc-ico indigo">
          <svg viewBox="0 0 24 24"><rect x="4" y="3.5" width="16" height="17" rx="2" /><path d="M8 9h8M8 13h8M8 17h5" /></svg>
        </div>
      </div>

      <div class="stat-card">
        <div class="sc-left">
          <span class="sc-label">极高意向买家 (≥90分)</span>
          <span class="sc-num">{{ highIntent }}</span>
          <span class="sc-foot muted"><span class="pill">{{ pct(highIntent) }}%</span> · 核心转化标的</span>
        </div>
        <div class="sc-ico emerald">
          <svg viewBox="0 0 24 24"><path d="m12 3 7 3v5.5c0 4.2-2.9 7.6-7 8.5-4.1-.9-7-4.3-7-8.5V6z" /><path d="m9 12 2 2 4-4" /></svg>
        </div>
      </div>

      <div class="stat-card">
        <div class="sc-left">
          <span class="sc-label">已提取联系人</span>
          <span class="sc-num">{{ contacts.length }}</span>
          <span class="sc-foot indigo">
            <svg viewBox="0 0 24 24" class="mini-ico"><path d="m5 12 4 4 10-10" /></svg>
            覆盖 {{ withContact }} 家公司
          </span>
        </div>
        <div class="sc-ico sky">
          <svg viewBox="0 0 24 24"><rect x="3" y="6" width="18" height="12" rx="2" /><path d="m4 8 8 5 8-5" /></svg>
        </div>
      </div>

      <div class="stat-card">
        <div class="sc-left">
          <span class="sc-label">客户已回复</span>
          <span class="sc-num">{{ repliedCount }}</span>
          <span class="sc-foot amber"><span class="dot-amber"></span>需人工跟进</span>
        </div>
        <div class="sc-ico amber">
          <svg viewBox="0 0 24 24"><path d="M20 14.5a2.5 2.5 0 0 1-2.5 2.5H8l-4 3V6.5A2.5 2.5 0 0 1 6.5 4h11A2.5 2.5 0 0 1 20 6.5z" /></svg>
        </div>
      </div>
    </div>

    <!-- ===== 筛选 ===== -->
    <div class="filter-card">
      <div class="filter-row">
        <div class="search-wrap">
          <svg viewBox="0 0 24 24" class="search-ico"><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></svg>
          <input v-model="kw" class="search-input" placeholder="多维搜索：公司名、官网域名、行业关键词..." />
        </div>

        <select v-model="country" class="sel">
          <option value="">国家/地区: 全部 ({{ countryCount }})</option>
          <option v-for="c in countryOptions" :key="c" :value="c">{{ c }}</option>
        </select>

        <select v-model="identity" class="sel">
          <option value="">身份标签: 全部</option>
          <option value="buyer">买家 Buyer</option>
          <option value="competitor">同行 Competitor</option>
          <option value="unknown">待判定 Unknown</option>
          <option value="irrelevant">无关 Irrelevant</option>
        </select>

        <select v-model.number="minScore" class="sel">
          <option :value="0">AI 评分: 全部</option>
          <option :value="60">AI 评分: ≥ 60</option>
          <option :value="80">AI 评分: ≥ 80 高意向</option>
          <option :value="90">AI 评分: ≥ 90 极高意向</option>
        </select>

        <button class="btn-reset" @click="reset">
          <svg viewBox="0 0 24 24"><path d="M3 12a9 9 0 1 0 3-6.7" /><path d="M3 4v5h5" /></svg>
          重置
        </button>
      </div>
    </div>

    <!-- ===== 表格 ===== -->
    <div class="table-card">
      <div class="tc-head">
        <div class="tch-left">
          <span class="tch-title">客户总表清单</span>
          <span class="tch-badge">{{ filtered.length }} 条结果</span>
        </div>
        <span class="tch-right">共 {{ companies.length }} 家 · 筛选后 {{ filtered.length }}</span>
      </div>

      <div class="table-scroll">
        <table>
          <thead>
            <tr>
              <th style="min-width: 230px">公司主体 &amp; 官网</th>
              <th style="min-width: 130px">国家 / 地区</th>
              <th style="min-width: 160px">细分行业</th>
              <th style="min-width: 110px">身份标签</th>
              <th style="min-width: 140px">AI 匹配度</th>
              <th style="min-width: 150px">联系人</th>
              <th style="min-width: 170px" class="ta-right">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in filtered" :key="c.id">
              <td>
                <div class="co-cell">
                  <div class="co-logo">{{ (c.name || '?').slice(0, 1).toUpperCase() }}</div>
                  <div class="co-info">
                    <span class="co-name" @click="$router.push('/companies/' + c.id)">{{ c.name }}</span>
                    <a v-if="c.website" :href="c.website" target="_blank" class="co-site">{{ shortUrl(c.website) }}</a>
                    <span v-else class="co-site muted">无官网</span>
                  </div>
                </div>
              </td>
              <td>
                <div class="country-cell">
                  <span class="flag">{{ flagOf(c.country) }}</span>
                  <span>{{ c.country || '未标注' }}</span>
                </div>
              </td>
              <td>
                <span class="ind-tag">{{ c.industry || '—' }}</span>
                <div class="ind-desc">{{ (c.description || '').slice(0, 28) || '—' }}</div>
              </td>
              <td>
                <span class="ident" :class="identClass(c.identity)">
                  <span class="ident-dot"></span>{{ identLabel(c.identity) }}
                </span>
              </td>
              <td>
                <div class="score-cell">
                  <div class="ring">
                    <svg viewBox="0 0 36 36">
                      <circle class="ring-bg" cx="18" cy="18" r="15.9155" />
                      <circle
                        class="ring-fg"
                        cx="18"
                        cy="18"
                        r="15.9155"
                        :stroke-dasharray="(c.match_score || 0) + ', 100'"
                        :class="scoreClass(c.match_score)"
                      />
                    </svg>
                    <span class="ring-num">{{ Math.round(c.match_score || 0) }}</span>
                  </div>
                  <div class="score-txt">
                    <span class="score-level" :class="scoreClass(c.match_score)">{{ scoreLabel(c.match_score) }}</span>
                    <span class="score-sub">{{ scoreHint(c.match_score) }}</span>
                  </div>
                </div>
              </td>
              <td>
                <div class="contact-cell">
                  <span v-if="contactOf(c.id).length" class="ct-title">{{ contactOf(c.id)[0].title || '联系人' }}</span>
                  <span v-else class="ct-none">暂无</span>
                  <span class="ct-count">共 {{ contactOf(c.id).length }} 位</span>
                </div>
              </td>
              <td class="ta-right">
                <div class="row-actions">
                  <button class="ico-btn" title="查看公司档案" @click="$router.push('/companies/' + c.id)">
                    <svg viewBox="0 0 24 24"><rect x="4" y="3.5" width="16" height="17" rx="2" /><circle cx="12" cy="10" r="2.6" /><path d="M8 17c.8-1.8 2.3-2.6 4-2.6s3.2.8 4 2.6" /></svg>
                  </button>
                  <button class="btn-mini" :disabled="!contactOf(c.id).length" @click="generate(c)">
                    生成开发信
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="!filtered.length">
              <td colspan="7" class="empty">没有符合筛选条件的客户</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { companyApi, contactApi, emailApi } from '../api'

const companies = ref([])
const contacts = ref([])
const kw = ref('')
const country = ref('')
const identity = ref('')
const minScore = ref(0)

const countryCount = computed(
  () => new Set(companies.value.map((c) => c.country).filter(Boolean)).size
)
const countryOptions = computed(() =>
  [...new Set(companies.value.map((c) => c.country).filter(Boolean))].sort()
)
const highIntent = computed(
  () => companies.value.filter((c) => (c.match_score || 0) >= 90).length
)
const withContact = computed(
  () => new Set(contacts.value.map((c) => c.company_id)).size
)
const repliedCount = computed(
  () => contacts.value.filter((c) => c.status === 'replied').length
)

const filtered = computed(() => {
  const k = kw.value.trim().toLowerCase()
  return companies.value.filter((c) => {
    if (k) {
      const hay = [c.name, c.website, c.industry, c.description, c.country]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()
      if (!hay.includes(k)) return false
    }
    if (country.value && c.country !== country.value) return false
    if (identity.value && c.identity !== identity.value) return false
    if (minScore.value && (c.match_score || 0) < minScore.value) return false
    return true
  })
})

function pct(n) {
  return companies.value.length ? Math.round((n / companies.value.length) * 100) : 0
}
function shortUrl(u) {
  return (u || '').replace(/^https?:\/\//, '').replace(/\/$/, '')
}
const FLAGS = {
  'United States': '🇺🇸', USA: '🇺🇸', Germany: '🇩🇪', 'United Kingdom': '🇬🇧', UK: '🇬🇧',
  Japan: '🇯🇵', Australia: '🇦🇺', France: '🇫🇷', Italy: '🇮🇹', Spain: '🇪🇸',
  Netherlands: '🇳🇱', Poland: '🇵🇱', China: '🇨🇳', India: '🇮🇳', Canada: '🇨🇦',
  Brazil: '🇧🇷', Mexico: '🇲🇽', Turkey: '🇹🇷', 'South Korea': '🇰🇷', Sweden: '🇸🇪',
  Norway: '🇳🇴', Denmark: '🇩🇰', Switzerland: '🇨🇭', Austria: '🇦🇹', Belgium: '🇧🇪',
  'Czech Republic': '🇨🇿', Vietnam: '🇻🇳', Thailand: '🇹🇭', Indonesia: '🇮🇩',
  Malaysia: '🇲🇾', Singapore: '🇸🇬',
}
function flagOf(name) {
  return FLAGS[name] || '🌐'
}
function identLabel(v) {
  return { buyer: '买家 Buyer', competitor: '同行 Competitor', irrelevant: '无关', unknown: '待判定' }[v] || '待判定'
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
  if (n >= 90) return '极强匹配'
  if (n >= 70) return '较强匹配'
  if (n >= 40) return '一般匹配'
  if (n > 0) return '弱匹配'
  return '未评分'
}
function scoreHint(s) {
  const n = s || 0
  if (n >= 90) return '优先触达'
  if (n >= 70) return '建议触达'
  if (n >= 40) return '可观察'
  return '待评估'
}
function contactOf(companyId) {
  return contacts.value.filter((c) => c.company_id === companyId)
}
function reset() {
  kw.value = ''
  country.value = ''
  identity.value = ''
  minScore.value = 0
}
async function generate(c) {
  const cs = contactOf(c.id)
  if (!cs.length) return
  try {
    await emailApi.generate(c.id, cs[0].id)
    ElMessage.success('已生成开发信草稿')
  } catch (e) {
    ElMessage.error('生成失败：' + (e.response?.data?.detail || e.message))
  }
}

onMounted(async () => {
  const [co, ct] = await Promise.all([companyApi.list(), contactApi.list()])
  companies.value = co.data
  contacts.value = ct.data
})
</script>

<style scoped>
.pool { display: flex; flex-direction: column; gap: 18px; }

.pool-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; flex-wrap: wrap; }
.ph-left { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.kicker {
  display: flex; align-items: center; gap: 7px; font-size: 10.5px; font-weight: 700;
  letter-spacing: .08em; text-transform: uppercase; color: #94a3b8;
}
.k-sep { color: #cbd5e1; }
.k-badge {
  color: #047857; background: #ecfdf5; border: 1px solid #d1fae5;
  padding: 2px 8px; border-radius: 999px; letter-spacing: .04em;
}
.pool-title { font-size: 23px; font-weight: 700; color: #0f172a; margin: 0; letter-spacing: -.025em; }
.pool-title span { font-size: 15px; font-weight: 500; color: #64748b; }
.pool-sub { font-size: 13px; color: #64748b; margin: 0; max-width: 620px; }
.ph-actions { display: flex; gap: 8px; flex: 0 0 auto; }
.btn-outline {
  display: inline-flex; align-items: center; gap: 6px; height: 34px; padding: 0 14px;
  background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; color: #334155;
  font-size: 12.5px; font-weight: 600; cursor: pointer; box-shadow: 0 1px 2px rgba(15,23,42,.03);
}
.btn-outline:hover { background: #f8fafc; border-color: #cbd5e1; }
.btn-outline svg { width: 14px; height: 14px; stroke: currentColor; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }

.stat-row { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
.stat-card {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px 18px;
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,.02);
}
.sc-left { display: flex; flex-direction: column; gap: 3px; min-width: 0; }
.sc-label { font-size: 11.5px; color: #64748b; font-weight: 500; }
.sc-num {
  font-size: 24px; font-weight: 700; color: #0f172a; letter-spacing: -.02em;
  font-variant-numeric: tabular-nums; line-height: 1.2;
}
.sc-foot { font-size: 11px; display: inline-flex; align-items: center; gap: 4px; }
.sc-foot.green { color: #059669; font-weight: 600; }
.sc-foot.indigo { color: #4f46e5; font-weight: 600; }
.sc-foot.amber { color: #b45309; }
.sc-foot.muted { color: #94a3b8; }
.mini-ico { width: 12px; height: 12px; stroke: currentColor; fill: none; stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round; }
.pill { background: #f1f5f9; color: #475569; padding: 1px 5px; border-radius: 4px; font-size: 10px; font-weight: 600; }
.dot-amber { width: 5px; height: 5px; border-radius: 50%; background: #f59e0b; }
.sc-ico { width: 42px; height: 42px; flex: 0 0 42px; border-radius: 11px; display: grid; place-items: center; }
.sc-ico svg { width: 20px; height: 20px; stroke: currentColor; fill: none; stroke-width: 1.7; stroke-linecap: round; stroke-linejoin: round; }
.sc-ico.indigo { background: #eef2ff; color: #4f46e5; border: 1px solid #e0e7ff; }
.sc-ico.emerald { background: #ecfdf5; color: #059669; border: 1px solid #d1fae5; }
.sc-ico.sky { background: #f0f9ff; color: #0284c7; border: 1px solid #e0f2fe; }
.sc-ico.amber { background: #fffbeb; color: #d97706; border: 1px solid #fef3c7; }

.filter-card {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,.02);
}
.filter-row { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
.search-wrap { position: relative; flex: 1; min-width: 260px; }
.search-ico {
  position: absolute; left: 11px; top: 50%; transform: translateY(-50%);
  width: 15px; height: 15px; stroke: #94a3b8; fill: none; stroke-width: 1.9;
  stroke-linecap: round; stroke-linejoin: round;
}
.search-input {
  width: 100%; height: 34px; padding: 0 12px 0 33px; background: #f8fafc;
  border: 1px solid #e2e8f0; border-radius: 8px; font-size: 12.5px; color: #0f172a;
  outline: none; transition: all .15s;
}
.search-input::placeholder { color: #94a3b8; }
.search-input:focus { background: #fff; border-color: #4f46e5; box-shadow: 0 0 0 3px rgba(79,70,229,.12); }
.sel {
  height: 34px; padding: 0 10px; background: #f8fafc; border: 1px solid #e2e8f0;
  border-radius: 8px; font-size: 12.5px; color: #334155; font-weight: 500; cursor: pointer;
  outline: none; max-width: 190px;
}
.sel:focus { border-color: #4f46e5; background: #fff; }
.btn-reset {
  display: inline-flex; align-items: center; gap: 5px; height: 34px; padding: 0 12px;
  background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; color: #64748b;
  font-size: 12.5px; font-weight: 500; cursor: pointer;
}
.btn-reset:hover { background: #f8fafc; color: #0f172a; }
.btn-reset svg { width: 13px; height: 13px; stroke: currentColor; fill: none; stroke-width: 1.9; stroke-linecap: round; stroke-linejoin: round; }

.table-card {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,.02); overflow: hidden;
}
.tc-head {
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  padding: 13px 18px; background: #f8fafc; border-bottom: 1px solid #e2e8f0;
}
.tch-left { display: flex; align-items: center; gap: 8px; }
.tch-title { font-size: 13px; font-weight: 700; color: #0f172a; }
.tch-badge {
  font-size: 10.5px; font-weight: 600; color: #4f46e5; background: #eef2ff;
  border: 1px solid #e0e7ff; padding: 1px 7px; border-radius: 999px;
}
.tch-right { font-size: 11.5px; color: #94a3b8; }
.table-scroll { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
thead th {
  background: #f8fafc; color: #94a3b8; font-size: 10.5px; font-weight: 700;
  text-transform: uppercase; letter-spacing: .05em; text-align: left;
  padding: 9px 14px; border-bottom: 1px solid #e2e8f0; white-space: nowrap;
}
tbody td { padding: 11px 14px; border-bottom: 1px solid #f1f5f9; color: #334155; vertical-align: middle; }
tbody tr:last-child td { border-bottom: 0; }
tbody tr:hover { background: #f8fafc; }
.ta-right { text-align: right; }

.co-cell { display: flex; align-items: center; gap: 10px; }
.co-logo {
  width: 34px; height: 34px; flex: 0 0 34px; border-radius: 9px; display: grid; place-items: center;
  background: #eef2ff; border: 1px solid #e0e7ff; color: #4f46e5; font-weight: 700; font-size: 13px;
}
.co-info { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.co-name {
  font-size: 12.5px; font-weight: 600; color: #0f172a; cursor: pointer;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 210px;
}
.co-name:hover { color: #4f46e5; }
.co-site {
  font-size: 10.5px; color: #94a3b8; font-family: ui-monospace, monospace;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 200px;
}
.co-site:hover { color: #4f46e5; }
.co-site.muted { color: #cbd5e1; }

.country-cell { display: flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 500; color: #334155; }
.flag { font-size: 14px; line-height: 1; }

.ind-tag {
  display: inline-block; padding: 1px 6px; border-radius: 4px; background: #f1f5f9;
  color: #475569; font-size: 10.5px; font-weight: 500; max-width: 150px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.ind-desc { font-size: 10.5px; color: #94a3b8; margin-top: 3px; max-width: 160px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.ident {
  display: inline-flex; align-items: center; gap: 5px; padding: 2px 8px; border-radius: 999px;
  font-size: 10.5px; font-weight: 600; white-space: nowrap;
}
.ident-dot { width: 5px; height: 5px; border-radius: 50%; background: currentColor; }
.id-buyer { background: #ecfdf5; color: #047857; border: 1px solid #d1fae5; }
.id-comp { background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }
.id-irr { background: #f8fafc; color: #64748b; border: 1px solid #e2e8f0; }
.id-unk { background: #fffbeb; color: #b45309; border: 1px solid #fef3c7; }

.score-cell { display: flex; align-items: center; gap: 8px; }
.ring { position: relative; width: 32px; height: 32px; flex: 0 0 32px; }
.ring svg { width: 32px; height: 32px; transform: rotate(-90deg); }
.ring-bg { fill: none; stroke: #f1f5f9; stroke-width: 3.5; }
.ring-fg { fill: none; stroke-width: 3.5; stroke-linecap: round; transition: stroke-dasharray .6s ease; }
.sc-high { stroke: #4f46e5; }
.sc-mid { stroke: #6366f1; }
.sc-low { stroke: #94a3b8; }
.sc-none { stroke: #cbd5e1; }
.ring-num {
  position: absolute; inset: 0; display: grid; place-items: center;
  font-size: 10px; font-weight: 700; color: #334155; font-variant-numeric: tabular-nums;
}
.score-txt { display: flex; flex-direction: column; gap: 1px; }
.score-level { font-size: 10.5px; font-weight: 600; }
.score-level.sc-high { color: #4f46e5; }
.score-level.sc-mid { color: #6366f1; }
.score-level.sc-low { color: #64748b; }
.score-level.sc-none { color: #94a3b8; }
.score-sub { font-size: 9.5px; color: #b6c0cf; }

.contact-cell { display: flex; flex-direction: column; gap: 2px; }
.ct-title {
  display: inline-block; padding: 1px 6px; border-radius: 4px; background: #eef2ff;
  color: #4338ca; font-size: 10.5px; font-weight: 500; max-width: 140px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.ct-none { font-size: 10.5px; color: #cbd5e1; }
.ct-count { font-size: 9.5px; color: #94a3b8; }

.row-actions { display: flex; align-items: center; justify-content: flex-end; gap: 6px; }
.ico-btn {
  width: 28px; height: 28px; border-radius: 6px; border: 1px solid transparent;
  background: transparent; color: #94a3b8; cursor: pointer; display: grid; place-items: center;
}
.ico-btn:hover { background: #f1f5f9; color: #4f46e5; }
.ico-btn svg { width: 15px; height: 15px; stroke: currentColor; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.btn-mini {
  height: 27px; padding: 0 10px; border-radius: 6px; background: #4f46e5; border: 1px solid #4f46e5;
  color: #fff; font-size: 11px; font-weight: 600; cursor: pointer; white-space: nowrap;
}
.btn-mini:hover:not(:disabled) { background: #4338ca; }
.btn-mini:disabled { background: #cbd5e1; border-color: #cbd5e1; cursor: not-allowed; }

.empty { text-align: center; padding: 28px 0; color: #94a3b8; font-size: 12px; }

@media (max-width: 1280px) {
  .stat-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 700px) {
  .stat-row { grid-template-columns: minmax(0, 1fr); }
}
</style>
