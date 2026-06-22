<template>
  <main class="center-dashboard">
    <section class="hero-kpi">
      <button type="button" class="kpi-orbit" @click="emit('selectCore')">
        <div class="kpi-core">
          <strong class="digital">{{ totalVisits }}</strong>
          <span>真实 MQTT leave 事件 / 条记录</span>
        </div>
      </button>
      <div class="protection-ring">
        <button v-for="item in ringStats" :key="item.label" type="button" @click="emit('selectProtection', item)">
          <span>{{ item.label }}</span>
          <strong class="digital">{{ item.value }}</strong>
        </button>
      </div>
    </section>

    <section class="screen-panel main-stat-panel">
      <h2 class="panel-title">年度设备事件统计</h2>
      <div class="main-stat-grid">
        <div class="map-wrap">
          <CampusMap @select="emit('selectMapPoint', $event)" />
          <YearTimeline @select="emit('selectYear', $event)" />
        </div>
        <div class="bar-wrap">
          <div class="sub-title">当前年度各设备事件量</div>
          <BarChart />
        </div>
      </div>
    </section>

    <section class="video-section">
      <VideoCards @open="emit('openMedia', $event)" />
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import request from '@/api/request'
import type { ApiResponse } from '@/types'
import { protectionStats, type MapPoint, type ProtectionStat, type VideoCard } from '@/data/mockData'
import BarChart from './charts/BarChart.vue'
import CampusMap from './CampusMap.vue'
import YearTimeline from './YearTimeline.vue'
import VideoCards from './VideoCards.vue'

interface MqttStatus {
  broker: {
    connected: boolean
    clients: {
      connected: number | null
      active: number | null
      total: number | null
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

const emit = defineEmits<{
  selectCore: []
  selectProtection: [item: ProtectionStat]
  selectMapPoint: [point: MapPoint]
  selectYear: [year: number]
  openMedia: [item: VideoCard]
}>()

const stats = ref<MqttStatus>({
  broker: {
    connected: false,
    clients: { connected: 0, active: 0, total: 0 }
  },
  business: {
    event_count: 0,
    status_count: 0,
    latest_event_at: null,
    latest_status_at: null,
    latest_business_at: null
  }
})
let timer: number | undefined

const hasBusinessData = computed(() => stats.value.business.event_count > 0 || stats.value.business.status_count > 0)
const totalVisits = computed(() => (hasBusinessData.value ? stats.value.business.event_count.toLocaleString() : '0'))

const formatTime = (value: string | null) => {
  if (!value) return '暂无'
  return value.replace('T', ' ').slice(0, 19)
}

const ringStats = computed<ProtectionStat[]>(() => {
  if (!hasBusinessData.value) return protectionStats
  return [
    {
      label: '状态上报',
      value: String(stats.value.business.status_count),
      detail: 'MQTT birdcam/status 主题已经写入 device_status 表的状态记录数量。'
    },
    {
      label: 'Broker客户端',
      value: String(stats.value.broker.clients.connected ?? 0),
      detail: 'MQTT Broker 当前连接客户端数量。'
    },
    {
      label: '最新事件',
      value: formatTime(stats.value.business.latest_event_at).slice(11) || '暂无',
      detail: `最新 MQTT 事件入库时间：${formatTime(stats.value.business.latest_event_at)}。`
    },
    {
      label: '最新状态',
      value: formatTime(stats.value.business.latest_status_at).slice(11) || '暂无',
      detail: `最新 MQTT 状态入库时间：${formatTime(stats.value.business.latest_status_at)}。`
    }
  ]
})

const loadStats = async () => {
  const res = await request<ApiResponse<MqttStatus>>({ url: '/mqtt/status' })
  stats.value = res.data
}

onMounted(() => {
  loadStats()
  timer = window.setInterval(loadStats, 60 * 1000)
})

onUnmounted(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<style scoped>
.center-dashboard {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  gap: 14px;
  min-height: 0;
}

.hero-kpi {
  position: relative;
  display: grid;
  grid-template-columns: minmax(260px, 0.9fr) minmax(0, 1fr);
  gap: 12px;
  align-items: center;
}

.kpi-orbit {
  display: grid;
  place-items: center;
  min-height: clamp(120px, 16vh, 172px);
  border: 1px solid rgba(53, 232, 255, 0.22);
  border-radius: 8px;
  background:
    radial-gradient(circle at 50% 50%, rgba(53, 232, 255, 0.18), transparent 58%),
    rgba(5, 15, 30, 0.68);
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.kpi-orbit:hover,
.kpi-orbit:focus-visible {
  border-color: rgba(87, 255, 173, 0.66);
  box-shadow: 0 0 28px rgba(53, 232, 255, 0.16);
}

.kpi-core {
  display: grid;
  place-items: center;
  width: min(96%, 390px);
  aspect-ratio: 2.8 / 1;
  border: 1px solid rgba(87, 255, 173, 0.34);
  border-radius: 999px;
  background: rgba(2, 10, 22, 0.76);
  box-shadow: 0 0 42px rgba(53, 232, 255, 0.2);
}

.kpi-core strong {
  color: var(--green);
  font-size: clamp(42px, 4vw, 76px);
  line-height: 0.98;
  text-shadow: 0 0 24px rgba(87, 255, 173, 0.45);
}

.kpi-core span {
  color: var(--text-muted);
  font-size: clamp(11px, 0.85vw, 14px);
}

.protection-ring {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.protection-ring button {
  min-height: clamp(74px, 10vh, 104px);
  min-width: 0;
  padding: 14px 10px;
  border: 1px solid rgba(53, 232, 255, 0.22);
  border-radius: 8px;
  background: linear-gradient(180deg, rgba(53, 232, 255, 0.1), rgba(5, 14, 28, 0.76));
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.protection-ring button:hover,
.protection-ring button:focus-visible {
  border-color: rgba(87, 255, 173, 0.62);
  transform: translateY(-1px);
}

.protection-ring span {
  color: var(--text-muted);
  font-size: 12px;
}

.protection-ring strong {
  display: block;
  margin-top: 9px;
  color: #eaffff;
  font-size: clamp(18px, 1.2vw, 28px);
  white-space: nowrap;
}

.main-stat-panel {
  display: flex;
  min-height: 0;
  flex-direction: column;
  padding: 16px;
}

.main-stat-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.18fr) minmax(260px, 0.82fr);
  gap: 14px;
  flex: 1;
  min-height: 0;
}

.map-wrap {
  display: grid;
  grid-template-rows: minmax(0, 1fr) auto;
  min-height: 0;
}

.bar-wrap {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  min-height: 0;
  border: 1px solid rgba(53, 232, 255, 0.18);
  border-radius: 8px;
  background: rgba(4, 17, 32, 0.52);
  padding: 12px;
}

.sub-title {
  margin-bottom: 8px;
  color: #cfefff;
  font-size: 13px;
  font-weight: 800;
}

.video-section {
  min-height: 0;
}
</style>
