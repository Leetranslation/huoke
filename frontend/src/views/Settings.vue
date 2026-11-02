<template>
  <div>
    <div class="page-head">
      <div>
        <h1 class="page-title">设置</h1>
        <p class="page-sub">账号、邮件与模型配置</p>
      </div>
    </div>

    <div class="card" style="max-width:640px">
      <div class="field">
        <label class="label">邮箱</label>
        <input class="input" value="demo@example.com" />
      </div>
      <div class="field">
        <label class="label">SMTP 主机</label>
        <input class="input" placeholder="smtp.qq.com" />
      </div>
      <div class="form-row">
        <div class="field"><label class="label">端口</label><input class="input" placeholder="465" /></div>
        <div class="field"><label class="label">密码 / 授权码</label><input class="input" type="password" /></div>
      </div>
      <div class="field">
        <label class="label">模型</label>
        <input class="input" value="deepseek-chat" disabled />
      </div>
      <button class="btn btn-primary" @click="save">保存</button>
    </div>
  </div>
</template>

<script setup>
const save = () => alert('已保存（演示）')
</script>
