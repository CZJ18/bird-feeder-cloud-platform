<template>
  <div class="bird-screen">
    <div class="screen-glow glow-a"></div>
    <div class="screen-glow glow-b"></div>
    <div class="screen-grid"></div>

    <nav class="screen-switch" aria-label="大屏页面切换">
      <button type="button" :class="{ active: activePage === 'overview' }" @click="activePage = 'overview'">总览</button>
      <button type="button" :class="{ active: activePage === 'detail' }" @click="activePage = 'detail'">明细</button>
    </nav>

    <div v-if="activePage === 'overview'" class="screen-shell">
      <LeftPanel
        @select-stat="openStat"
        @select-species="openSpecies"
        @select-node="openNode"
        @select-hub="openHub"
      />
      <CenterDashboard
        @select-core="openCore"
        @select-protection="openProtection"
        @select-map-point="openMapPoint"
        @select-year="openYear"
        @open-media="openMedia"
      />
      <RightPanel
        @apply-filter="openFilterResult"
        @upload-file="openUploadResult"
        @open-chart="openChart"
      />
    </div>

    <DashboardDetailPage
      v-else
      @open-metric="openMetric"
      @open-chart="openChart"
      @open-device="openDevice"
      @open-map-point="openMapPoint"
      @open-moment="openMedia"
      @open-low-confidence="openLowConfidence"
    />

    <Teleport to="body">
      <div v-if="modal" class="detail-layer" @click.self="closeModal">
        <section class="detail-modal" role="dialog" aria-modal="true" :aria-label="modal.title">
          <button type="button" class="modal-close" aria-label="关闭详情" @click="closeModal">×</button>
          <img v-if="modal.image" class="modal-image" :src="modal.image" :alt="modal.title" />
          <div class="modal-content">
            <span class="modal-kicker">{{ modal.kicker }}</span>
            <h2>{{ modal.title }}</h2>
            <p>{{ modal.description }}</p>
            <dl v-if="modal.meta.length" class="modal-meta">
              <div v-for="item in modal.meta" :key="item.label">
                <dt>{{ item.label }}</dt>
                <dd>{{ item.value }}</dd>
              </div>
            </dl>
          </div>
        </section>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import LeftPanel from '@/components/LeftPanel.vue'
import CenterDashboard from '@/components/CenterDashboard.vue'
import RightPanel from '@/components/RightPanel.vue'
import DashboardDetailPage from '@/components/DashboardDetailPage.vue'
import type {
  DashboardMetric,
  DeviceStatusRow,
  LowConfidenceRow,
  MapPoint,
  NetworkNode,
  OverviewStat,
  ProtectionStat,
  SpeciesBar,
  VideoCard
} from '@/data/mockData'

interface DetailModal {
  kicker: string
  title: string
  description: string
  image?: string
  meta: Array<{ label: string; value: string }>
}

const activePage = ref<'overview' | 'detail'>('overview')
const modal = ref<DetailModal | null>(null)

const showModal = (nextModal: DetailModal) => {
  modal.value = nextModal
}

const closeModal = () => {
  modal.value = null
}

const openMetric = (item: DashboardMetric) => {
  showModal({
    kicker: '前端展示字段',
    title: item.label,
    description: item.description,
    meta: [
      { label: '当前数值', value: `${item.value}${item.unit}` },
      { label: '推荐刷新', value: item.refresh }
    ]
  })
}

const openStat = (item: OverviewStat) => {
  showModal({
    kicker: '核心指标',
    title: item.label,
    description: item.detail,
    meta: [
      { label: '当前数值', value: `${item.value}${item.unit}` },
      { label: '刷新策略', value: item.icon === 'device' ? '5 分钟刷新' : '30 秒至 5 分钟刷新' }
    ]
  })
}

const openSpecies = (item: SpeciesBar) => {
  showModal({
    kicker: '物种详情',
    title: item.name,
    description: `${item.name} 当前在样本中的事件量为 ${item.value} 条，平均识别置信度 ${item.confidence}%。`,
    meta: [
      { label: '拉丁名', value: item.latin },
      { label: '保护级别', value: item.protection },
      { label: '事件数量', value: `${item.value} 条` },
      { label: '平均置信度', value: `${item.confidence}%` }
    ]
  })
}

const openNode = (node: NetworkNode) => {
  showModal({
    kicker: '采集链路',
    title: node.label,
    description: node.status === '在线' ? '该节点正在向数据中心同步监测数据。' : '该节点最近未上报状态，需要检查网络或设备电源。',
    meta: [
      { label: '状态', value: node.status },
      { label: '最后上报', value: node.lastSeen },
      { label: '实时吞吐', value: node.throughput }
    ]
  })
}

