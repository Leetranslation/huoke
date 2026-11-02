<template>
  <div class="login">
    <!-- 顶部 -->
    <header class="top">
      <div class="brand">
        <div class="brand-mark">
          <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3" /><circle cx="12" cy="12" r="7.5" opacity=".55" /><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2" /></svg>
        </div>
        <div class="brand-text">
          <div class="brand-name-row">
            <span class="brand-name">远洋获客</span>
            <span class="brand-tag">PRO</span>
          </div>
          <span class="brand-sub">AI 外贸获客自动化引擎</span>
        </div>
      </div>
      <div class="top-right">
        <span class="status-pill"><i class="dot"></i>服务在线</span>
        <span class="engine">v1.0 · YxAgent</span>
      </div>
    </header>

    <!-- 主体 -->
    <main class="body">
      <!-- 左：品牌区 -->
      <section class="intro">
        <span class="intro-badge">
          <svg viewBox="0 0 24 24"><path d="m12 3 1.8 4.4L18 9l-4.2 1.6L12 15l-1.8-4.4L6 9l4.2-1.6z" /></svg>
          新一代外贸买家画像大模型 · 精准触达
        </span>
        <h1 class="intro-title">
          精准洞察全球高价值采购商<br />
          <span>AI 驱动全链路自动化销售管线</span>
        </h1>
        <p class="intro-sub">
          基于多模态官网语义解析、企业 DNA 建模与决策人图谱，自动完成「找客户 → 画像评分 → 个性化开发信 → 打开追踪 → 回复识别 → 自动跟进」闭环。
        </p>

        <div class="intro-cards">
          <div class="ic">
            <div class="ic-head">
              <span class="ic-label">已挖掘企业</span>
              <span class="ic-pill emerald">买家 {{ buyerPct }}%</span>
            </div>
            <div class="ic-num">{{ companies.length }}<span>家</span></div>
            <div class="ic-foot">{{ contacts.length }} 位决策人联系人</div>
          </div>
          <div class="ic">
            <div class="ic-head">
              <span class="ic-label">覆盖国家 / 地区</span>
              <span class="ic-pill indigo">实时同步</span>
            </div>
            <div class="ic-num">{{ countries }}<span>个</span></div>
            <div class="ic-foot">{{ campaigns.length }} 个获客任务在管</div>
          </div>
        </div>

        <div class="intro-flow">
          <span class="flow-label">流水线</span>
          <div class="flow-steps">
            <span v-for="(s, i) in flow" :key="s" class="flow-step">
              <i>{{ i + 1 }}</i>{{ s }}
            </span>
          </div>
        </div>
      </section>

      <!-- 右：登录卡 -->
      <section class="login-card">
        <div class="lc-bar"></div>
        <div class="lc-body">
          <div class="lc-kicker">
            <svg viewBox="0 0 24 24"><path d="m12 3 7 3v5.5c0 4.2-2.9 7.6-7 8.5-4.1-.9-7-4.3-7-8.5V6z" /></svg>
            企业控制台
          </div>
          <h2 class="lc-title">登录系统</h2>
          <p class="lc-sub">访问您的智能获客工作台</p>

          <div class="field">
            <label>企业邮箱</label>
            <div class="inp-wrap">
              <svg viewBox="0 0 24 24"><rect x="3" y="5.4" width="18" height="13.2" rx="2.2" /><path d="m4.2 7.2 7.8 5.6 7.8-5.6" /></svg>
              <input v-model="email" placeholder="name@company.com" @keyup.enter="login" />
            </div>
          </div>

          <div class="field">
            <label>登录密码</label>
            <div class="inp-wrap">
              <svg viewBox="0 0 24 24"><rect x="4" y="10" width="16" height="10" rx="2" /><path d="M8 10V7.5a4 4 0 0 1 8 0V10" /></svg>
              <input v-model="password" :type="showPwd ? 'text' : 'password'" placeholder="请输入密码" @keyup.enter="login" />
              <button class="eye" @click="showPwd = !showPwd">
                <svg v-if="!showPwd" viewBox="0 0 24 24"><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12z" /><circle cx="12" cy="12" r="2.6" /></svg>
                <svg v-else viewBox="0 0 24 24"><path d="M3 3l18 18" /><path d="M10.6 6.2A9.8 9.8 0 0 1 12 6c6.5 0 10 6 10 6a17 17 0 0 1-3.4 4" /><path d="M6.2 8.3A16.7 16.7 0 0 0 2 12s3.5 6 10 6c1.5 0 2.8-.3 4-.8" /></svg>
              </button>
            </div>
          </div>

          <button class="login-btn" @click="login">
            登录系统
            <span class="kbd">Enter</span>
          </button>

          <p class="lc-tip">演示环境 · 任意邮箱密码可直接进入</p>
        </div>
      </section>
    </main>

    <!-- 底部 -->
    <footer class="foot">
      <span>AI 生成开发信 · 全链路邮件追踪 · 回复自动识别</span>
      <span>© 2026 远洋获客 YxAgent</span>
    </footer>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { campaignApi, companyApi, contactApi } from '../api'

