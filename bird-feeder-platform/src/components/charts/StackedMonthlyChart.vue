<template>
  <div ref="chartRef" class="chart-host"></div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { monthlyTrends } from '@/data/mockData'

const props = withDefaults(defineProps<{
  dimensions?: string[]
  series?: Array<{ species: string; values: number[] }>
}>(), {
  dimensions: () => [],
  series: () => []
})

const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null
const palette = ['#35e8ff', '#57ffad', '#ffd76a', '#ff9f43', '#b98cff']

const render = () => {
  if (!chartRef.value) return
  chart = chart || echarts.init(chartRef.value)
  const dimensions = props.series.length ? props.dimensions : monthlyTrends.months
  const seriesData = props.series.length ? props.series : monthlyTrends.series.map(item => ({ species: item.name, values: item.data }))
  chart.setOption({
    color: palette,
    grid: { left: 34, right: 14, top: 30, bottom: 24 },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
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
      data: dimensions,
      axisTick: { show: false },
      axisLine: { lineStyle: { color: 'rgba(53, 232, 255, 0.24)' } },
      axisLabel: { color: '#9db6c7', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(130, 190, 210, 0.12)' } },
      axisLabel: { color: '#82a9bb', fontSize: 10 }
    },
    series: seriesData.map(item => ({
      name: item.species,
      type: 'bar',
      stack: 'events',
      barWidth: 12,
      emphasis: { focus: 'series' },
      data: item.values
    }))
  })
}

const resize = () => chart?.resize()

watch(() => [props.dimensions, props.series], () => nextTick(render), { deep: true })

onMounted(() => {
  render()
  window.addEventListener('resize', resize)
})

onUnmounted(() => {
  window.removeEventListener('resize', resize)
  chart?.dispose()
})
</script>
