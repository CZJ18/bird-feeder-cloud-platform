<template>
  <div class="events-page">
    <div class="page-header">
      <h2>鸟类识别记录</h2>
      <div class="filters">
        <el-select
          v-model="filterDevice"
          placeholder="选择设备"
          clearable
          @change="loadEvents"
        >
          <el-option
            v-for="device in devices"
            :key="device.device_id"
            :label="device.name"
            :value="device.device_id"
          />
        </el-select>
        <el-input
          v-model="filterBird"
          placeholder="输入鸟类名称"
          clearable
          @change="loadEvents"
          style="width: 200px"
        />
      </div>
    </div>

    <el-table
      :data="events"
      stripe
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="device_id" label="设备ID" width="120" />
      <el-table-column prop="bird_name" label="鸟类名称" width="120" />
      <el-table-column label="置信度" width="120">
        <template #default="{ row }">
          <el-tag type="success">{{ (row.confidence * 100).toFixed(0) }}%</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="图片" width="120">
        <template #default="{ row }">
          <el-image
            :src="row.image_url"
            :preview-src-list="[row.image_url]"
            fit="cover"
            style="width: 80px; height: 60px; border-radius: 8px; cursor: pointer;"
          >
            <template #error>
              <div class="image-error">
                <el-icon><Picture /></el-icon>
              </div>
            </template>
          </el-image>
        </template>
      </el-table-column>
      <el-table-column label="电池" width="100">
        <template #default="{ row }">
          <span :style="{ color: getBatteryColor(row.battery) }">{{ row.battery }}%</span>
        </template>
      </el-table-column>
      <el-table-column label="饲料" width="100">
        <template #default="{ row }">
          <span :style="{ color: getFoodColor(row.food_level) }">{{ row.food_level }}%</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="识别时间" min-width="180" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Picture } from '@element-plus/icons-vue'
import { getBirdEvents } from '@/api/bird'
import { getDeviceList } from '@/api/device'
import type { BirdEvent, Device } from '@/types'

const events = ref<BirdEvent[]>([])
const devices = ref<Device[]>([])
const loading = ref(false)
const filterDevice = ref('')
const filterBird = ref('')

const loadEvents = async () => {
  loading.value = true
  try {
    events.value = await getBirdEvents({
      device_id: filterDevice.value || undefined,
      bird_name: filterBird.value || undefined
    })
  } catch (error) {
    console.error('Failed to load events:', error)
  } finally {
    loading.value = false
  }
}

const loadDevices = async () => {
  try {
    devices.value = await getDeviceList()
  } catch (error) {
    console.error('Failed to load devices:', error)
  }
}

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

onMounted(() => {
  loadEvents()
  loadDevices()
})
</script>

<style scoped lang="scss">
.events-page {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  
  h2 {
    color: #ffffff;
    font-size: 24px;
    font-weight: 600;
    margin: 0;
  }
  
  .filters {
    display: flex;
    gap: 12px;
  }
}

.image-error {
  width: 80px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #333;
  border-radius: 8px;
  color: #8b8ba3;
}

:deep(.el-table) {
  background: rgba(26, 26, 46, 0.8) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 12px;
  overflow: hidden;
  
  th.el-table__cell {
    background: rgba(0, 212, 255, 0.1) !important;
    color: #00d4ff !important;
    font-weight: 600;
    border-bottom: 1px solid rgba(0, 212, 255, 0.2);
  }
  
  td.el-table__cell {
    background: rgba(26, 26, 46, 0.5) !important;
    color: #ffffff;
    border-bottom: 1px solid rgba(0, 212, 255, 0.1);
  }
  
  tr:hover > td.el-table__cell {
    background: rgba(0, 212, 255, 0.1) !important;
  }
}
</style>
