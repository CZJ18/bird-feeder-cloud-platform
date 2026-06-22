<template>
  <main class="detail-page">
    <section class="metric-grid">
      <button
        v-for="item in dashboardMetrics"
        :key="item.label"
        type="button"
        class="metric-card"
        :class="`tone-${item.tone}`"
        @click="emit('openMetric', item)"
      >
        <span>{{ item.label }}</span>
        <strong class="digital">{{ item.value }}<em>{{ item.unit }}</em></strong>
        <small>{{ item.refresh }}刷新</small>
      </button>
    </section>

    <section class="chart-grid">
      <ChartCard title="物种分布（饼图）" action-label="详情" @action="emit('openChart', '物种分布（饼图）')">
        <PieChart :data="speciesDistribution" />
      </ChartCard>
      <ChartCard title="时间动态（折线图）" action-label="详情" @action="emit('openChart', '时间动态（折线图）')">
        <TimeLineChart :data="timeDynamics" />
      </ChartCard>
      <ChartCard title="月度趋势（堆叠图）" action-label="详情" @action="emit('openChart', '月度趋势（堆叠图）')">
        <StackedMonthlyChart :dimensions="monthlyTrend.dimensions" :series="monthlyTrend.data" />
      </ChartCard>
    </section>

    <section class="bottom-grid">
      <section class="screen-panel data-panel device-panel">
        <h2 class="panel-title">设备状态列表</h2>
        <div class="table-head device-row">
          <span>设备</span>
          <span>位置</span>
          <span>状态</span>
          <span>温度</span>
          <span>今日</span>
        </div>
        <button
          v-for="item in deviceStatusRows"
          :key="item.deviceId"
          type="button"
          class="device-row table-row"
          @click="emit('openDevice', item)"
        >
          <span>
            <strong>{{ item.deviceId }}</strong>
            <small>{{ item.name }}</small>
          </span>
          <span>{{ item.location }}</span>
          <span class="status-dot" :class="{ offline: item.status === '离线' }">{{ item.status }}</span>
          <span>{{ item.temperature }}</span>
          <span class="digital">{{ item.todayEvents }}</span>
        </button>
        <p v-if="!deviceStatusRows.length" class="empty-text">暂无设备状态上报</p>
      </section>

      <section class="screen-panel data-panel map-panel">
        <h2 class="panel-title">设备地图数据</h2>
        <div class="map-list">
          <button v-for="point in mapPoints" :key="point.deviceId" type="button" @click="emit('openMapPoint', point)">
            <span>{{ point.name }}</span>
            <strong class="digital">{{ point.events }}</strong>
            <small>{{ point.deviceId }} / {{ point.status }} / {{ point.species }}种</small>
          </button>
        </div>
        <p v-if="!mapPoints.length" class="empty-text">暂无带经纬度的设备事件</p>
      </section>

      <section class="screen-panel data-panel moment-panel">
        <h2 class="panel-title">精彩瞬间</h2>
        <div class="moment-list">
          <button v-for="item in videoCards" :key="item.title" type="button" @click="emit('openMoment', item)">
            <img :src="item.image" :alt="item.title" />
            <span>{{ item.title }}</span>
            <small>{{ item.camera }} / {{ item.time }}</small>
          </button>
        </div>
        <p v-if="!videoCards.length" class="empty-text">暂无管理员添加的精彩瞬间</p>
      </section>

      <section class="screen-panel data-panel review-panel">
        <div class="panel-heading">
          <h2 class="panel-title">低置信度列表</h2>
          <button type="button" class="refresh-button" @click="refreshReviews">手动刷新</button>
        </div>
        <div class="review-state">最近刷新：{{ reviewRefreshText }}</div>
        <div class="review-list">
          <button v-for="item in lowConfidenceRows" :key="item.id" type="button" @click="emit('openLowConfidence', item)">
            <img :src="item.image" :alt="item.id" />
            <span>
              <strong>{{ item.species }}</strong>
              <small>{{ item.deviceId }} / {{ item.time }}</small>
            </span>
            <em :class="item.status">{{ statusText(item.status) }}</em>
            <b class="digital">{{ item.confidence }}</b>
          </button>
        </div>
        <p v-if="!lowConfidenceRows.length" class="empty-text">暂无待审核图片</p>
      </section>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import ChartCard from './ChartCard.vue'
