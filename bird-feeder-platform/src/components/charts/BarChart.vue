<template>
  <div ref="chartRef" class="chart-host"></div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import * as echarts from 'echarts'
import request from '@/api/request'
import type { ApiResponse } from '@/types'
import { annualAreaStats } from '@/data/mockData'

interface DeviceMapApi {
  voltageLevel: string[]
  categoryData: Record<string, Array<{ name: string; value: number }>>
}

const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null
const rows = ref<Array<{ name: string; value: number }>>([])

const render = () => {
  if (!chartRef.value) return
  chart = chart || echarts.init(chartRef.value)
  chart.setOption({
    grid: { left: 72, right: 18, top: 16, bottom: 18 },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: 'rgba(4, 15, 30, 0.96)',
      borderColor: 'rgba(53, 232, 255, 0.5)',
      textStyle: { color: '#eafcff' }
    },
    xAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(130, 190, 210, 0.12)' } },
      axisLabel: { color: '#82a9bb' }
    },
    yAxis: {
      type: 'category',
      inverse: true,
      data: rows.value.map(item => item.name),
      axisLine: { lineStyle: { color: 'rgba(53, 232, 255, 0.22)' } },
      axisTick: { show: false },
      axisLabel: { color: '#c8e9f4', fontSize: 11 }
    },
    series: [
      {
        type: 'bar',
        data: rows.value.map(item => item.value),
        barWidth: 10,
        itemStyle: {
          borderRadius: [0, 8, 8, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#156cff' },
            { offset: 0.62, color: '#35e8ff' },
            { offset: 1, color: '#57ffad' }
          ])
        },
        backgroundStyle: { color: 'rgba(255,255,255,0.04)' },
        showBackground: true
      }
    ]
  })
}

const loadData = async () => {
  const res = await request<ApiResponse<DeviceMapApi>>({ url: '/devices/map' })
  const year = res.data.voltageLevel[res.data.voltageLevel.length - 1]
  const realRows = (year ? res.data.categoryData[year] || [] : [])
    .slice()
    .sort((a, b) => b.value - a.value)
    .slice(0, 8)
  rows.value = realRows.length && realRows.some(item => item.value > 0) ? realRows : annualAreaStats
  await nextTick()
  render()
}

const resize = () => chart?.resize()

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