const openHub = () => {
  showModal({
    kicker: '数据中心',
    title: '边缘设备数据汇聚',
    description: '摄像头与识别终端通过 MQTT 和 HTTP 上传事件、状态与低置信度图片，前端大屏按接口聚合展示。',
    meta: [
      { label: '数据类型', value: 'leave 事件、设备状态、待审核图片' },
      { label: '安全策略', value: '静态 Token + 设备 API Key' }
    ]
  })
}

const openCore = () => {
  showModal({
    kicker: '累计识别',
    title: '23,456 条有效识别记录',
    description: '该数值统计数据库事件表中所有 leave 事件，用于表示平台累计有效观测规模。',
    meta: [
      { label: '事件类型', value: 'leave' },
      { label: '统计口径', value: '高置信度事件表' },
      { label: '建议刷新', value: '30 秒' }
    ]
  })
}

const openProtection = (item: ProtectionStat) => {
  showModal({
    kicker: '保护等级',
    title: item.label,
    description: item.detail,
    meta: [
      { label: '记录数量', value: item.value },
      { label: '展示位置', value: '核心指标环绕区' }
    ]
  })
}

const openMapPoint = (point: MapPoint) => {
  showModal({
    kicker: '设备地图数据',
    title: point.name,
    description: `${point.name} 当前热度为 ${point.heat}，设备 ${point.status}。`,
    meta: [
      { label: '设备编号', value: point.deviceId },
      { label: '在线状态', value: point.status },
      { label: '观测物种', value: `${point.species} 种` },
      { label: '年度事件', value: `${point.events} 条` }
    ]
  })
}

const openYear = (year: number) => {
  showModal({
    kicker: '年度切换',
    title: `${year} 年数据视图`,
    description: '年份轴已切换选中状态。接真实 API 后，可按该年份重新请求地图与年度趋势数据。',
    meta: [
      { label: '当前年份', value: String(year) },
      { label: '联动区域', value: '地图热力、区域排行、年度趋势' }
    ]
  })
}

const openDevice = (item: DeviceStatusRow) => {
  showModal({
    kicker: '设备状态列表',
    title: `${item.deviceId} / ${item.name}`,
    description: item.status === '在线' ? '设备最近 5 分钟内有状态上报。' : '设备已超过在线窗口，需要检查网络、电源或采集进程。',
    meta: [
      { label: '位置', value: item.location },
      { label: '状态', value: item.status },
      { label: '最后上报', value: item.lastSeen },
      { label: 'CPU 温度', value: item.temperature },
      { label: '电量', value: item.battery },
      { label: '余粮', value: item.foodLevel }
    ]
  })
}

const openMedia = (item: VideoCard) => {
  showModal({
    kicker: '精彩瞬间',
    title: item.title,
    description: item.description,
    image: item.image,
    meta: [
      { label: '采集设备', value: item.camera },
      { label: '识别物种', value: item.species },
      { label: '采集时间', value: item.time },
      { label: '片段时长', value: item.duration }
    ]
  })
}

const openLowConfidence = (item: LowConfidenceRow) => {
  showModal({
    kicker: '低置信度图片',
    title: `${item.id} / ${item.species}`,
    description: '该图片来自低置信度队列，需要人工确认识别结果后再进入正式事件统计。',
    image: item.image,
    meta: [
      { label: '设备编号', value: item.deviceId },
      { label: '置信度', value: item.confidence },
      { label: '采集时间', value: item.time },
      { label: '审核状态', value: item.status === 'pending' ? '待审核' : item.status === 'approved' ? '已通过' : '已驳回' }
    ]
  })
}

const openFilterResult = (payload: { camera: string; startTime: string; endTime: string }) => {
  showModal({
    kicker: '筛选已应用',
    title: payload.camera,
    description: '当前大屏已经记录筛选条件。接入真实 API 后，这里会触发对应时间范围的数据刷新。',
    meta: [
      { label: '开始时间', value: payload.startTime.replace('T', ' ') },
      { label: '结束时间', value: payload.endTime.replace('T', ' ') }
    ]
  })
}

const openUploadResult = (payload: { camera: string; fileName: string }) => {
  showModal({
    kicker: '上传队列',
    title: payload.fileName,
    description: '文件已进入前端上传流程。接后端图片上传接口后，会携带设备 API Key 提交到云端存储。',
    meta: [
      { label: '来源设备', value: payload.camera },
      { label: '处理状态', value: '等待后端确认' }
    ]
  })
}

