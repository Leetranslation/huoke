<template>
  <div class="tasks">
    <!-- ===== 页头 ===== -->
    <div class="page-head">
      <div class="ph-left">
        <div class="kicker">
          <span class="k-badge">AUTONOMOUS SOURCING ENGINE</span>
          <span class="live"><i class="pulse"></i>智能体集群就绪</span>
        </div>
        <h1 class="page-title">获客任务中心 <span>(Lead Generation Tasks)</span></h1>
        <p class="page-sub">
          基于目标市场与行业特征，AI 流水线自主挖掘海外高意向采购商，并验证企业资质与决策人。
        </p>
      </div>
      <div class="ph-actions">
        <button class="btn-primary" @click="showForm = !showForm">
          <svg viewBox="0 0 24 24"><path d="M12 5v14M5 12h14" /></svg>
          {{ showForm ? '收起表单' : '新建获客任务' }}
        </button>
      </div>
    </div>

    <!-- ===== 3 指标卡 ===== -->
    <div class="stat-row">
      <div class="stat-card">
        <div class="sc-left">
          <span class="sc-label">执行中管线状态</span>
          <div class="sc-num-row">
            <span class="sc-num">{{ runningCount }}</span>
            <span class="sc-delta up">共 {{ campaigns.length }} 个任务</span>
          </div>
          <p class="sc-desc">{{ companies.length }} 家企业正在线索池中</p>
        </div>
        <div class="sc-ico indigo">
          <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3" /><path d="M12 3v3.5M12 17.5V21M3 12h3.5M17.5 12H21" /></svg>
        </div>
      </div>

      <div class="stat-card">
        <div class="sc-left">
          <span class="sc-label">已挖掘核验线索</span>
          <div class="sc-num-row">
            <span class="sc-num">{{ companies.length }}</span>
            <span class="sc-delta up">{{ contacts.length }} 位决策人</span>
          </div>
          <p class="sc-desc">含采购主管 / 管理层直投邮箱</p>
        </div>
        <div class="sc-ico emerald">
          <svg viewBox="0 0 24 24"><rect x="4" y="3.5" width="16" height="17" rx="2" /><path d="M8 9h8M8 13h8M8 17h5" /></svg>
        </div>
      </div>

      <div class="stat-card">
        <div class="sc-left">
          <span class="sc-label">高意向率 (AI 分 &gt; 85)</span>
          <div class="sc-num-row">
            <span class="sc-num indigo">{{ highFitPct }}%</span>
            <span class="sc-delta indigo">S 级标的 {{ highFitCount }} 家</span>
          </div>
          <div class="mini-track"><i :style="{ width: highFitPct + '%' }"></i></div>
        </div>
        <div class="sc-ico ring-ico">
          <svg viewBox="0 0 36 36">
            <circle cx="18" cy="18" r="15.9155" class="ring-bg" />
            <circle cx="18" cy="18" r="15.9155" class="ring-fg" :stroke-dasharray="highFitPct + ', 100'" />
          </svg>
        </div>
      </div>
    </div>

    <!-- ===== 创建表单（可折叠） ===== -->
    <div v-if="showForm" class="creator">
      <div class="creator-head">
        <div class="ch-left">
          <span class="ch-bar"></span>
          <div>
            <h2>创建与编排获客任务</h2>
            <p>配置搜索向量，AI 将自动拆解为「官网校验 → 线索挖掘 → 画像评分 → 决策人提取」任务链</p>
          </div>
        </div>
        <button class="icon-btn" @click="showForm = false">
          <svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18" /></svg>
        </button>
      </div>

      <div class="creator-body">
        <div class="c-left">
          <div class="field-2">
            <div class="field">
              <label>任务名称 <em>*</em></label>
              <input v-model="form.name" class="inp" placeholder="例如：2025 欧美工商业储能分销商" />
            </div>
            <div class="field">
              <label>核心推广产品 <em>*</em></label>
              <input v-model="form.product_name" class="inp" placeholder="输入精准产品名称" />
            </div>
          </div>

          <div class="field">
            <label>公司官网 <span class="hint">（AI 深度研读与语义对齐源）</span></label>
            <input v-model="form.website" class="inp" placeholder="https://yourcompany.com" />
          </div>

          <div class="field">
            <label>目标客户类型 <span class="hint">（可多选）</span></label>
            <div class="chips">
              <button
                v-for="t in typeOptions"
                :key="t"
                class="chip"
                :class="{ on: formTypes.includes(t) }"
                @click="toggleType(t)"
              >
                <svg v-if="formTypes.includes(t)" viewBox="0 0 24 24" class="chip-ico"><path d="m5 12 4 4 10-10" /></svg>
                <svg v-else viewBox="0 0 24 24" class="chip-ico"><path d="M12 5v14M5 12h14" /></svg>
                {{ t }}
              </button>
            </div>
          </div>

          <div class="field">
            <label>目标采购市场区域</label>
            <div class="checks">
              <label v-for="m in marketOptions" :key="m" class="check" :class="{ on: formMarkets.includes(m) }">
                <input type="checkbox" :checked="formMarkets.includes(m)" @change="toggleMarket(m)" />
                <span>{{ m }}</span>
              </label>
            </div>
          </div>
        </div>

        <div class="c-right">
          <div class="preview">
            <div class="pv-head">
              <svg viewBox="0 0 24 24" class="pv-ico"><circle cx="6" cy="6" r="2.4" /><circle cx="18" cy="6" r="2.4" /><circle cx="12" cy="18" r="2.4" /><path d="M6 8.4v2a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2v-2M12 12.4v3.2" /></svg>
              <span>AI 四步流水线</span>
            </div>
            <ol class="pv-steps">
              <li><b>官网语义解析</b>：提炼产品定位、目标客户与排除规则</li>
              <li><b>线索拓扑发现</b>：按市场区域批量抓取候选企业</li>
              <li><b>画像匹配打分</b>：逐家判定买家身份与意向分数</li>
              <li><b>决策人提取</b>：从官网抓取联系人邮箱</li>
            </ol>
            <p class="pv-tip">提示：创建后可在任务详情页逐步执行，每一步都会显示进度。</p>
          </div>

          <div class="creator-foot">
            <button class="btn-outline" @click="resetForm">重置</button>
            <button class="btn-primary" :disabled="creating" @click="create">
              <svg viewBox="0 0 24 24"><path d="m13 2-2 9h6l-8 11 2-9H5z" /></svg>
              {{ creating ? '创建中...' : '创建任务' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== 任务列表 ===== -->
    <div class="table-card">
      <div class="tc-head">
        <div class="tch-left">
          <h3>获客任务运行列表</h3>
          <span class="tch-badge">共 {{ campaigns.length }} 项</span>
        </div>
        <div class="tch-right">
          <div class="search-mini">
            <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></svg>
            <input v-model="filterKw" placeholder="按产品、区域或任务名称过滤..." />
          </div>
        </div>
      </div>

      <div class="table-scroll">
        <table>
          <thead>
            <tr>
              <th style="min-width: 220px">任务名称与定位</th>
              <th style="min-width: 150px">核心推广标的</th>
              <th style="min-width: 130px">目标市场</th>
              <th style="min-width: 150px">线索 / 联系人</th>
              <th style="min-width: 120px">流水线状态</th>
              <th style="min-width: 110px">创建时间</th>
              <th style="min-width: 110px" class="ta-right">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in filtered" :key="c.id">
              <td>
                <div class="t-name-col">
                  <span class="t-name" @click="$router.push('/campaigns/' + c.id)">{{ c.name }}</span>
                  <span class="t-site">{{ shortUrl(c.website) || '未配置官网' }}</span>
                </div>
              </td>
              <td><span class="t-product">{{ c.product_name || '—' }}</span></td>
              <td>
                <div class="t-markets">
                  <span v-for="m in (c.target_market || []).slice(0, 3)" :key="m" class="m-tag">{{ m }}</span>
                  <span v-if="!c.target_market?.length" class="muted">—</span>
                </div>
              </td>
              <td>
                <div class="t-quota">
                  <div class="q-top">
                    <span>{{ statOf(c.id).companies }} 家</span>
                    <span class="q-sep">/</span>
                    <span class="q-contacts">{{ statOf(c.id).contacts }} 位</span>
                  </div>
                  <div class="q-track">
                    <i :style="{ width: statOf(c.id).pct + '%' }" :class="statOf(c.id).tone"></i>
                  </div>
                </div>
              </td>
              <td>
                <span class="st" :class="statOf(c.id).stClass">
                  <i class="st-dot"></i>{{ statOf(c.id).stLabel }}
                </span>
              </td>
              <td class="t-time">{{ (c.created_at || '').slice(0, 10) }}</td>
              <td class="ta-right">
                <div class="row-actions">
                  <button class="ico-btn" title="查看详情" @click="$router.push('/campaigns/' + c.id)">
                    <svg viewBox="0 0 24 24"><circle cx="6" cy="6" r="2.2" /><circle cx="18" cy="6" r="2.2" /><circle cx="12" cy="18" r="2.2" /><path d="M6 8.2v1.6a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V8.2M12 11.8v4" /></svg>
                  </button>
                  <button class="btn-mini" @click="$router.push('/campaigns/' + c.id)">详情</button>
                </div>
              </td>
            </tr>
            <tr v-if="!filtered.length">
              <td colspan="7" class="empty">还没有任务，点击右上角「新建获客任务」开始</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { campaignApi, companyApi, contactApi } from '../api'

const campaigns = ref([])
const companies = ref([])
const contacts = ref([])
const showForm = ref(false)
const creating = ref(false)
const filterKw = ref('')

const typeOptions = ['区域总代', 'EPC 总承包商', '分销商', '安装运维商', '终端用户']
const marketOptions = ['北美', '西欧', 'DACH 德语区', '北欧', '澳洲', '中东', '东南亚']

const form = reactive({
  name: '',
  product_name: '',
  website: '',
})
const formTypes = ref([])
const formMarkets = ref([])

const runningCount = computed(
  () => campaigns.value.filter((c) => c.status !== 'completed').length
)
const highFitCount = computed(
  () => companies.value.filter((c) => (c.match_score || 0) > 85).length
)
const highFitPct = computed(() => {
  if (!companies.value.length) return 0
  return Math.round((highFitCount.value / companies.value.length) * 100)
})

const filtered = computed(() => {
  const k = filterKw.value.trim().toLowerCase()
  if (!k) return campaigns.value
  return campaigns.value.filter((c) =>
    [c.name, c.product_name, (c.target_market || []).join(' ')]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .includes(k)
  )
})

function shortUrl(u) {
  return (u || '').replace(/^https?:\/\//, '').replace(/\/$/, '')
}

function statOf(campaignId) {
  const cos = companies.value.filter((x) => x.campaign_id === campaignId)
  const ids = new Set(cos.map((x) => x.id))
  const cs = contacts.value.filter((x) => ids.has(x.company_id))
  const profiled = cos.filter((x) => x.profile && Object.keys(x.profile).length).length

  let step = 0
  if (cos.length) step = 1
  if (profiled) step = 2
  if (cs.length) step = 3
  if (step === 4) step = 4

  const pct = cos.length ? Math.min(100, Math.round((step / 4) * 100)) : 0
  let stLabel = '待启动'
  let stClass = 'st-idle'
  if (step === 4) {
    stLabel = '联系人就绪'
    stClass = 'st-done'
  } else if (step >= 1) {
    stLabel = '挖掘中'
    stClass = 'st-run'
  }
  const tone = step === 4 ? 'done' : step >= 1 ? 'run' : 'idle'
  return { companies: cos.length, contacts: cs.length, pct, stLabel, stClass, tone }
}

function toggleType(t) {
  const i = formTypes.value.indexOf(t)
  if (i >= 0) formTypes.value.splice(i, 1)
  else formTypes.value.push(t)
}
function toggleMarket(m) {
  const i = formMarkets.value.indexOf(m)
  if (i >= 0) formMarkets.value.splice(i, 1)
  else formMarkets.value.push(m)
}
function resetForm() {
  form.name = ''
  form.product_name = ''
  form.website = ''
  formTypes.value = []
  formMarkets.value = []
}

async function create() {
  if (!form.name.trim() || !form.product_name.trim()) {
    ElMessage.warning('任务名称和核心产品为必填项')
    return
  }
  creating.value = true
  try {
    await campaignApi.create({
      name: form.name.trim(),
      product_name: form.product_name.trim(),
      website: form.website.trim(),
      target_market: formMarkets.value,
      keywords: formTypes.value,
    })
    ElMessage.success('任务已创建')
    resetForm()
    showForm.value = false
    const r = await campaignApi.list()
    campaigns.value = r.data
  } catch (e) {
    ElMessage.error('创建失败：' + (e.response?.data?.detail || e.message))
  } finally {
    creating.value = false
  }
}

onMounted(async () => {
  const [c, co, ct] = await Promise.all([
    campaignApi.list(),
    companyApi.list(),
    contactApi.list(),
  ])
  campaigns.value = c.data
  companies.value = co.data
  contacts.value = ct.data
})
</script>

<style scoped>
.tasks { display: flex; flex-direction: column; gap: 18px; }

/* 页头 */
.page-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; flex-wrap: wrap; }
.ph-left { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.kicker { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.k-badge {
  font-size: 10px; font-weight: 700; letter-spacing: .06em; color: #4f46e5;
  background: #eef2ff; border: 1px solid #e0e7ff; padding: 2px 8px; border-radius: 999px;
}
.live { display: inline-flex; align-items: center; gap: 5px; font-size: 11px; font-weight: 500; color: #059669; }
.pulse {
  width: 6px; height: 6px; border-radius: 50%; background: #10b981;
  animation: pl 2s infinite;
}
@keyframes pl {
  0% { box-shadow: 0 0 0 0 rgba(16,185,129,.5); }
  70% { box-shadow: 0 0 0 6px rgba(16,185,129,0); }
  100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); }
}
.page-title { font-size: 23px; font-weight: 700; color: #0f172a; margin: 0; letter-spacing: -.025em; }
.page-title span { font-size: 15px; font-weight: 500; color: #64748b; }
.page-sub { font-size: 13px; color: #64748b; margin: 0; max-width: 680px; }
.ph-actions { display: flex; gap: 8px; flex: 0 0 auto; }

.btn-primary, .btn-outline {
  display: inline-flex; align-items: center; gap: 6px; height: 34px; padding: 0 14px;
  border-radius: 8px; font-size: 12.5px; font-weight: 600; cursor: pointer; white-space: nowrap;
  transition: all .15s;
}
.btn-primary { background: #4f46e5; border: 1px solid #4f46e5; color: #fff; box-shadow: 0 1px 2px rgba(79,70,229,.25); }
.btn-primary:hover:not(:disabled) { background: #4338ca; }
.btn-primary:disabled { background: #a5b4fc; border-color: #a5b4fc; cursor: not-allowed; }
.btn-outline { background: #fff; border: 1px solid #e2e8f0; color: #334155; }
.btn-outline:hover { background: #f8fafc; border-color: #cbd5e1; }
.btn-primary svg, .btn-outline svg { width: 14px; height: 14px; stroke: currentColor; fill: none; stroke-width: 1.9; stroke-linecap: round; stroke-linejoin: round; }

/* 指标卡 */
.stat-row { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.stat-card {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px 20px;
  display: flex; align-items: center; justify-content: space-between; gap: 14px;
  box-shadow: 0 1px 3px rgba(15,23,42,.04);
}
.sc-left { display: flex; flex-direction: column; gap: 5px; min-width: 0; }
.sc-label { font-size: 10.5px; font-weight: 700; color: #94a3b8; letter-spacing: .06em; text-transform: uppercase; }
.sc-num-row { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
.sc-num { font-size: 28px; font-weight: 800; color: #0f172a; letter-spacing: -.03em; font-variant-numeric: tabular-nums; line-height: 1.1; }
.sc-num.indigo { color: #4f46e5; }
.sc-delta { font-size: 11px; font-weight: 600; }
.sc-delta.up { color: #059669; }
.sc-delta.indigo { color: #4f46e5; }
.sc-desc { font-size: 11px; color: #64748b; margin: 0; }
.mini-track { width: 100%; max-width: 190px; height: 7px; border-radius: 4px; background: #f1f5f9; overflow: hidden; margin-top: 2px; }
.mini-track i { display: block; height: 100%; border-radius: 4px; background: linear-gradient(90deg, #6366f1, #10b981); transition: width .7s; }
.sc-ico { width: 46px; height: 46px; flex: 0 0 46px; border-radius: 12px; display: grid; place-items: center; }
.sc-ico svg { width: 21px; height: 21px; stroke: currentColor; fill: none; stroke-width: 1.7; stroke-linecap: round; stroke-linejoin: round; }
.sc-ico.indigo { background: #eef2ff; color: #4f46e5; border: 1px solid #e0e7ff; }
.sc-ico.emerald { background: #ecfdf5; color: #059669; border: 1px solid #d1fae5; }
.sc-ico.ring-ico { background: #f8fafc; border: 1px solid #e2e8f0; position: relative; }
.ring-ico svg { width: 30px; height: 30px; transform: rotate(-90deg); }
.ring-bg { fill: none; stroke: #e2e8f0; stroke-width: 3.5; }
.ring-fg { fill: none; stroke: #4f46e5; stroke-width: 3.5; stroke-linecap: round; }

/* 创建表单 */
.creator {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px 22px;
  box-shadow: 0 1px 3px rgba(15,23,42,.04); display: flex; flex-direction: column; gap: 18px;
}
.creator-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; padding-bottom: 14px; border-bottom: 1px solid #f1f5f9; }
.ch-left { display: flex; align-items: flex-start; gap: 10px; }
.ch-bar { width: 4px; height: 20px; border-radius: 3px; background: #4f46e5; flex: 0 0 4px; margin-top: 1px; }
.creator-head h2 { font-size: 14.5px; font-weight: 700; color: #0f172a; margin: 0; }
.creator-head p { font-size: 11.5px; color: #64748b; margin: 3px 0 0; max-width: 620px; }
.icon-btn {
  width: 28px; height: 28px; border-radius: 6px; border: 0; background: transparent;
  color: #94a3b8; cursor: pointer; display: grid; place-items: center; flex: 0 0 28px;
}
.icon-btn:hover { background: #f1f5f9; color: #475569; }
.icon-btn svg { width: 15px; height: 15px; stroke: currentColor; fill: none; stroke-width: 1.9; stroke-linecap: round; stroke-linejoin: round; }

.creator-body { display: grid; grid-template-columns: minmax(0, 8fr) minmax(0, 4fr); gap: 20px; }
.c-left { display: flex; flex-direction: column; gap: 14px; }
.field-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 11.5px; font-weight: 600; color: #334155; }
.field label em { color: #dc2626; font-style: normal; }
.field .hint { font-weight: 400; color: #94a3b8; }
.inp {
  height: 38px; padding: 0 12px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;
  font-size: 12.5px; color: #0f172a; outline: none; transition: all .15s;
}
.inp::placeholder { color: #94a3b8; }
.inp:focus { background: #fff; border-color: #4f46e5; box-shadow: 0 0 0 3px rgba(79,70,229,.1); }

.chips { display: flex; flex-wrap: wrap; gap: 7px; }
.chip {
  display: inline-flex; align-items: center; gap: 5px; height: 29px; padding: 0 11px;
  border-radius: 8px; border: 1px solid #e2e8f0; background: #f8fafc; color: #475569;
  font-size: 11.5px; font-weight: 500; cursor: pointer; transition: all .15s;
}
.chip:hover { background: #f1f5f9; }
.chip.on { background: #4f46e5; border-color: #4f46e5; color: #fff; box-shadow: 0 1px 2px rgba(79,70,229,.2); }
.chip-ico { width: 12px; height: 12px; stroke: currentColor; fill: none; stroke-width: 2.4; stroke-linecap: round; stroke-linejoin: round; }

.checks { display: flex; flex-wrap: wrap; gap: 7px; }
.check {
  display: inline-flex; align-items: center; gap: 6px; height: 30px; padding: 0 10px;
  border-radius: 8px; border: 1px solid #e2e8f0; background: #f8fafc; color: #475569;
  font-size: 11.5px; cursor: pointer; transition: all .15s;
}
.check:hover { background: #f1f5f9; }
.check.on { background: #eef2ff; border-color: #c7d2fe; color: #4338ca; font-weight: 600; }
.check input { accent-color: #4f46e5; width: 13px; height: 13px; }

.preview {
  background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px;
  display: flex; flex-direction: column; gap: 10px;
}
.pv-head { display: flex; align-items: center; gap: 7px; font-size: 12px; font-weight: 700; color: #4338ca; }
.pv-ico { width: 16px; height: 16px; stroke: currentColor; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.pv-steps { margin: 0; padding-left: 16px; display: flex; flex-direction: column; gap: 7px; font-size: 11px; color: #475569; line-height: 1.55; }
.pv-steps b { color: #0f172a; font-weight: 600; }
.pv-tip { font-size: 10.5px; color: #94a3b8; margin: 4px 0 0; line-height: 1.5; }
.creator-foot { display: flex; justify-content: flex-end; gap: 8px; padding-top: 12px; border-top: 1px solid #f1f5f9; }

/* 表格 */
.table-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 1px 3px rgba(15,23,42,.04); overflow: hidden; }
.tc-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 13px 18px; border-bottom: 1px solid #f1f5f9; flex-wrap: wrap; }
.tch-left { display: flex; align-items: center; gap: 8px; }
.tch-left h3 { font-size: 13.5px; font-weight: 700; color: #0f172a; margin: 0; }
.tch-badge { font-size: 10.5px; font-weight: 600; color: #475569; background: #f1f5f9; padding: 1px 7px; border-radius: 999px; }
.search-mini { position: relative; }
.search-mini svg {
  position: absolute; left: 10px; top: 50%; transform: translateY(-50%);
  width: 14px; height: 14px; stroke: #94a3b8; fill: none; stroke-width: 1.9; stroke-linecap: round; stroke-linejoin: round;
}
.search-mini input {
  height: 32px; width: 240px; padding: 0 10px 0 30px; background: #f8fafc; border: 1px solid #e2e8f0;
  border-radius: 8px; font-size: 11.5px; outline: none; color: #0f172a;
}
.search-mini input::placeholder { color: #94a3b8; }
.search-mini input:focus { background: #fff; border-color: #4f46e5; }

.table-scroll { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
thead th {
  background: #f8fafc; color: #94a3b8; font-size: 10.5px; font-weight: 700;
  text-transform: uppercase; letter-spacing: .05em; text-align: left;
  padding: 10px 16px; border-bottom: 1px solid #e2e8f0; white-space: nowrap;
}
tbody td { padding: 12px 16px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
tbody tr:last-child td { border-bottom: 0; }
tbody tr:hover { background: #f8fafc; }
.ta-right { text-align: right; }

.t-name-col { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.t-name { font-size: 12.5px; font-weight: 600; color: #0f172a; cursor: pointer; }
.t-name:hover { color: #4f46e5; }
.t-site { font-size: 10.5px; color: #94a3b8; font-family: ui-monospace, monospace; }
.t-product { font-size: 12px; color: #334155; }
.t-markets { display: flex; flex-wrap: wrap; gap: 4px; }
.m-tag { font-size: 10px; padding: 1px 6px; background: #f1f5f9; color: #475569; border-radius: 4px; white-space: nowrap; }
.muted { color: #cbd5e1; font-size: 11px; }

.t-quota { display: flex; flex-direction: column; gap: 5px; min-width: 110px; }
.q-top { display: flex; align-items: baseline; gap: 4px; font-size: 11px; color: #334155; font-weight: 600; font-variant-numeric: tabular-nums; }
.q-sep { color: #cbd5e1; font-weight: 400; }
.q-contacts { color: #4f46e5; }
.q-track { height: 5px; border-radius: 3px; background: #f1f5f9; overflow: hidden; }
.q-track i { display: block; height: 100%; border-radius: 3px; transition: width .6s; }
.q-track i.run { background: #10b981; }
.q-track i.done { background: #4f46e5; }
.q-track i.idle { background: #cbd5e1; }

.st { display: inline-flex; align-items: center; gap: 5px; padding: 3px 9px; border-radius: 999px; font-size: 10.5px; font-weight: 600; white-space: nowrap; }
.st-dot { width: 5px; height: 5px; border-radius: 50%; background: currentColor; }
.st-run { background: #ecfdf5; color: #047857; border: 1px solid #d1fae5; }
.st-done { background: #eef2ff; color: #4338ca; border: 1px solid #e0e7ff; }
.st-idle { background: #f8fafc; color: #94a3b8; border: 1px solid #e2e8f0; }

.t-time { font-size: 11px; color: #94a3b8; font-variant-numeric: tabular-nums; }

.row-actions { display: flex; align-items: center; justify-content: flex-end; gap: 6px; }
.ico-btn {
  width: 28px; height: 28px; border-radius: 6px; border: 1px solid transparent; background: transparent;
  color: #94a3b8; cursor: pointer; display: grid; place-items: center;
}
.ico-btn:hover { background: #eef2ff; color: #4f46e5; }
.ico-btn svg { width: 15px; height: 15px; stroke: currentColor; fill: none; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.btn-mini {
  height: 27px; padding: 0 10px; border-radius: 6px; background: #4f46e5; border: 1px solid #4f46e5;
  color: #fff; font-size: 11px; font-weight: 600; cursor: pointer;
}
.btn-mini:hover { background: #4338ca; }

.empty { text-align: center; padding: 32px 0; color: #94a3b8; font-size: 12px; }

@media (max-width: 1200px) {
  .stat-row { grid-template-columns: minmax(0, 1fr); }
  .creator-body { grid-template-columns: minmax(0, 1fr); }
}
@media (max-width: 760px) {
  .field-2 { grid-template-columns: minmax(0, 1fr); }
}
</style>
