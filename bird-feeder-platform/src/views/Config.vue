<template>
  <div class="config-page">
    <div class="page-header">
      <h2>远程参数设置</h2>
    </div>

    <div class="config-content">
      <el-card class="device-select-card">
        <template #header>
          <div class="card-header">
            <span>选择设备</span>
          </div>
        </template>
        <el-select
          v-model="selectedDeviceId"
          placeholder="请选择设备"
          size="large"
          style="width: 100%"
          @change="loadConfig"
        >
          <el-option
            v-for="device in devices"
            :key="device.device_id"
            :label="`${device.name} (${device.device_id})`"
            :value="device.device_id"
          />
        </el-select>
      </el-card>

      <el-card v-if="selectedDeviceId" class="config-form-card">
        <template #header>
          <div class="card-header">
            <span>设备参数配置</span>
            <el-tag type="info">{{ selectedDeviceId }}</el-tag>
          </div>
        </template>
        
        <el-form
          :model="configForm"
          label-width="160px"
          label-position="left"
        >
          <el-form-item label="拍摄间隔">
            <el-input-number
              v-model="configForm.capture_interval"
              :min="60"
              :max="3600"
              :step="60"
            />
            <span class="form-tip">秒 (60-3600)</span>
          </el-form-item>

          <el-form-item label="识别置信度阈值">
            <el-input-number
              v-model="configForm.confidence_threshold"
              :min="0.5"
              :max="1"
              :step="0.05"
              :precision="2"
            />
            <span class="form-tip">0.5-1.0</span>
          </el-form-item>

          <el-form-item label="上传图片">
            <el-switch v-model="configForm.upload_image" />
            <span class="form-tip">开启后会将识别图片上传到服务器</span>
          </el-form-item>

          <el-form-item label="夜间模式">
            <el-switch v-model="configForm.night_mode" />
            <span class="form-tip">开启后在夜间时段降低拍摄频率</span>
          </el-form-item>

          <el-form-item label="低电量阈值">
            <el-input-number
              v-model="configForm.low_battery_threshold"
              :min="5"
              :max="50"
              :step="5"
            />
            <span class="form-tip">低于此值时设备进入节能模式 (%)</span>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" size="large" @click="saveConfig" :loading="saving">
              保存配置
            </el-button>
            <el-button size="large" @click="resetForm">
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-empty v-else description="请先选择一个设备" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getDeviceList } from '@/api/device'
import { getDeviceConfig, updateDeviceConfig } from '@/api/config'
import type { Device, DeviceConfig } from '@/types'

const route = useRoute()
const devices = ref<Device[]>([])
const selectedDeviceId = ref('')
const saving = ref(false)

const configForm = reactive({
  capture_interval: 300,
  confidence_threshold: 0.85,
  upload_image: true,
  night_mode: true,
  low_battery_threshold: 20
})

const loadDevices = async () => {
  try {
    devices.value = await getDeviceList()
    
    const deviceParam = route.query.device as string
    if (deviceParam) {
      selectedDeviceId.value = deviceParam
      await loadConfig()
    }
  } catch (error) {
    console.error('Failed to load devices:', error)
  }
}

const loadConfig = async () => {
  if (!selectedDeviceId.value) return
  
  try {
    const config = await getDeviceConfig(selectedDeviceId.value)
    Object.assign(configForm, {
      capture_interval: config.capture_interval,
      confidence_threshold: config.confidence_threshold,
      upload_image: config.upload_image,
      night_mode: config.night_mode,
      low_battery_threshold: config.low_battery_threshold
    })
  } catch (error) {
    console.error('Failed to load config:', error)
    ElMessage.error('加载配置失败')
  }
}

const saveConfig = async () => {
  if (!selectedDeviceId.value) return
  
  saving.value = true
  try {
    const result = await updateDeviceConfig(selectedDeviceId.value, configForm)
    if (result.success) {
      ElMessage.success(result.message)
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    console.error('Failed to save config:', error)
    ElMessage.error('保存配置失败')
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  configForm.capture_interval = 300
  configForm.confidence_threshold = 0.85
  configForm.upload_image = true
  configForm.night_mode = true
  configForm.low_battery_threshold = 20
}

onMounted(() => {
  loadDevices()
})
</script>

<style scoped lang="scss">
.config-page {
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

.config-content {
  max-width: 800px;
}

.device-select-card {
  margin-bottom: 20px;
}

.config-form-card {
  :deep(.el-card__header) {
    background: rgba(0, 212, 255, 0.1) !important;
    border-bottom: 1px solid rgba(0, 212, 255, 0.2);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  span {
    color: #ffffff;
    font-size: 16px;
    font-weight: 600;
  }
}

.form-tip {
  margin-left: 12px;
  color: #8b8ba3;
  font-size: 12px;
}

:deep(.el-card) {
  background: rgba(26, 26, 46, 0.8) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 12px;
}

:deep(.el-form-item__label) {
  color: #8b8ba3 !important;
}

:deep(.el-input__wrapper) {
  background: rgba(26, 26, 46, 0.8) !important;
  border: 1px solid rgba(0, 212, 255, 0.2) !important;
  box-shadow: none !important;
  
  .el-input__inner {
    color: #ffffff !important;
  }
}

:deep(.el-select) {
  .el-input__wrapper {
    background: rgba(26, 26, 46, 0.8) !important;
  }
}
</style>