const router = useRouter()
const email = ref('')
const password = ref('')
const showPwd = ref(false)
const campaigns = ref([])
const companies = ref([])
const contacts = ref([])

const flow = ['官网分析', '线索挖掘', '画像评分', '开发信', '追踪回复']

const countries = ref(0)
const buyerPct = ref(0)

function login() {
  if (!email.value.trim()) {
    ElMessage.warning('请输入邮箱')
    return
  }
  router.push('/dashboard')
}

onMounted(async () => {
  try {
    const [c, co, ct] = await Promise.all([
      campaignApi.list(),
      companyApi.list(),
      contactApi.list(),
    ])
    campaigns.value = c.data
    companies.value = co.data
    contacts.value = ct.data
    countries.value = new Set(companies.value.map((x) => x.country).filter(Boolean)).size
    const buyers = companies.value.filter((x) => x.identity === 'buyer').length
    buyerPct.value = companies.value.length
      ? Math.round((buyers / companies.value.length) * 100)
      : 0
  } catch (e) {
    /* 登录页静默失败 */
  }
})
</script>

<style scoped>
.login {
  min-height: 100vh; background: #f8fafc;
  display: flex; flex-direction: column;
  background-image: radial-gradient(circle at 15% 0%, rgba(99, 102, 241, .07), transparent 45%),
    radial-gradient(circle at 85% 100%, rgba(16, 185, 129, .06), transparent 45%);
}

