<template>
  <div ref="chartRef" class="chart-host"></div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import * as echarts from 'echarts'
import request from '@/api/request'
import type { ApiResponse } from '@/types'
import { monthlyTrends } from '@/data/mockData'

interface MonthlyTrend {
  dimensions: string[]
  data: Array<{ species: string; values: number[] }>
}

const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null
const trend = ref<MonthlyTrend>({ dimensions: [], data: [] })

const palette = ['#35e8ff', '#57ffad', '#ffd76a', '#ff9f43', '#b98cff']

const render = () => {
  if (!chartRef.value) return
  chart = chart || echarts.init(chartRef.value)
  chart.setOption({
    color: palette,
    grid: { left: 34, right: 12, top: 28, bottom: 24 },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(4, 15, 30, 0.96)',
      borderColor: 'rgba(53, 232, 255, 0.5)',
      textStyle: { color: '#eafcff' }
    },
    legend: {
      top: 0,
      left: 0,
      itemWidth: 10,
      itemHeight: 8,
      textStyle: { color: '#9db6c7', fontSize: 10 }
    },
    xAxis: {
      type: 'category',
      data: trend.value.dimensions,
      axisTick: { show: false },
      axisLine: { lineStyle: { color: 'rgba(53, 232, 255, 0.24)' } },
      axisLabel: { color: '#9db6c7', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(130, 190, 210, 0.12)' } },
      axisLabel: { color: '#82a9bb', fontSize: 10 }
    },
    series: trend.value.data.map((item, index) => ({
      name: item.species,
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 4,
      data: item.values,
      lineStyle: { width: 2 },
      itemStyle: { shadowBlur: 8, shadowColor: palette[index % palette.length] }
    }))
  })
}

const loadData = async () => {
  const res = await request<ApiResponse<MonthlyTrend>>({ url: '/monthly-trend' })
  trend.value = res.data.data.length
    ? res.data
    : {
        dimensions: monthlyTrends.months,
        data: monthlyTrends.series.map(item => ({ species: item.name, values: item.data }))
      }
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
