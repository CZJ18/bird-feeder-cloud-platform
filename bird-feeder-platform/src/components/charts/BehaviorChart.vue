<template>
  <div ref="chartRef" class="chart-host"></div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import * as echarts from 'echarts'
import request from '@/api/request'
import type { ApiResponse } from '@/types'
import { behaviorData } from '@/data/mockData'

interface TimePoint {
  mdate: string
  value: number
  temperature?: number | null
}

const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null
const rows = ref<TimePoint[]>([])

const fallbackRows = () =>
  behaviorData.days.map((day, index) => ({
    mdate: day,
    value: behaviorData.observations[index] || 0,
    temperature: behaviorData.activity[index] || null
  }))

const render = () => {
  if (!chartRef.value) return
  chart = chart || echarts.init(chartRef.value)
  chart.setOption({
    grid: { left: 34, right: 18, top: 22, bottom: 24 },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(4, 15, 30, 0.96)',
      borderColor: 'rgba(53, 232, 255, 0.5)',
      textStyle: { color: '#eafcff' }
    },
    legend: {
      top: 0,
      right: 4,
      textStyle: { color: '#9db6c7', fontSize: 10 },
      itemWidth: 10,
      itemHeight: 8
    },
    xAxis: {
      type: 'category',
      data: rows.value.map(item => item.mdate),
      axisTick: { show: false },
      axisLine: { lineStyle: { color: 'rgba(53, 232, 255, 0.24)' } },
      axisLabel: { color: '#9db6c7', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(130, 190, 210, 0.12)' } },
      axisLabel: { color: '#82a9bb', fontSize: 10 }
    },
    series: [
      {
        name: '观测数量',
        type: 'bar',
        data: rows.value.map(item => item.value),
        barWidth: 12,
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#35e8ff' },
            { offset: 1, color: 'rgba(47, 141, 255, 0.18)' }
          ])
        }
      },
      {
        name: '平均温度',
        type: 'line',
        smooth: true,
        symbolSize: 7,
        data: rows.value.map(item => item.temperature ?? null),
        lineStyle: { width: 2, color: '#ffd76a' },
        itemStyle: { color: '#ffd76a', shadowBlur: 12, shadowColor: 'rgba(255, 215, 106, 0.8)' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(255, 215, 106, 0.18)' },
            { offset: 1, color: 'rgba(255, 215, 106, 0)' }
          ])
        }
      }
    ]
  })
}

const loadData = async () => {
  const res = await request<ApiResponse<{ regionData: TimePoint[] }>>({
    url: '/time-dynamics',
    params: { days: 7, unit: 'day' }
  })
  rows.value = res.data.regionData.length ? res.data.regionData : fallbackRows()
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