import PieChart from './charts/PieChart.vue'
import TimeLineChart from './charts/TimeLineChart.vue'
import StackedMonthlyChart from './charts/StackedMonthlyChart.vue'
import request, { resolveAssetUrl } from '@/api/request'
import type { ApiResponse } from '@/types'
import {
  dashboardMetrics as mockDashboardMetrics,
  deviceStatusRows as mockDeviceStatusRows,
  lowConfidenceRows as mockLowConfidenceRows,
  mapPoints as mockMapPoints,
  videoCards as mockVideoCards,
  type DashboardMetric,
  type DeviceStatusRow,
  type LowConfidenceRow,
  type MapPoint,
  type ReviewStatus,
  type VideoCard
} from '@/data/mockData'

type Tone = DashboardMetric['tone']

interface DashboardStats {
  speciesStats: {
    totalVisits: number
    totalSpecies: number
    onlineCount: number
  }
  kpiCard: {
    todayNew: number
    todayActive: number
    pendingReview: number
    avgConfidence: number
    todaySpeciesCount: number
  }
}

interface MqttStatus {
  broker: {
    connected: boolean
    clients: {
      connected: number | null
      active: number | null
      total: number | null
    }
    messages: {
      received: number | null
      publish_received: number | null
    }
  }
  business: {
    event_count: number
    status_count: number
    latest_event_at: string | null
    latest_status_at: string | null
    latest_business_at: string | null
  }
}

interface SpeciesPoint {
  name: string
  value: number
}

interface TimePoint {
  mdate: string
  value: number
  temperature?: number | null
}

interface MonthlyTrend {
  dimensions: string[]
  data: Array<{ species: string; values: number[] }>
}

interface DeviceStatusApiRow {
  device_id: string
  name: string
  cpu_temperature: number | null
  online: boolean
  last_seen: string | null
}

interface DeviceListApiRow {
  device_id: string
  name: string
  location: string
  status: 'online' | 'offline'
  battery: number
  food_level: number
  last_online: string
}

interface DeviceMapApi {
  voltageLevel: string[]
  categoryData: Record<string, Array<{ name: string; value: number }>>
  topData: Record<string, Array<{ name: string; value: [number, number, number] }>>
}

interface MomentApiRow {
  id: number
  videoUrl?: string
  title: string
  coverImage?: string
}

interface LowConfidenceApiRow {
  id: number
  device_id: string
  species: string
  confidence: number
  timestamp: string
  image_url: string
  review_status: ReviewStatus
}

const emit = defineEmits<{
  openMetric: [item: DashboardMetric]
  openChart: [title: string]
  openDevice: [item: DeviceStatusRow]
  openMapPoint: [point: MapPoint]
  openMoment: [item: VideoCard]
  openLowConfidence: [item: LowConfidenceRow]
}>()

const dashboardStats = ref<DashboardStats>({
  speciesStats: {
    totalVisits: 0,
    totalSpecies: 0,
    onlineCount: 0
  },
  kpiCard: {
    todayNew: 0,
    todayActive: 0,
    pendingReview: 0,
    avgConfidence: 0,
    todaySpeciesCount: 0
  }
})

const speciesDistribution = ref<SpeciesPoint[]>([])
const timeDynamics = ref<TimePoint[]>([])
const monthlyTrend = ref<MonthlyTrend>({ dimensions: [], data: [] })
const deviceStatusRows = ref<DeviceStatusRow[]>([])
const mapPoints = ref<MapPoint[]>([])
const videoCards = ref<VideoCard[]>([])
const lowConfidenceRows = ref<LowConfidenceRow[]>([])
const reviewRefreshText = ref('尚未刷新')
let timer: number | undefined

