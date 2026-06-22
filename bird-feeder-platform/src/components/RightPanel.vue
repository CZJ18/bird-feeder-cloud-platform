<template>
  <aside class="right-panel">
    <FilterUploadPanel @apply="emit('applyFilter', $event)" @upload="emit('uploadFile', $event)" />
    <ChartCard title="时间动态与设备温度" action-label="详情" @action="emit('openChart', '时间动态与设备温度')">
      <BehaviorChart />
    </ChartCard>
    <ChartCard title="物种分布分析" action-label="详情" @action="emit('openChart', '物种分布分析')">
      <PieChart />
    </ChartCard>
    <ChartCard title="月度物种趋势" action-label="详情" @action="emit('openChart', '月度物种趋势')">
      <MultiLineChart />
    </ChartCard>
  </aside>
</template>

<script setup lang="ts">
import ChartCard from './ChartCard.vue'
import FilterUploadPanel from './FilterUploadPanel.vue'
import BehaviorChart from './charts/BehaviorChart.vue'
import PieChart from './charts/PieChart.vue'
import MultiLineChart from './charts/MultiLineChart.vue'

const emit = defineEmits<{
  applyFilter: [payload: { camera: string; startTime: string; endTime: string }]
  uploadFile: [payload: { camera: string; fileName: string }]
  openChart: [title: string]
}>()
</script>

<style scoped>
.right-panel {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr);
  gap: 14px;
  min-height: 0;
}
</style>
