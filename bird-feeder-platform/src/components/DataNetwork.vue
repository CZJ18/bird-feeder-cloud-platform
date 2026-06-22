<template>
  <div class="network">
    <svg class="network-lines" viewBox="0 0 100 100" preserveAspectRatio="none">
      <path v-for="node in nodes" :key="node.label" :d="linePath(node)" />
    </svg>

    <div class="hub" role="button" tabindex="0" @click="emit('selectHub')" @keydown.enter.prevent="emit('selectHub')">
      <span :class="{ offline: !mqttStatus?.broker.connected }"></span>
      <strong>{{ hubTitle }}</strong>
      <small>{{ hubSubtitle }}</small>
    </div>

    <div
      v-for="node in nodes"
      :key="node.label"
      class="network-node"
      :class="{ offline: node.status === '离线' }"
      :style="{ left: `${node.x}%`, top: `${node.y}%` }"
      role="button"
      tabindex="0"
      @click="emit('select', node)"
      @keydown.enter.prevent="emit('select', node)"
      @keydown.space.prevent="emit('select', node)"
    >
      <i></i>
      <span>{{ node.label }}</span>
      <b>{{ node.throughput }}</b>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import request from '@/api/request'
import type { ApiResponse } from '@/types'
import type { NetworkNode } from '@/data/mockData'

interface MqttStatus {
  broker: {
    connected: boolean
    host: string
    port: number
    version?: string | null
    uptime?: string | null
    clients: {
      connected?: number | null
      active?: number | null
      total?: number | null
    }
    messages: {
      received?: number | null
      sent?: number | null
      publish_received?: number | null
      publish_sent?: number | null
    }
    error?: string | null
    probed_at: string
  }
  business: {
    event_count: number
    status_count: number
    latest_event_at?: string | null
    latest_status_at?: string | null
    latest_business_at?: string | null
  }
  topics: {
    event: string
    status: string
  }
}

const emit = defineEmits<{
  select: [node: NetworkNode]
  selectHub: []
}>()

const mqttStatus = ref<MqttStatus | null>(null)
let timer: number | undefined

const onlineText = computed(() => (mqttStatus.value?.broker.connected ? '在线' : '离线'))
const hubTitle = computed(() => (mqttStatus.value?.broker.connected ? 'MQTT Broker' : 'MQTT 未连接'))
const hubSubtitle = computed(() => {
  const clients = mqttStatus.value?.broker.clients.connected
  return clients == null ? '客户端 --' : `客户端 ${clients}`
})

const formatTime = (value?: string | null) => {
  if (!value) return '无业务消息'
  return value.replace('T', ' ').slice(0, 19)
}

const nodes = computed<NetworkNode[]>(() => {
  const status = mqttStatus.value
  const brokerOnline = status?.broker.connected ?? false
  const state = brokerOnline ? '在线' : '离线'
  const clients = status?.broker.clients
  const messages = status?.broker.messages
  const business = status?.business
  return [
    {
      label: `连接客户端 ${clients?.connected ?? '--'}`,
      x: 18,
      y: 24,
      status: state,
      lastSeen: status?.broker.probed_at || '--',
      throughput: `活跃 ${clients?.active ?? '--'} / 总 ${clients?.total ?? '--'}`
    },
    {
      label: status?.topics.event || 'birdcam/event',
      x: 80,
      y: 24,
      status: state,
      lastSeen: formatTime(business?.latest_event_at),
      throughput: `${business?.event_count ?? 0} 条`
    },
    {
      label: status?.topics.status || 'birdcam/status',
      x: 18,
      y: 74,
      status: state,
      lastSeen: formatTime(business?.latest_status_at),
      throughput: `${business?.status_count ?? 0} 条`
    },
    {
      label: 'Broker 消息流',
      x: 80,
      y: 74,
      status: state,
      lastSeen: formatTime(status?.business.latest_business_at),
      throughput: `收 ${messages?.publish_received ?? '--'} / 发 ${messages?.publish_sent ?? '--'}`
    }
  ]
})

const loadMqttStatus = async () => {
  const res = await request<ApiResponse<MqttStatus>>({ url: '/mqtt/status' })
  mqttStatus.value = res.data
}

const linePath = (node: { x: number; y: number }) => {
  const controlX = (node.x + 50) / 2
  const controlY = node.y < 50 ? node.y + 16 : node.y - 16
  return `M 50 50 Q ${controlX} ${controlY} ${node.x} ${node.y}`
}

onMounted(() => {
  loadMqttStatus()
  timer = window.setInterval(loadMqttStatus, 30 * 1000)
})

onUnmounted(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<style scoped>
.network {
  position: relative;
  height: clamp(170px, 19vh, 230px);
  min-height: 0;
}

.network-lines {
  position: absolute;
  inset: 0;
}

.network-lines path {
  fill: none;
  stroke: rgba(53, 232, 255, 0.42);
  stroke-width: 0.8;
  stroke-dasharray: 4 3;
  filter: drop-shadow(0 0 4px rgba(53, 232, 255, 0.7));
}

.hub {
  position: absolute;
  left: 50%;
  top: 50%;
  display: grid;
  place-items: center;
  width: 96px;
  height: 96px;
  transform: translate(-50%, -50%);
  border: 1px solid rgba(87, 255, 173, 0.58);
  border-radius: 999px;
  background: radial-gradient(circle, rgba(87, 255, 173, 0.22), rgba(8, 30, 45, 0.86));
  box-shadow: 0 0 28px rgba(87, 255, 173, 0.24);
  cursor: pointer;
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.hub:hover,
.hub:focus-visible {
  transform: translate(-50%, -50%) scale(1.04);
  box-shadow: 0 0 34px rgba(87, 255, 173, 0.36);
}

.hub span {
  width: 16px;
  height: 16px;
  border-radius: 999px;
  background: var(--green);
  box-shadow: 0 0 18px rgba(87, 255, 173, 0.9);
}

.hub span.offline {
  background: var(--danger);
  box-shadow: 0 0 18px rgba(255, 95, 134, 0.8);
}

.hub strong {
  margin-top: -12px;
  font-size: 12px;
}

.hub small {
  margin-top: -18px;
  color: var(--text-muted);
  font-size: 10px;
}

.network-node {
  position: absolute;
  display: grid;
  grid-template-columns: 10px minmax(0, auto);
  gap: 4px 6px;
  align-items: center;
  transform: translate(-50%, -50%);
  color: #caeefe;
  font-size: clamp(10px, 0.68vw, 12px);
  white-space: nowrap;
  cursor: pointer;
  transition: transform 0.2s ease, color 0.2s ease;
}

.network-node:hover,
.network-node:focus-visible {
  color: #ffffff;
  transform: translate(-50%, -50%) scale(1.04);
}

.network-node i {
  grid-row: span 2;
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: var(--cyan);
  box-shadow: 0 0 14px rgba(53, 232, 255, 0.95);
}

.network-node.offline i {
  background: var(--danger);
  box-shadow: 0 0 14px rgba(255, 95, 134, 0.75);
}

.network-node b {
  color: var(--text-muted);
  font-size: 10px;
  font-weight: 600;
}
</style>
