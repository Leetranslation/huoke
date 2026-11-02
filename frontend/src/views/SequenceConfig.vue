<template>
  <div>
    <div class="page-head">
      <div>
        <h1 class="page-title">跟进序列</h1>
        <p class="page-sub">配置自动跟进的轮次与节奏（对应状态机）</p>
      </div>
    </div>

    <div class="card" style="margin-bottom:16px">
      <div class="card-head"><div class="card-title"><span class="t-dot"></span>序列参数</div></div>
      <div class="form-row">
        <div class="field" style="margin-bottom:0">
          <label class="label">总轮次</label>
          <input class="input" type="number" v-model="maxSteps" min="1" max="10" />
        </div>
        <div class="field" style="margin-bottom:0">
          <label class="label">每轮间隔（天）</label>
          <input class="input" type="number" v-model="interval" min="1" max="30" />
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-head"><div class="card-title"><span class="t-dot"></span>序列步骤</div></div>
      <div v-for="(s, i) in steps" :key="i" class="step-row">
        <span class="step-no">{{ i + 1 }}</span>
        <div style="flex:1">
          <div class="step-title">{{ s.title }}</div>
          <div class="step-desc">{{ s.desc }}</div>
        </div>
        <span class="chip chip-gray">{{ s.time }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const maxSteps = ref(5)
const interval = ref(3)
const steps = ref([
  { title: '首封开发信', desc: '基于画像的个性化开发信', time: '第 0 天' },
  { title: '未打开重发', desc: '换标题 / 时间重新发送', time: '+3 天' },
  { title: '未回复跟进', desc: '换角度补充价值点', time: '+5 天' },
  { title: '再次跟进', desc: '提供案例 / 数据', time: '+7 天' },
  { title: '最后尝试', desc: '礼貌收尾，超限自动停止', time: '+7 天' },
])
</script>

<style scoped>
.step-row { display:flex; align-items:center; gap:14px; padding:14px 0; border-bottom:1px solid #F2F4F8; }
.step-row:last-child { border-bottom:0; }
.step-no {
  width:28px; height:28px; border-radius:50%; background:var(--primary-weak); color:var(--primary);
  display:grid; place-items:center; font-size:12px; font-weight:700; flex:0 0 28px;
}
.step-title { font-weight:600; font-size:13px; }
.step-desc { color:var(--muted-2); font-size:11.5px; margin-top:3px; }
</style>