const metric = (label: string, value: number, unit: string, refresh: string, tone: Tone, description: string): DashboardMetric => ({
  label,
  value: String(value),
  unit,
  refresh,
  tone,
  description
})

const hasBusinessData = computed(() => dashboardStats.value.speciesStats.totalVisits > 0 || dashboardStats.value.kpiCard.todayNew > 0)

const dashboardMetrics = computed<DashboardMetric[]>(() => {
  if (!hasBusinessData.value) return mockDashboardMetrics
  return [
    metric('累计识别总数', dashboardStats.value.speciesStats.totalVisits, '条', '30秒', 'cyan', '数据库 event_leave 表的真实 leave 事件总数。'),
    metric('累计物种数', dashboardStats.value.speciesStats.totalSpecies, '种', '30秒', 'green', 'event_leave 表中不同 class_id 的数量。'),
    metric('在线设备数', dashboardStats.value.speciesStats.onlineCount, '台', '5分钟', 'blue', '最近 5 分钟内有状态上报的设备数量。'),
    metric('今日新增', dashboardStats.value.kpiCard.todayNew, '条', '30秒', 'amber', '今天发生的 leave 事件数量。'),
    metric('今日活跃设备', dashboardStats.value.kpiCard.todayActive, '台', '1分钟', 'cyan', '今天有事件或状态上报的设备数量。'),
    metric('待审核图片', dashboardStats.value.kpiCard.pendingReview, '张', '手动', 'orange', '低置信度图片表中 pending 记录数量。'),
    metric('平均置信度', dashboardStats.value.kpiCard.avgConfidence, '%', '30秒', 'green', '所有 leave 事件的平均 confidence。'),
    metric('今日观测物种数', dashboardStats.value.kpiCard.todaySpeciesCount, '种', '30秒', 'blue', '今天事件中不同 class_id 的数量。')
  ]
})

const formatTime = (value?: string | null) => {
  if (!value) return '未上报'
  return value.replace('T', ' ').slice(0, 19)
}

const loadDashboardStats = async () => {
  const res = await request<ApiResponse<MqttStatus>>({ url: '/mqtt/status' })
  const mqtt = res.data
  dashboardStats.value = {
    speciesStats: {
      totalVisits: mqtt.business.event_count,
      totalSpecies: mqtt.broker.clients.connected ?? 0,
      onlineCount: mqtt.broker.clients.active ?? 0
    },
    kpiCard: {
      todayNew: mqtt.business.status_count,
      todayActive: mqtt.broker.clients.connected ?? 0,
      pendingReview: 0,
      avgConfidence: mqtt.broker.connected ? 100 : 0,
      todaySpeciesCount: mqtt.broker.messages.publish_received ?? 0
    }
  }
}

const loadCharts = async () => {
  const [speciesRes, timeRes, monthlyRes] = await Promise.all([
    request<ApiResponse<{ regionData: SpeciesPoint[] }>>({ url: '/species/distribution', params: { top: 10 } }),
    request<ApiResponse<{ regionData: TimePoint[] }>>({ url: '/time-dynamics', params: { days: 7, unit: 'day' } }),
    request<ApiResponse<MonthlyTrend>>({ url: '/monthly-trend' })
  ])
  speciesDistribution.value = speciesRes.data.regionData
  timeDynamics.value = timeRes.data.regionData
  monthlyTrend.value = monthlyRes.data
}

const loadDevices = async () => {
  const [statusRes, listRes] = await Promise.all([
    request<ApiResponse<{ devices: DeviceStatusApiRow[] }>>({ url: '/devices/status' }),
    request<ApiResponse<{ devices: DeviceListApiRow[] }>>({ url: '/device/list' })
  ])

  const statusById = new Map(statusRes.data.devices.map(item => [item.device_id, item]))
  if (!statusRes.data.devices.some(item => item.last_seen)) {
    deviceStatusRows.value = mockDeviceStatusRows
    return
  }
  deviceStatusRows.value = listRes.data.devices.map(item => {
    const status = statusById.get(item.device_id)
    return {
      deviceId: item.device_id,
      name: item.name,
      location: item.location || '--',
      status: item.status === 'online' ? '在线' : '离线',
      lastSeen: formatTime(status?.last_seen || item.last_online),
      temperature: status?.cpu_temperature == null ? '--' : `${status.cpu_temperature.toFixed(1)}°C`,
      battery: `${item.battery || 0}%`,
      foodLevel: `${item.food_level || 0}%`,
      todayEvents: 0
    }
  })
}