const openChart = (title: string) => {
  showModal({
    kicker: '图表详情',
    title,
    description: '该图表支持鼠标悬停查看明细。接真实接口后，可扩展为按时间、物种和点位联动过滤。',
    meta: [
      { label: '交互方式', value: '悬停 tooltip / 详情弹窗' },
      { label: '数据来源', value: '事件表聚合 + 状态表平均值' }
    ]
  })
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') closeModal()
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
</script>

<style scoped>
.bird-screen {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background:
    radial-gradient(circle at 50% -8%, rgba(53, 232, 255, 0.16), transparent 30%),
    linear-gradient(135deg, #030915 0%, #061426 42%, #030713 100%);
}

.screen-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(53, 232, 255, 0.07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(53, 232, 255, 0.07) 1px, transparent 1px);
  background-size: 34px 34px;
  mask-image: radial-gradient(circle at center, black 0 64%, transparent 96%);
}

.screen-grid::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255,255,255,0.035), transparent 8%, transparent 92%, rgba(255,255,255,0.03));
  pointer-events: none;
}

.screen-glow {
  position: absolute;
  width: 34vw;
  aspect-ratio: 1;
  border-radius: 999px;
  filter: blur(70px);
  opacity: 0.32;
  pointer-events: none;
}

.glow-a {
  left: -10vw;
  top: 20vh;
  background: var(--blue);
}

.glow-b {
  right: -8vw;
  bottom: -8vh;
  background: var(--green);
}

.screen-switch {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 5;
  display: flex;
  gap: 6px;
  padding: 4px;
  border: 1px solid rgba(53, 232, 255, 0.22);
  border-radius: 8px;
  background: rgba(4, 15, 30, 0.72);
  backdrop-filter: blur(8px);
}

.screen-switch button {
  height: 28px;
  min-width: 56px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 12px;
  font-weight: 800;
}

.screen-switch button.active {
  background: linear-gradient(90deg, rgba(21, 108, 255, 0.82), rgba(53, 232, 255, 0.72));
  color: #ffffff;
}

.screen-shell {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(290px, 25%) minmax(620px, 50%) minmax(290px, 25%);
  gap: 16px;
  width: 100%;
  height: 100%;
  padding: 16px;
}

.detail-layer {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: grid;
  place-items: center;
  padding: 28px;
  background: rgba(0, 7, 18, 0.72);
  backdrop-filter: blur(8px);
}

.detail-modal {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  width: min(760px, 94vw);
  max-height: 88vh;
  overflow: hidden;
  border: 1px solid rgba(53, 232, 255, 0.42);
  border-radius: 8px;
  background:
    linear-gradient(135deg, rgba(53, 232, 255, 0.12), transparent 42%),
    rgba(5, 16, 31, 0.96);
  box-shadow: 0 0 52px rgba(53, 232, 255, 0.22);
}

.modal-close {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 2;
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.45);
  color: #ffffff;
  cursor: pointer;
  font-size: 24px;
  line-height: 1;
}

.modal-image {
  width: 100%;
  max-height: 46vh;
  object-fit: cover;
  border-bottom: 1px solid rgba(53, 232, 255, 0.22);
}

.modal-content {
  padding: 22px;
}

.modal-kicker {
  color: var(--green);
  font-size: 12px;
  font-weight: 800;
}

.modal-content h2 {
  margin: 8px 42px 8px 0;
  color: #f4fdff;
  font-size: clamp(22px, 2.3vw, 34px);
  line-height: 1.12;
}

.modal-content p {
  margin: 0;
  color: #b8d3e1;
  font-size: 14px;
  line-height: 1.7;
}

.modal-meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin: 18px 0 0;
}

.modal-meta div {
  min-width: 0;
  border: 1px solid rgba(53, 232, 255, 0.18);
  border-radius: 8px;
  background: rgba(53, 232, 255, 0.07);
  padding: 10px;
}

.modal-meta dt {
  color: var(--text-muted);
  font-size: 12px;
}

.modal-meta dd {
  margin: 5px 0 0;
  color: #ecfbff;
  font-size: 14px;
  font-weight: 800;
  overflow-wrap: anywhere;
}

@media (max-width: 1280px) {
  .bird-screen {
    overflow: auto;
  }

  .screen-shell {
    grid-template-columns: 1fr;
    height: auto;
    min-height: 100vh;
  }
}

@media (max-width: 720px) {
  .detail-layer {
    padding: 14px;
  }

  .modal-meta {
    grid-template-columns: 1fr;
  }
}
</style>