/* 顶部 */
.top { display: flex; align-items: center; justify-content: space-between; padding: 18px 32px; }
.brand { display: flex; align-items: center; gap: 10px; }
.brand-mark {
  width: 34px; height: 34px; border-radius: 9px; display: grid; place-items: center;
  background: linear-gradient(135deg, #6366f1, #4f46e5); box-shadow: 0 2px 8px rgba(79,70,229,.28);
}
.brand-mark svg { width: 18px; height: 18px; stroke: #fff; fill: none; stroke-width: 1.9; stroke-linecap: round; }
.brand-text { display: flex; flex-direction: column; gap: 1px; }
.brand-name-row { display: flex; align-items: center; gap: 6px; }
.brand-name { font-size: 14px; font-weight: 700; color: #0f172a; letter-spacing: -.01em; }
.brand-tag {
  font-size: 8.5px; font-weight: 700; letter-spacing: .06em; color: #fff;
  background: #4f46e5; padding: 1px 5px; border-radius: 3px;
}
.brand-sub { font-size: 10px; color: #94a3b8; }
.top-right { display: flex; align-items: center; gap: 10px; }
.status-pill {
  display: inline-flex; align-items: center; gap: 5px; font-size: 10.5px; font-weight: 600;
  color: #047857; background: #ecfdf5; border: 1px solid #d1fae5; padding: 3px 9px; border-radius: 999px;
}
.dot { width: 5px; height: 5px; border-radius: 50%; background: #10b981; }
.engine { font-size: 10.5px; color: #94a3b8; font-family: ui-monospace, monospace; }

/* 主体 */
.body {
  flex: 1; display: grid; grid-template-columns: minmax(0, 1fr) 400px;
  gap: 56px; align-items: center; padding: 0 56px; max-width: 1280px; width: 100%; margin: 0 auto;
}

.intro { display: flex; flex-direction: column; gap: 18px; min-width: 0; }
.intro-badge {
  align-self: flex-start; display: inline-flex; align-items: center; gap: 5px;
  font-size: 11px; font-weight: 600; color: #4338ca;
  background: #eef2ff; border: 1px solid #e0e7ff; padding: 4px 11px; border-radius: 999px;
}
.intro-badge svg { width: 12px; height: 12px; stroke: currentColor; fill: none; stroke-width: 1.9; stroke-linejoin: round; }
.intro-title {
  font-size: 36px; font-weight: 800; color: #0f172a; line-height: 1.28;
  letter-spacing: -.035em; margin: 0;
}
.intro-title span { color: #4f46e5; }
.intro-sub { font-size: 13px; color: #64748b; line-height: 1.85; margin: 0; max-width: 540px; }

.intro-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; max-width: 520px; }
.ic { background: #fff; border: 1px solid #e2e8f0; border-radius: 11px; padding: 14px 16px; display: flex; flex-direction: column; gap: 5px; box-shadow: 0 1px 3px rgba(15,23,42,.04); }
.ic-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.ic-label { font-size: 10.5px; font-weight: 600; color: #64748b; }
.ic-pill { font-size: 9px; font-weight: 700; padding: 1px 6px; border-radius: 999px; }
.ic-pill.emerald { color: #047857; background: #ecfdf5; border: 1px solid #d1fae5; }
.ic-pill.indigo { color: #4338ca; background: #eef2ff; border: 1px solid #e0e7ff; }
.ic-num { font-size: 28px; font-weight: 800; color: #0f172a; letter-spacing: -.03em; font-variant-numeric: tabular-nums; line-height: 1.1; }
.ic-num span { font-size: 12px; font-weight: 600; color: #94a3b8; margin-left: 3px; }
.ic-foot { font-size: 10.5px; color: #94a3b8; }

.intro-flow { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.flow-label { font-size: 9.5px; font-weight: 700; color: #cbd5e1; text-transform: uppercase; letter-spacing: .06em; }
.flow-steps { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.flow-step {
  display: inline-flex; align-items: center; gap: 4px; font-size: 10.5px; color: #475569;
  background: #fff; border: 1px solid #e2e8f0; padding: 3px 9px 3px 5px; border-radius: 999px;
}
.flow-step i {
  width: 14px; height: 14px; border-radius: 50%; background: #eef2ff; color: #4338ca;
  display: grid; place-items: center; font-size: 8px; font-weight: 700; font-style: normal;
}

/* 登录卡 */
.login-card {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 14px; overflow: hidden;
  box-shadow: 0 20px 50px -12px rgba(15, 23, 42, .12), 0 4px 12px rgba(15,23,42,.04);
}
.lc-bar { height: 4px; background: linear-gradient(90deg, #4f46e5, #6366f1 55%, #a5b4fc); }
.lc-body { padding: 26px 28px 22px; display: flex; flex-direction: column; gap: 13px; }
.lc-kicker {
  display: inline-flex; align-items: center; gap: 4px; align-self: flex-start;
  font-size: 9.5px; font-weight: 700; color: #4338ca; letter-spacing: .05em;
  background: #eef2ff; border: 1px solid #e0e7ff; padding: 2px 8px; border-radius: 999px;
}
.lc-kicker svg { width: 10px; height: 10px; stroke: currentColor; fill: none; stroke-width: 2; stroke-linejoin: round; }
.lc-title { font-size: 22px; font-weight: 800; color: #0f172a; margin: 2px 0 0; letter-spacing: -.03em; }
.lc-sub { font-size: 11.5px; color: #94a3b8; margin: -8px 0 4px; }

.field { display: flex; flex-direction: column; gap: 5px; }
.field label { font-size: 10.5px; font-weight: 600; color: #334155; }
.inp-wrap { position: relative; display: flex; align-items: center; }
.inp-wrap > svg {
  position: absolute; left: 11px; width: 14px; height: 14px; stroke: #94a3b8;
  fill: none; stroke-width: 1.9; stroke-linecap: round; stroke-linejoin: round; pointer-events: none;
}
.inp-wrap input {
  width: 100%; height: 40px; padding: 0 38px 0 32px; background: #f8fafc;
  border: 1px solid #e2e8f0; border-radius: 8px; font-size: 12.5px; color: #0f172a;
  outline: none; transition: all .15s;
}
.inp-wrap input::placeholder { color: #b6c0cf; }
.inp-wrap input:focus { background: #fff; border-color: #4f46e5; box-shadow: 0 0 0 3px rgba(79,70,229,.11); }
.eye {
  position: absolute; right: 8px; width: 26px; height: 26px; border: 0; background: transparent;
  color: #94a3b8; cursor: pointer; display: grid; place-items: center; border-radius: 5px;
}
.eye:hover { background: #f1f5f9; color: #475569; }
.eye svg { width: 14px; height: 14px; stroke: currentColor; fill: none; stroke-width: 1.9; stroke-linecap: round; stroke-linejoin: round; }

.login-btn {
  height: 42px; margin-top: 4px; border: 0; border-radius: 9px; cursor: pointer;
  background: linear-gradient(135deg, #4f46e5, #4338ca); color: #fff;
  font-size: 13px; font-weight: 700; letter-spacing: .01em;
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  box-shadow: 0 4px 14px rgba(79, 70, 229, .28);
  transition: all .15s;
}
.login-btn:hover { transform: translateY(-1px); box-shadow: 0 6px 18px rgba(79,70,229,.34); }
.login-btn:active { transform: translateY(0); }
.kbd {
  font-size: 9px; font-weight: 600; background: rgba(255,255,255,.2);
  padding: 1px 5px; border-radius: 3px; font-family: ui-monospace, monospace;
}
.lc-tip { text-align: center; font-size: 10.5px; color: #b6c0cf; margin: 2px 0 0; }

/* 底部 */
.foot {
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
  padding: 14px 32px; font-size: 10.5px; color: #b6c0cf; flex-wrap: wrap;
}

@media (max-width: 1080px) {
  .body { grid-template-columns: minmax(0, 1fr); gap: 32px; padding: 0 32px 32px; }
  .intro-title { font-size: 28px; }
  .login-card { max-width: 400px; width: 100%; }
}
@media (max-width: 620px) {
  .top { padding: 14px 20px; }
  .body { padding: 0 20px 24px; }
  .intro-title { font-size: 24px; }
  .intro-cards { grid-template-columns: 1fr; }
}
</style>