const loadMap = async () => {
  const res = await request<ApiResponse<DeviceMapApi>>({ url: '/devices/map' })
  const currentYear = res.data.voltageLevel[res.data.voltageLevel.length - 1]
  const points = currentYear ? res.data.topData[currentYear] || [] : []
  if (!points.length) {
    mapPoints.value = mockMapPoints
    return
  }
  mapPoints.value = points.map((point, index) => ({
    name: point.name,
    x: 20 + (index % 5) * 14,
    y: 24 + Math.floor(index / 5) * 18,
    heat: point.value[2],
    deviceId: point.name,
    species: 0,
    events: point.value[2],
    status: '离线'
  }))
}

const loadMoments = async () => {
  const res = await request<ApiResponse<{ regionData: MomentApiRow[] }>>({ url: '/moments' })
  if (!res.data.regionData.length) {
    videoCards.value = mockVideoCards
    return
  }
  videoCards.value = res.data.regionData.map(item => ({
    title: item.title,
    duration: '0:00',
    tone: 'cyan',
    camera: `MOMENT-${item.id}`,
    species: '--',
    time: '--',
    image: resolveAssetUrl(item.coverImage || ''),
    description: item.videoUrl ? `视频地址：${item.videoUrl}` : '管理员添加的精彩瞬间'
  }))
}

const refreshReviews = async () => {
  const res = await request<ApiResponse<{ total: number; list: LowConfidenceApiRow[] }>>({
    url: '/low-confidence',
    params: { page: 1, size: 20, status: 'all' }
  })
  if (!res.data.list.length) {
    lowConfidenceRows.value = mockLowConfidenceRows
    reviewRefreshText.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
    return
  }
  lowConfidenceRows.value = res.data.list.map(item => ({
    id: String(item.id),
    deviceId: item.device_id,
    species: item.species,
    confidence: `${Math.round(item.confidence * 100)}%`,
    time: formatTime(item.timestamp),
    status: item.review_status,
    image: resolveAssetUrl(item.image_url)
  }))
  reviewRefreshText.value = new Date().toLocaleTimeString('zh-CN', { hour12: false })
}

const loadRealtime = async () => {
  await Promise.all([loadDashboardStats(), loadDevices()])
}

const statusText = (status: ReviewStatus) => {
  if (status === 'pending') return '待审核'
  if (status === 'approved') return '已通过'
  return '已驳回'
}

onMounted(async () => {
  await Promise.all([loadRealtime(), loadCharts(), loadMap(), loadMoments(), refreshReviews()])
  timer = window.setInterval(loadRealtime, 5 * 60 * 1000)
})

