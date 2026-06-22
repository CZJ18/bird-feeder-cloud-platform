<template>
  <div class="devices-page">
    <div class="page-header">
      <h2>设备管理</h2>
    </div>

    <el-table
      :data="devices"
      stripe
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column prop="device_id" label="设备ID" width="120" />
      <el-table-column prop="name" label="设备名称" min-width="150" />
      <el-table-column prop="location" label="位置" min-width="150" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'online' ? 'success' : 'danger'" size="small">
            {{ row.status === 'online' ? '在线' : '离线' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="电池" width="180">
        <template #default="{ row }">
          <div class="progress-cell">
            <el-progress
              :percentage="row.battery"
              :color="getBatteryColor(row.battery)"
              :show-text="false"
              :stroke-width="8"
            />
            <span class="progress-text">{{ row.battery }}%</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="饲料余量" width="180">
        <template #default="{ row }">
          <div class="progress-cell">
            <el-progress
              :percentage="row.food_level"
              :color="getFoodColor(row.food_level)"
              :show-text="false"
              :stroke-width="8"
            />
            <span class="progress-text">{{ row.food_level }}%</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="network" label="网络" width="100">
        <template #default="{ row }">
          <el-tag type="info" size="small">{{ row.network }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="last_online" label="最后在线" width="160" />
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="viewDetail(row)">
            查看详情
          </el-button>
          <el-button type="success" size="small" @click="capture(row)" :disabled="row.status === 'offline'">
            立即拍照
          </el-button>
          <el-button type="warning" size="small" @click="restart(row)" :disabled="row.status === 'offline'">
            重启设备
          </el-button>
          <el-button type="info" size="small" @click="openConfig(row)">
            修改参数
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="detailDialogVisible" title="设备详情" width="600px">
      <div v-if="selectedDevice" class="device-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="设备ID">{{ selectedDevice.device_id }}</el-descriptions-item>
          <el-descriptions-item label="设备名称">{{ selectedDevice.name }}</el-descriptions-item>
          <el-descriptions-item label="位置">{{ selectedDevice.location }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="selectedDevice.status === 'online' ? 'success' : 'danger'">
              {{ selectedDevice.status === 'online' ? '在线' : '离线' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="电池">
            <el-progress
              :percentage="selectedDevice.battery"
              :color="getBatteryColor(selectedDevice.battery)"
              :stroke-width="10"
            />
          </el-descriptions-item>
          <el-descriptions-item label="饲料余量">
            <el-progress
              :percentage="selectedDevice.food_level"
              :color="getFoodColor(selectedDevice.food_level)"
              :stroke-width="10"
            />
          </el-descriptions-item>
          <el-descriptions-item label="网络类型">{{ selectedDevice.network }}</el-descriptions-item>
          <el-descriptions-item label="最后在线时间">{{ selectedDevice.last_online }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getDeviceList, sendDeviceCommand } from '@/api/device'
import type { Device } from '@/types'

const devices = ref<Device[]>([])
const loading = ref(false)
const detailDialogVisible = ref(false)
const selectedDevice = ref<Device | null>(null)

const loadDevices = async () => {
  loading.value = true
  try {
    devices.value = await getDeviceList()
  } catch (error) {
    console.error('Failed to load devices:', error)
  } finally {
    loading.value = false
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

const viewDetail = (device: Device) => {
  selectedDevice.value = device
  detailDialogVisible.value = true
}

const capture = async (device: Device) => {
  try {
    const result = await sendDeviceCommand(device.device_id, 'capture')
    if (result.success) {
      ElMessage.success(result.message)
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('命令发送失败')
  }
}

const restart = async (device: Device) => {
  try {
    await ElMessageBox.confirm('确定要重启该设备吗?', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const result = await sendDeviceCommand(device.device_id, 'restart')
    if (result.success) {
      ElMessage.success(result.message)
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('命令发送失败')
    }
  }
}

const openConfig = (device: Device) => {
  router.push(`/manage/config?device=${device.device_id}`)
}

import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'

const router = useRouter()

onMounted(() => {
  loadDevices()
})
</script>

<style scoped lang="scss">
.devices-page {
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
  margin-bottom: 24px;
  
  h2 {
    color: #ffffff;
    font-size: 24px;
    font-weight: 600;
    margin: 0;
  }
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .el-progress {
    flex: 1;
  }
  
  .progress-text {
    color: #ffffff;
    font-size: 13px;
    font-weight: 600;
    min-width: 40px;
  }
}

.device-detail {
  :deep(.el-descriptions__label) {
    background: rgba(0, 212, 255, 0.1) !important;
    color: #8b8ba3 !important;
  }
  
  :deep(.el-descriptions__content) {
    background: rgba(26, 26, 46, 0.5) !important;
    color: #ffffff !important;
  }
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

:deep(.el-dialog) {
  background: rgba(26, 26, 46, 0.95) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 12px;
  
  .el-dialog__title {
    color: #ffffff !important;
  }
}
</style>
