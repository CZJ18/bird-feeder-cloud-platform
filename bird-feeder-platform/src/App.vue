<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

onMounted(() => {
  console.log('智能喂鸟器云端管理平台已启动')
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  width: 100%;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol',
    'Noto Color Emoji';
}

body {
  background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
  min-height: 100vh;
}

/* Element Plus 主题覆盖 */
.el-button--primary {
  --el-button-bg-color: #00d4ff !important;
  --el-button-border-color: #00d4ff !important;
  --el-button-hover-bg-color: #00b8e6 !important;
  --el-button-hover-border-color: #00b8e6 !important;
}

.el-input__wrapper {
  background: rgba(26, 26, 46, 0.8) !important;
  border: 1px solid rgba(0, 212, 255, 0.2) !important;
  box-shadow: none !important;
}

.el-input__inner {
  color: #ffffff !important;
}

.el-input__inner::placeholder {
  color: #8b8ba3 !important;
}

.el-select .el-input__wrapper {
  background: rgba(26, 26, 46, 0.8) !important;
}

.el-select-dropdown {
  background: rgba(26, 26, 46, 0.95) !important;
  border: 1px solid rgba(0, 212, 255, 0.2) !important;
}

.el-select-dropdown__item {
  color: #ffffff !important;
}

.el-select-dropdown__item.hover,
.el-select-dropdown__item:hover {
  background: rgba(0, 212, 255, 0.1) !important;
}

.el-select-dropdown__item.selected {
  color: #00d4ff !important;
}

.el-date-editor .el-input__wrapper {
  background: rgba(26, 26, 46, 0.8) !important;
}

.el-picker-panel {
  background: rgba(26, 26, 46, 0.95) !important;
  border: 1px solid rgba(0, 212, 255, 0.2) !important;
  color: #ffffff !important;
}

.el-date-picker__header-label {
  color: #ffffff !important;
}

.el-picker-panel__icon-btn {
  color: #8b8ba3 !important;
}

.el-date-table th {
  color: #8b8ba3 !important;
}

.el-date-table td.available:hover {
  background: rgba(0, 212, 255, 0.1) !important;
}

.el-date-table td.current:not(.disabled) .el-date-table-cell__text {
  background: #00d4ff !important;
}

.el-input-number {
  --el-input-bg-color: rgba(26, 26, 46, 0.8) !important;
  --el-input-border-color: rgba(0, 212, 255, 0.2) !important;
}

.el-input-number .el-input__inner {
  color: #ffffff !important;
}

.el-input-number__decrease,
.el-input-number__increase {
  background: rgba(0, 212, 255, 0.1) !important;
  color: #00d4ff !important;
  border-color: rgba(0, 212, 255, 0.2) !important;
}

.el-form-item__label {
  color: #8b8ba3 !important;
}

.el-dialog {
  background: rgba(26, 26, 46, 0.95) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 12px;
}

.el-dialog__header {
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
}

.el-dialog__title {
  color: #ffffff !important;
}

.el-dialog__body {
  color: #ffffff !important;
}

.el-tag {
  border-radius: 6px;
}

.el-empty__description {
  color: #8b8ba3 !important;
}

::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(26, 26, 46, 0.5);
}

::-webkit-scrollbar-thumb {
  background: rgba(0, 212, 255, 0.3);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 212, 255, 0.5);
}

/* 动画 */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
