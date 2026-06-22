<template>
  <div class="stat-grid">
    <button
      v-for="item in stats"
      :key="item.label"
      type="button"
      class="stat-card"
      :class="`tone-${item.tone}`"
      @click="emit('select', item)"
    >
      <div class="stat-icon">
        <el-icon>
          <component :is="iconMap[item.icon]" />
        </el-icon>
      </div>
      <div>
        <span>{{ item.label }}</span>
        <strong class="digital">{{ item.value }}<em>{{ item.unit }}</em></strong>
      </div>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { Cloudy, Connection, MostlyCloudy, Rank } from '@element-plus/icons-vue'
import request from '@/api/request'
import type { ApiResponse } from '@/types'
import { overviewStats, type OverviewStat } from '@/data/mockData'

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

const emit = defineEmits<{
  select: [item: OverviewStat]
}>()

const source = ref<MqttStatus>({
  broker: {
    connected: false,
    clients: { connected: 0, active: 0, total: 0 },
    messages: { received: 0, publish_received: 0 }
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

const hasBusinessData = computed(() => source.value.business.event_count > 0 || source.value.business.status_count > 0)

const stats = computed<OverviewStat[]>(() => {
  if (!hasBusinessData.value) return overviewStats
  return [
    {
      label: '累计事件',
      value: String(source.value.business.event_count),
      unit: '条',
      icon: 'species',
      tone: 'cyan',
      detail: '来自 MQTT birdcam/event 主题并已写入 event_leave 表的真实 leave 事件数量。'
    },
    {
      label: '状态上报',
      value: String(source.value.business.status_count),
      unit: '条',
      icon: 'activity',
      tone: 'green',
      detail: '来自 MQTT birdcam/status 主题并已写入 device_status 表的真实设备状态数量。'
    },
    {
      label: 'Broker客户端',
      value: String(source.value.broker.clients.connected ?? 0),
      unit: '个',
      icon: 'device',
      tone: 'blue',
      detail: 'MQTT Broker 当前连接客户端数量，来自 $SYS/broker/clients/connected。'
    },
    {
      label: 'MQTT连接',
      value: source.value.broker.connected ? '正常' : '异常',
      unit: '',
      icon: 'weather',
      tone: 'amber',
      detail: `最新业务入库时间：${source.value.business.latest_business_at || '暂无'}。`
    }
  ]
})

const iconMap = {
  species: MostlyCloudy,
  activity: Rank,
  device: Connection,
  weather: Cloudy
}

const loadStats = async () => {
  const res = await request<ApiResponse<MqttStatus>>({ url: '/mqtt/status' })
  source.value = res.data
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
.stat-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 74px;
  padding: 12px;
  border: 1px solid rgba(53, 232, 255, 0.22);
  border-radius: 8px;
  background: rgba(8, 24, 46, 0.68);
  box-shadow: inset 0 0 18px rgba(53, 232, 255, 0.05);
  text-align: left;
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.stat-card:hover,
.stat-card:focus-visible {
  border-color: rgba(87, 255, 173, 0.72);
  box-shadow: 0 0 24px rgba(53, 232, 255, 0.2), inset 0 0 18px rgba(53, 232, 255, 0.08);
  transform: translateY(-1px);
}

.stat-icon {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  flex: 0 0 38px;
  border-radius: 8px;
  color: var(--cyan);
  background: rgba(53, 232, 255, 0.12);
  box-shadow: 0 0 18px rgba(53, 232, 255, 0.22);
  font-size: 21px;
}

.tone-green .stat-icon {
  color: var(--green);
  background: rgba(87, 255, 173, 0.12);
}

.tone-amber .stat-icon {
  color: var(--amber);
  background: rgba(255, 215, 106, 0.12);
}

.stat-card span {
  display: block;
  color: var(--text-muted);
  font-size: clamp(11px, 0.7vw, 13px);
}

.stat-card strong {
  display: block;
  margin-top: 4px;
  color: var(--text-main);
  font-size: clamp(20px, 1.55vw, 30px);
  line-height: 1;
  text-shadow: 0 0 18px rgba(53, 232, 255, 0.35);
}

.stat-card em {
  margin-left: 3px;
  color: var(--text-muted);
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 12px;
  font-style: normal;
}
</style>
