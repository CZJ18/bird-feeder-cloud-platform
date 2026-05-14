<template>
  <div class="stat-card" :style="{ borderColor: borderColor }">
    <div class="card-header">
      <div class="icon-wrapper" :style="{ background: iconBg }">
        <el-icon :size="28" :color="color">
          <component :is="icon" />
        </el-icon>
      </div>
      <span class="label">{{ label }}</span>
    </div>
    <div class="card-body">
      <div class="value">{{ displayValue }}</div>
      <div v-if="trend" class="trend" :class="trendClass">
        <el-icon v-if="trend > 0"><Top /></el-icon>
        <el-icon v-else><Bottom /></el-icon>
        <span>{{ Math.abs(trend) }}%</span>
      </div>
    </div>
    <div v-if="subtitle" class="card-footer">
      <span class="subtitle">{{ subtitle }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Top, Bottom } from '@element-plus/icons-vue'

interface Props {
  label: string
  value: number | string
  icon: any
  color?: string
  trend?: number
  subtitle?: string
  suffix?: string
}

const props = withDefaults(defineProps<Props>(), {
  color: '#00d4ff',
  trend: 0,
  suffix: ''
})

const displayValue = computed(() => {
  return typeof props.value === 'number' 
    ? props.value.toLocaleString() + props.suffix 
    : props.value
})

const borderColor = computed(() => {
  return `${props.color}33`
})

const iconBg = computed(() => {
  return `${props.color}15`
})

const trendClass = computed(() => {
  return props.trend >= 0 ? 'positive' : 'negative'
})
</script>

<style scoped lang="scss">
.stat-card {
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 212, 255, 0.15);
  }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.label {
  color: #8b8ba3;
  font-size: 14px;
  font-weight: 500;
}

.card-body {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.value {
  color: #ffffff;
  font-size: 32px;
  font-weight: 700;
  letter-spacing: 2px;
}

.trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 6px;
  
  &.positive {
    color: #00ff88;
    background: rgba(0, 255, 136, 0.1);
  }
  
  &.negative {
    color: #ff4757;
    background: rgba(255, 71, 87, 0.1);
  }
}

.card-footer {
  .subtitle {
    color: #8b8ba3;
    font-size: 12px;
  }
}
</style>