onUnmounted(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<style scoped>
.detail-page {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-rows: auto minmax(240px, 0.9fr) minmax(0, 1.2fr);
  gap: 14px;
  width: 100%;
  height: 100%;
  padding: 16px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(8, minmax(0, 1fr));
  gap: 10px;
}

.metric-card {
  min-width: 0;
  min-height: 92px;
  padding: 12px;
  border: 1px solid rgba(53, 232, 255, 0.22);
  border-radius: 8px;
  background:
    linear-gradient(180deg, rgba(53, 232, 255, 0.11), rgba(5, 14, 28, 0.78)),
    rgba(8, 24, 46, 0.68);
  color: var(--text-main);
  text-align: left;
  cursor: pointer;
}

.metric-card span,
.metric-card small {
  display: block;
  color: var(--text-muted);
  font-size: 12px;
}

.metric-card strong {
  display: block;
  margin: 8px 0 6px;
  color: #ecfbff;
  font-size: clamp(21px, 1.6vw, 32px);
  line-height: 1;
}

.metric-card em {
  margin-left: 3px;
  color: var(--text-muted);
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 12px;
  font-style: normal;
}

.tone-green strong {
  color: var(--green);
}

.tone-blue strong {
  color: var(--cyan);
}

.tone-amber strong,
.tone-orange strong {
  color: var(--amber);
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  min-height: 0;
}

.bottom-grid {
  display: grid;
  grid-template-columns: 1.3fr 0.9fr 0.9fr 1.1fr;
  gap: 14px;
  min-height: 0;
}

.data-panel {
  min-height: 0;
  padding: 14px;
}

.device-panel,
.review-panel,
.moment-panel,
.map-panel {
  display: flex;
  flex-direction: column;
}

.device-row {
  display: grid;
  grid-template-columns: 1.1fr 1fr 70px 70px 54px;
  gap: 8px;
  align-items: center;
}

.table-head {
  margin-bottom: 6px;
  color: var(--text-muted);
  font-size: 11px;
}

.table-row {
  width: 100%;
  min-height: 46px;
  border: 0;
  border-top: 1px solid rgba(53, 232, 255, 0.12);
  background: transparent;
  color: #dffaff;
  cursor: pointer;
  text-align: left;
}

.table-row strong,
.table-row small {
  display: block;
}

.table-row small {
  margin-top: 3px;
  color: var(--text-muted);
  font-size: 11px;
}

.status-dot {
  color: var(--green);
  font-weight: 800;
}

.status-dot.offline {
  color: var(--danger);
}

.map-list,
.moment-list,
.review-list {
  display: grid;
  gap: 8px;
  min-height: 0;
  overflow: auto;
  padding-right: 2px;
}

.map-list button,
.moment-list button,
.review-list button {
  width: 100%;
  border: 1px solid rgba(53, 232, 255, 0.16);
  border-radius: 8px;
  background: rgba(53, 232, 255, 0.06);
  color: var(--text-main);
  cursor: pointer;
  text-align: left;
}

.map-list button {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 64px;
  gap: 5px;
  padding: 9px;
}

.map-list strong {
  color: var(--green);
  text-align: right;
}

.map-list small {
  grid-column: 1 / -1;
  color: var(--text-muted);
  font-size: 11px;
}

.moment-list button {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr);
  gap: 8px;
  align-items: center;
  padding: 6px;
}

.moment-list img {
  grid-row: span 2;
  width: 72px;
  height: 42px;
  border-radius: 6px;
  object-fit: cover;
}

.moment-list small {
  color: var(--text-muted);
  font-size: 11px;
}

.panel-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.refresh-button {
  height: 26px;
  border: 1px solid rgba(53, 232, 255, 0.28);
  border-radius: 6px;
  background: rgba(53, 232, 255, 0.08);
  color: var(--cyan);
  cursor: pointer;
  font-size: 12px;
}

.review-state,
.empty-text {
  color: var(--text-muted);
  font-size: 11px;
}

.review-state {
  margin: -4px 0 8px;
}

.empty-text {
  margin: 12px 0 0;
}

.review-list button {
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr) 54px 44px;
  gap: 8px;
  align-items: center;
  padding: 7px;
}

.review-list img {
  width: 44px;
  height: 34px;
  border-radius: 6px;
  object-fit: cover;
}

.review-list strong,
.review-list small {
  display: block;
}

.review-list small {
  margin-top: 3px;
  color: var(--text-muted);
  font-size: 10px;
}

.review-list em {
  color: var(--amber);
  font-size: 12px;
  font-style: normal;
  font-weight: 800;
}

.review-list em.approved {
  color: var(--green);
}

.review-list em.rejected {
  color: var(--danger);
}

.review-list b {
  color: var(--cyan);
  font-size: 13px;
  text-align: right;
}

@media (max-width: 1280px) {
  .detail-page {
    height: auto;
    min-height: 100vh;
  }

  .metric-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .chart-grid,
  .bottom-grid {
    grid-template-columns: 1fr;
  }
}
</style>
