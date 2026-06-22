<template>
  <div ref="chartRef" class="chart-host"></div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import { behaviorData } from '@/data/mockData'

const props = withDefaults(defineProps<{
  data?: Array<{ mdate: string; value: number; temperature?: number | null }>
}>(), {
  data: () => []
})

const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null

const render = () => {
  if (!chartRef.value) return
  chart = chart || echarts.init(chartRef.value)
  const data = props.data.length
    ? props.data
    : behaviorData.days.map((day, index) => ({
        mdate: day,
        value: behaviorData.observations[index] || 0,
        temperature: behaviorData.activity[index] || null
      }))
  const labels = data.map(item => item.mdate)
  chart.setOption({
    grid: { left: 36, right: 18, top: 24, bottom: 24 },
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
      data: labels,
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
        name: '识别事件',
        type: 'line',
        smooth: true,
        symbolSize: 7,
        data: data.map(item => item.value),
        lineStyle: { width: 3, color: '#35e8ff' },
        itemStyle: { color: '#35e8ff', shadowBlur: 12, shadowColor: 'rgba(53, 232, 255, 0.8)' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(53, 232, 255, 0.2)' },
            { offset: 1, color: 'rgba(53, 232, 255, 0)' }
          ])
        }
      },
      {
        name: '平均温度',
        type: 'line',
        smooth: true,
        symbolSize: 6,
        data: data.map(item => item.temperature ?? null),
        lineStyle: { width: 2, color: '#ffd76a' },
        itemStyle: { color: '#ffd76a' }
      }
    ]
  })
}

const resize = () => chart?.resize()

watch(() => props.data, () => nextTick(render), { deep: true })

onMounted(() => {
  render()
  window.addEventListener('resize', resize)
})

onUnmounted(() => {
  window.removeEventListener('resize', resize)
  chart?.dispose()
})
</script>
