<template>
  <div class="history-page">
    <div class="page-header">
      <h2>历史识别结果</h2>
    </div>

    <div class="stats-cards">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :lg="6">
          <StatCard
            label="历史识别总数"
            :value="stats.total_recognitions"
            :icon="Document"
            color="#00d4ff"
          />
        </el-col>
        <el-col :xs="24" :sm="12" :lg="6">
          <StatCard
            label="鸟类种类数"
            :value="stats.bird_species"
            :icon="Collection"
            color="#00ff88"
          />
        </el-col>
        <el-col :xs="24" :sm="12" :lg="6">
          <StatCard
            label="今日识别数"
            :value="stats.today_recognitions"
            :icon="Calendar"
            color="#ffb800"
          />
        </el-col>
        <el-col :xs="24" :sm="12" :lg="6">
          <StatCard
            label="平均置信度"
            :value="(stats.avg_confidence * 100).toFixed(1)"
            :icon="DataLine"
            color="#ff4757"
            suffix="%"
          />
        </el-col>
      </el-row>
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
        <el-form-item label="鸟类">
          <el-input v-model="filterForm.bird_name" placeholder="输入鸟类名称" clearable />
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="handleDateChange"
          />
        </el-form-item>
        <el-form-item label="置信度">
          <el-input-number
            v-model="filterForm.min_confidence"
            :min="0"
            :max="1"
            :step="0.1"
            placeholder="最小"
            style="width: 100px"
          />
          <span style="color: #8b8ba3; margin: 0 8px;">-</span>
          <el-input-number
            v-model="filterForm.max_confidence"
            :min="0"
            :max="1"
            :step="0.1"
            placeholder="最大"
            style="width: 100px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button type="success" @click="handleExport">导出CSV</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-table
      :data="records"
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
      <el-table-column prop="location" label="位置" min-width="150" />
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
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="viewDetail(row)">
            详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.page_size"
      :page-sizes="[10, 20, 50, 100]"
      :total="pagination.total"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handlePageChange"
      style="margin-top: 20px; justify-content: center;"
    />

    <el-dialog v-model="detailDialogVisible" title="识别详情" width="700px">
      <div v-if="selectedRecord" class="detail-content">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-image
              :src="selectedRecord.image_url"
              :preview-src-list="[selectedRecord.image_url]"
              fit="cover"
              style="width: 100%; height: 300px; border-radius: 12px;"
            />
          </el-col>
          <el-col :span="12">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="记录ID">{{ selectedRecord.id }}</el-descriptions-item>
              <el-descriptions-item label="设备ID">{{ selectedRecord.device_id }}</el-descriptions-item>
              <el-descriptions-item label="鸟类名称">{{ selectedRecord.bird_name }}</el-descriptions-item>
              <el-descriptions-item label="识别置信度">
                <el-tag type="success">{{ (selectedRecord.confidence * 100).toFixed(1) }}%</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="位置">{{ selectedRecord.location }}</el-descriptions-item>
              <el-descriptions-item label="电池">{{ selectedRecord.battery }}%</el-descriptions-item>
              <el-descriptions-item label="饲料余量">{{ selectedRecord.food_level }}%</el-descriptions-item>
              <el-descriptions-item label="识别时间">{{ selectedRecord.created_at }}</el-descriptions-item>
            </el-descriptions>
          </el-col>
        </el-row>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Document, Collection, Calendar, DataLine, Picture } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import StatCard from '@/components/StatCard.vue'
import { getHistoryRecords, exportHistoryCSV } from '@/api/history'
import { getDeviceList } from '@/api/device'
import type { HistoryRecord, Device, FilterParams } from '@/types'

const records = ref<HistoryRecord[]>([])
const devices = ref<Device[]>([])
const loading = ref(false)
const detailDialogVisible = ref(false)
const selectedRecord = ref<HistoryRecord | null>(null)
const dateRange = ref<[string, string] | null>(null)

const stats = ref({
  total_recognitions: 0,
  bird_species: 0,
  today_recognitions: 0,
  avg_confidence: 0
})

const filterForm = reactive<FilterParams>({
  device_id: '',
  bird_name: '',
  min_confidence: undefined,
  max_confidence: undefined
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const loadRecords = async () => {
  loading.value = true
  try {
    const params: FilterParams = {
      ...filterForm,
      page: pagination.page,
      page_size: pagination.page_size
    }
    
    const result = await getHistoryRecords(params)
    records.value = result.items
    pagination.total = result.total
    
    stats.value = {
      total_recognitions: result.total,
      bird_species: new Set(result.items.map(r => r.bird_name)).size,
      today_recognitions: result.items.filter(r => {
        const today = new Date().toISOString().split('T')[0]
        return r.created_at.startsWith(today)
      }).length,
      avg_confidence: result.items.length > 0
        ? result.items.reduce((sum, r) => sum + r.confidence, 0) / result.items.length
        : 0
    }
  } catch (error) {
    console.error('Failed to load records:', error)
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

const handleDateChange = (val: [string, string] | null) => {
  if (val) {
    filterForm.start_date = val[0]
    filterForm.end_date = val[1]
  } else {
    filterForm.start_date = undefined
    filterForm.end_date = undefined
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadRecords()
}

const handleReset = () => {
  filterForm.device_id = ''
  filterForm.bird_name = ''
  filterForm.min_confidence = undefined
  filterForm.max_confidence = undefined
  filterForm.start_date = undefined
  filterForm.end_date = undefined
  dateRange.value = null
  pagination.page = 1
  loadRecords()
}

const handleSizeChange = () => {
  pagination.page = 1
  loadRecords()
}

const handlePageChange = () => {
  loadRecords()
}

const handleExport = async () => {
  try {
    const url = await exportHistoryCSV(filterForm)
    const link = document.createElement('a')
    link.href = url
    link.download = `bird-history-${Date.now()}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const viewDetail = (record: HistoryRecord) => {
  selectedRecord.value = record
  detailDialogVisible.value = true
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
  loadRecords()
  loadDevices()
})
</script>

<style scoped lang="scss">
.history-page {
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

.stats-cards {
  margin-bottom: 20px;
}

.filter-card {
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
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

:deep(.el-dialog) {
  background: rgba(26, 26, 46, 0.95) !important;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 12px;
  
  .el-dialog__title {
    color: #ffffff !important;
  }
}

:deep(.el-descriptions__label) {
  background: rgba(0, 212, 255, 0.1) !important;
  color: #8b8ba3 !important;
}

:deep(.el-descriptions__content) {
  background: rgba(26, 26, 46, 0.5) !important;
  color: #ffffff !important;
}
</style>
