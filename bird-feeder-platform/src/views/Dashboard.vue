<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <StatCard
          label="设备总数"
          :value="statistics.total_devices"
          :icon="Monitor"
          color="#00d4ff"
        />
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <StatCard
          label="在线设备"
          :value="statistics.online_devices"
          :icon="Connection"
          color="#00ff88"
        />
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <StatCard
          label="今日识别"
          :value="statistics.today_recognitions"
          :icon="Camera"
          color="#ffb800"
        />
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <StatCard
          label="今日上传"
          :value="statistics.today_images"
          :icon="Picture"
          color="#ff4757"
        />
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :lg="16">
        <div class="chart-card">
          <div class="chart-header">
            <h3>识别次数趋势</h3>
          </div>
          <div ref="lineChartRef" class="chart-container"></div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="8">
        <div class="chart-card">
          <div class="chart-header">
            <h3>鸟类占比</h3>
          </div>
          <div ref="pieChartRef" class="chart-container"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="info-row">
      <el-col :xs="24" :lg="12">
        <div class="events-card">
          <div class="card-header">
            <h3>最近识别结果</h3>
            <el-button type="primary" text @click="$router.push('/events')">
              查看更多 <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
          <div class="events-list">
            <div v-for="event in recentEvents" :key="event.id" class="event-item">
              <el-image 
                :src="event.image_url" 
                :preview-src-list="[event.image_url]"
                fit="cover"
                class="event-image"
              >
                <template #error>
                  <div class="image-error">
                    <el-icon><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
              <div class="event-info">
                <div class="event-name">{{ event.bird_name }}</div>
                <div class="event-detail">
                  <span>{{ event.device_id }}</span>
                  <span>{{ event.created_at }}</span>
                </div>
              </div>
              <div class="event-confidence">
                {{ (event.confidence * 100).toFixed(0) }}%
              </div>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="devices-card">
          <div class="card-header">
            <h3>设备状态</h3>
            <el-button type="primary" text @click="$router.push('/devices')">
              管理设备 <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
          <div class="devices-grid">
            <DeviceStatusCard
              v-for="device in devices"
              :key="device.device_id"
              :device="device"
            />
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { Monitor, Connection, Camera, Picture, ArrowRight } from '@element-plus/icons-vue'
import StatCard from '@/components/StatCard.vue'
import DeviceStatusCard from '@/components/DeviceStatusCard.vue'
import { getStatistics } from '@/api/statistics'
import { getDeviceList } from '@/api/device'
import { getBirdEvents } from '@/api/bird'
import { getDailyRecognitions, getBirdDistribution } from '@/api/statistics'
import type { Statistics, Device, BirdEvent, DailyRecognition, BirdDistribution } from '@/types'

const statistics = ref<Statistics>({
  total_devices: 0,
  online_devices: 0,
  today_recognitions: 0,
  today_images: 0,
  total_bird_species: 0,
  average_confidence: 0
})

const devices = ref<Device[]>([])
const recentEvents = ref<BirdEvent[]>([])
const lineChartRef = ref<HTMLDivElement>()
const pieChartRef = ref<HTMLDivElement>()

let lineChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null

const loadData = async () => {
  try {
    statistics.value = await getStatistics()
    devices.value = await getDeviceList()
    recentEvents.value = await getBirdEvents({ limit: 6 })
    
    const dailyData = await getDailyRecognitions(14)
    const birdDist = await getBirdDistribution()
    
    renderLineChart(dailyData)
    renderPieChart(birdDist)
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
}

const renderLineChart = (data: DailyRecognition[]) => {
  if (!lineChartRef.value) return
  
  if (lineChart) {
    lineChart.dispose()
  }
  
  lineChart = echarts.init(lineChartRef.value)
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(26, 26, 46, 0.95)',
      borderColor: '#00d4ff',
      textStyle: { color: '#ffffff' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.map(d => d.date.slice(5)),
      axisLine: { lineStyle: { color: '#333' } },
      axisLabel: { color: '#8b8ba3' }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#333' } },
      axisLabel: { color: '#8b8ba3' },
      splitLine: { lineStyle: { color: 'rgba(0, 212, 255, 0.1)' } }
    },
    series: [
      {
        name: '识别次数',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: {
          color: '#00d4ff',
          width: 3
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 212, 255, 0.3)' },
            { offset: 1, color: 'rgba(0, 212, 255, 0.05)' }
          ])
        },
        itemStyle: { color: '#00d4ff' },
        data: data.map(d => d.count)
      }
    ]
  }
  
  lineChart.setOption(option)
}

const renderPieChart = (data: BirdDistribution[]) => {
  if (!pieChartRef.value) return
  
  if (pieChart) {
    pieChart.dispose()
  }
  
  pieChart = echarts.init(pieChartRef.value)
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(26, 26, 46, 0.95)',
      borderColor: '#00d4ff',
      textStyle: { color: '#ffffff' }
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: { color: '#8b8ba3' }
    },
    series: [
      {
        name: '鸟类占比',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#1a1a2e',
          borderWidth: 2
        },
        label: { show: false },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
            color: '#ffffff'
          }
        },
        labelLine: { show: false },
        data: data.map((d, i) => ({
          value: d.value,
          name: d.name,
          itemStyle: {
            color: ['#00d4ff', '#00ff88', '#ffb800', '#ff4757', '#9C27B0', '#795548', '#607D8B'][i]
          }
        }))
      }
    ]
  }
  
  pieChart.setOption(option)
}

const handleResize = () => {
  lineChart?.resize()
  pieChart?.resize()
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  lineChart?.dispose()
  pieChart?.dispose()
})
</script>

<style scoped lang="scss">
.dashboard {
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

.stats-row {
  margin-bottom: 20px;
}

.charts-row {
  margin-bottom: 20px;
}

.info-row {
  margin-bottom: 20px;
}

.chart-card {
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 12px;
  padding: 20px;
  height: 100%;
}

.chart-header {
  margin-bottom: 16px;
  
  h3 {
    color: #ffffff;
    font-size: 16px;
    font-weight: 600;
    margin: 0;
  }
}

.chart-container {
  width: 100%;
  height: 300px;
}

.events-card,
.devices-card {
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 12px;
  padding: 20px;
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  
  h3 {
    color: #ffffff;
    font-size: 16px;
    font-weight: 600;
    margin: 0;
  }
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.event-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(0, 212, 255, 0.05);
  border-radius: 8px;
  transition: all 0.3s;
  
  &:hover {
    background: rgba(0, 212, 255, 0.1);
  }
}

.event-image {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  
  .image-error {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #333;
    color: #8b8ba3;
  }
}

.event-info {
  flex: 1;
  
  .event-name {
    color: #ffffff;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 4px;
  }
  
  .event-detail {
    display: flex;
    gap: 12px;
    color: #8b8ba3;
    font-size: 12px;
  }
}

.event-confidence {
  color: #00ff88;
  font-size: 16px;
  font-weight: 700;
  padding: 4px 12px;
  background: rgba(0, 255, 136, 0.1);
  border-radius: 6px;
}

.devices-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}
</style>
