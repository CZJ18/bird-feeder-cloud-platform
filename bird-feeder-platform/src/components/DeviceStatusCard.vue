<template>
  <div class="device-status-card">
    <div class="card-header">
      <div class="device-info">
        <div class="device-name">{{ device.name }}</div>
        <div class="device-id">{{ device.device_id }}</div>
      </div>
      <el-tag :type="device.status === 'online' ? 'success' : 'danger'" size="small">
        {{ device.status === 'online' ? '在线' : '离线' }}
      </el-tag>
    </div>
    
    <div class="card-body">
      <div class="info-row">
        <span class="label">位置</span>
        <span class="value">{{ device.location }}</span>
      </div>
      <div class="info-row">
        <span class="label">网络</span>
        <el-tag size="small" type="info">{{ device.network }}</el-tag>
      </div>
      <div class="info-row">
        <span class="label">最后在线</span>
        <span class="value time">{{ device.last_online }}</span>
      </div>
    </div>
    
    <div class="card-footer">
      <div class="progress-item">
        <div class="progress-header">
          <span class="label">电池</span>
          <span class="value">{{ device.battery }}%</span>
        </div>
        <el-progress 
          :percentage="device.battery" 
          :color="getBatteryColor(device.battery)"
          :show-text="false"
          :stroke-width="6"
        />
      </div>
      <div class="progress-item">
        <div class="progress-header">
          <span class="label">饲料</span>
          <span class="value">{{ device.food_level }}%</span>
        </div>
        <el-progress 
          :percentage="device.food_level" 
          :color="getFoodColor(device.food_level)"
          :show-text="false"
          :stroke-width="6"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Device } from '@/types'

interface Props {
  device: Device
}

defineProps<Props>()

const getBatteryColor = (value: number) => {
  if (value > 60) return '#00ff88'
  if (value > 30) return '#ffb800'
  return '#ff4757'
}

const getFoodColor = (value: number) => {
  if (value > 60) return '#00d4ff'
  if (value > 30) return '#ffb800'
  return '#ff4757'
}
</script>

<style scoped lang="scss">
.device-status-card {
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 12px;
  padding: 16px;
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 212, 255, 0.1);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.device-info {
  flex: 1;
}

.device-name {
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.device-id {
  color: #8b8ba3;
  font-size: 12px;
}

.card-body {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 212, 255, 0.1);
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  
  &:last-child {
    margin-bottom: 0;
  }
  
  .label {
    color: #8b8ba3;
    font-size: 13px;
  }
  
  .value {
    color: #ffffff;
    font-size: 13px;
    
    &.time {
      font-size: 12px;
      color: #8b8ba3;
    }
  }
}

.card-footer {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.progress-item {
  .progress-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
    
    .label {
      color: #8b8ba3;
      font-size: 12px;
    }
    
    .value {
      color: #ffffff;
      font-size: 12px;
      font-weight: 600;
    }
  }
}
</style>
