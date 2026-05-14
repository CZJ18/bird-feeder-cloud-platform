<template>
  <div class="logs-page">
    <div class="page-header">
      <h2>系统日志</h2>
    </div>

    <div class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="设备">
          <el-select v-model="filterForm.device_id" placeholder="选择设备" clearable>
            <el-option
              v-for="device in devices"
              :key="device.device_id"
              :label="device.name"
              :value="device.device_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="日志类型">
          <el-select v-model="filterForm.type" placeholder="选择类型" clearable>
            <el-option label="INFO" value="INFO" />
            <el-option label="WARNING" value="WARNING" />
            <el-option label="ERROR" value="ERROR" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-table
      :data="logs"
      stripe
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="device_id" label="设备ID" width="120" />
      <el-table-column label="类型" width="120">
        <template #default="{ row }">
          <el-tag :type="getLogType(row.type)" size="small">
            {{ row.type }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="message" label="消息内容" min-width="400" />
      <el-table-column prop="created_at" label="时间" width="180" />
    </el-table>

    <el-pagination
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.page_size"
      :page-sizes="[20, 50, 100]"
      :total="pagination.total"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handlePageChange"
      style="margin-top: 20px; justify-content: center;"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getLogs } from '@/api/logs'
import { getDeviceList } from '@/api/device'
import type { SystemLog, Device } from '@/types'

const logs = ref<SystemLog[]>([])
const devices = ref<Device[]>([])
const loading = ref(false)

const filterForm = reactive({
  device_id: '',
  type: '' as 'INFO' | 'WARNING' | 'ERROR' | ''
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const loadLogs = async () => {
  loading.value = true
  try {
    const result = await getLogs({
      device_id: filterForm.device_id || undefined,
      type: filterForm.type || undefined,
      page: pagination.page,
      page_size: pagination.page_size
    })
    logs.value = result.items
    pagination.total = result.total
  } catch (error) {
    console.error('Failed to load logs:', error)
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

const handleSearch = () => {
  pagination.page = 1
  loadLogs()
}

const handleReset = () => {
  filterForm.device_id = ''
  filterForm.type = ''
  pagination.page = 1
  loadLogs()
}

const handleSizeChange = () => {
  pagination.page = 1
  loadLogs()
}

const handlePageChange = () => {
  loadLogs()
}

const getLogType = (type: string) => {
  switch (type) {
    case 'INFO':
      return 'info'
    case 'WARNING':
      return 'warning'
    case 'ERROR':
      return 'danger'
    default:
      return 'info'
  }
}

onMounted(() => {
  loadLogs()
  loadDevices()
})
</script>

<style scoped lang="scss">
.logs-page {
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

.filter-card {
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
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

:deep(.el-pagination) {
  .el-pagination__total {
    color: #8b8ba3;
  }
  
  .el-pager li {
    background: rgba(26, 26, 46, 0.8) !important;
    color: #8b8ba3 !important;
    
    &.is-active {
      background: rgba(0, 212, 255, 0.2) !important;
      color: #00d4ff !important;
    }
  }
}
</style>
