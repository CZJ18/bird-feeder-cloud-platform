<template>
  <div ref="chartRef" class="chart-host"></div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import request from '@/api/request'
import type { ApiResponse } from '@/types'
import { populationShare } from '@/data/mockData'

const props = defineProps<{
  data?: Array<{ name: string; value: number }>
}>()

const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null
const internalData = ref<Array<{ name: string; value: number }>>([])
const chartData = computed(() => props.data ?? internalData.value)

const colors = ['#35e8ff', '#57ffad', '#ffd76a', '#ff9f43', '#2f8dff', '#b98cff', '#ff5f86']

const render = () => {
  if (!chartRef.value) return
  chart = chart || echarts.init(chartRef.value)
  const data = chartData.value.length ? chartData.value : populationShare
  chart.setOption({
    color: colors,
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(4, 15, 30, 0.96)',
      borderColor: 'rgba(53, 232, 255, 0.5)',
      textStyle: { color: '#eafcff' }
    },
    legend: {
      right: 0,
      top: 'middle',
      orient: 'vertical',
      itemWidth: 9,
      itemHeight: 9,
      textStyle: { color: '#9db6c7', fontSize: 10 }
    },
    series: [
      {
        name: '物种分布',
        type: 'pie',
        radius: ['42%', '68%'],
        center: ['38%', '52%'],
        avoidLabelOverlap: true,
        label: {
          color: '#dffaff',
          formatter: '{b}\n{c}',
          fontSize: 10
        },
        labelLine: {
          lineStyle: { color: 'rgba(53, 232, 255, 0.35)' }
        },
        itemStyle: {
          borderColor: '#071426',
          borderWidth: 2,
          shadowBlur: 12,
          shadowColor: 'rgba(53, 232, 255, 0.2)'
        },
        data
      }
    ]
  })
}

const resize = () => chart?.resize()

const loadData = async () => {
  if (props.data) return
  const res = await request<ApiResponse<{ regionData: Array<{ name: string; value: number }> }>>({
    url: '/species/distribution',
    params: { top: 7 }
  })
  internalData.value = res.data.regionData.length ? res.data.regionData : populationShare
  await nextTick()
  render()
}

watch(() => props.data, () => nextTick(render), { deep: true })

onMounted(() => {
  render()
  loadData()
  window.addEventListener('resize', resize)
})

onUnmounted(() => {
  window.removeEventListener('resize', resize)
  chart?.dispose()
})
</script>
