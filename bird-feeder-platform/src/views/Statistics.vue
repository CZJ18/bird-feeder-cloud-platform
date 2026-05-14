<template>
  <div class="statistics-page">
    <div class="page-header">
      <h2>数据统计</h2>
    </div>

    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="chart-header">
            <h3>每日识别次数趋势</h3>
          </div>
          <div ref="lineChartRef" class="chart-container"></div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="chart-header">
            <h3>不同鸟类出现次数</h3>
          </div>
          <div ref="barChartRef" class="chart-container"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="chart-header">
            <h3>鸟类占比分布</h3>
          </div>
          <div ref="pieChartRef" class="chart-container"></div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="chart-card">
          <div class="chart-header">
            <h3>设备上传次数排行</h3>
          </div>
          <div ref="rankChartRef" class="chart-container"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="24">
        <div class="chart-card">
          <div class="chart-header">
            <h3>饲料余量变化趋势</h3>
          </div>
          <div ref="trendChartRef" class="chart-container-large"></div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import {
  getDailyRecognitions,
  getBirdDistribution,
  getDeviceUploadRank,
  getFoodLevelTrend
} from '@/api/statistics'
import type { DailyRecognition, BirdDistribution, DeviceUploadRank } from '@/types'

const lineChartRef = ref<HTMLDivElement>()
const barChartRef = ref<HTMLDivElement>()
const pieChartRef = ref<HTMLDivElement>()
const rankChartRef = ref<HTMLDivElement>()
const trendChartRef = ref<HTMLDivElement>()

let lineChart: echarts.ECharts | null = null
let barChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null
let rankChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

const loadData = async () => {
  try {
    const [dailyData, birdDist, rankData, trendData] = await Promise.all([
      getDailyRecognitions(30),
      getBirdDistribution(),
      getDeviceUploadRank(),
      getFoodLevelTrend()
    ])

    renderLineChart(dailyData)
    renderBarChart(birdDist)
    renderPieChart(birdDist)
    renderRankChart(rankData)
    renderTrendChart(trendData)
  } catch (error) {
    console.error('Failed to load statistics:', error)
  }
}

const renderLineChart = (data: DailyRecognition[]) => {
  if (!lineChartRef.value) return
  if (lineChart) lineChart.dispose()
  
  lineChart = echarts.init(lineChartRef.value)
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(26, 26, 46, 0.95)',
      borderColor: '#00d4ff',
      textStyle: { color: '#ffffff' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.map(d => d.date.slice(5)),
      axisLine: { lineStyle: { color: '#333' } },
      axisLabel: { color: '#8b8ba3', rotate: 45 }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#333' } },
      axisLabel: { color: '#8b8ba3' },
      splitLine: { lineStyle: { color: 'rgba(0, 212, 255, 0.1)' } }
    },
    series: [
      {
        name: '识别次数',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { color: '#00d4ff', width: 3 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 212, 255, 0.3)' },
            { offset: 1, color: 'rgba(0, 212, 255, 0.05)' }
          ])
        },
        itemStyle: { color: '#00d4ff' },
        data: data.map(d => d.count)
      }
    ]
  }
  
  lineChart.setOption(option)
}

const renderBarChart = (data: BirdDistribution[]) => {
  if (!barChartRef.value) return
  if (barChart) barChart.dispose()
  
  barChart = echarts.init(barChartRef.value)
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(26, 26, 46, 0.95)',
      borderColor: '#00d4ff',
      textStyle: { color: '#ffffff' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.map(d => d.name),
      axisLine: { lineStyle: { color: '#333' } },
      axisLabel: { color: '#8b8ba3', rotate: 30 }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#333' } },
      axisLabel: { color: '#8b8ba3' },
      splitLine: { lineStyle: { color: 'rgba(0, 212, 255, 0.1)' } }
    },
    series: [
      {
        name: '出现次数',
        type: 'bar',
        barWidth: '60%',
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#00ff88' },
            { offset: 1, color: '#00d4ff' }
          ])
        },
        data: data.map(d => d.value)
      }
    ]
  }
  
  barChart.setOption(option)
}

const renderPieChart = (data: BirdDistribution[]) => {
  if (!pieChartRef.value) return
  if (pieChart) pieChart.dispose()
  
  pieChart = echarts.init(pieChartRef.value)
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(26, 26, 46, 0.95)',
      borderColor: '#00d4ff',
      textStyle: { color: '#ffffff' }
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: { color: '#8b8ba3' }
    },
    series: [
      {
        name: '占比',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#1a1a2e',
          borderWidth: 2
        },
        label: { show: false },
        emphasis: {
          label: { show: true, fontSize: 14, fontWeight: 'bold', color: '#ffffff' }
        },
        labelLine: { show: false },
        data: data.map((d, i) => ({
          value: d.value,
          name: d.name,
          itemStyle: {
            color: ['#00d4ff', '#00ff88', '#ffb800', '#ff4757', '#9C27B0', '#795548', '#607D8B'][i]
          }
        }))
      }
    ]
  }
  
  pieChart.setOption(option)
}

const renderRankChart = (data: DeviceUploadRank[]) => {
  if (!rankChartRef.value) return
  if (rankChart) rankChart.dispose()
  
  rankChart = echarts.init(rankChartRef.value)
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(26, 26, 46, 0.95)',
      borderColor: '#00d4ff',
      textStyle: { color: '#ffffff' },
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#333' } },
      axisLabel: { color: '#8b8ba3' },
      splitLine: { lineStyle: { color: 'rgba(0, 212, 255, 0.1)' } }
    },
    yAxis: {
      type: 'category',
      data: data.map(d => d.device_name),
      axisLine: { lineStyle: { color: '#333' } },
      axisLabel: { color: '#8b8ba3' }
    },
    series: [
      {
        name: '上传次数',
        type: 'bar',
        barWidth: '60%',
        itemStyle: {
          borderRadius: [0, 6, 6, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#00d4ff' },
            { offset: 1, color: '#00ff88' }
          ])
        },
        data: data.map(d => d.upload_count)
      }
    ]
  }
  
  rankChart.setOption(option)
}

const renderTrendChart = (data: any[]) => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()
  
  trendChart = echarts.init(trendChartRef.value)
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(26, 26, 46, 0.95)',
      borderColor: '#00d4ff',
      textStyle: { color: '#ffffff' }
    },
    legend: {
      data: ['饲料余量'],
      textStyle: { color: '#8b8ba3' },
      top: '5%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.map(d => d.date.slice(5)),
      axisLine: { lineStyle: { color: '#333' } },
      axisLabel: { color: '#8b8ba3' }
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLine: { lineStyle: { color: '#333' } },
      axisLabel: { color: '#8b8ba3', formatter: '{value}%' },
      splitLine: { lineStyle: { color: 'rgba(0, 212, 255, 0.1)' } }
    },
    series: [
      {
        name: '饲料余量',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { color: '#00d4ff', width: 3 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 212, 255, 0.3)' },
            { offset: 1, color: 'rgba(0, 212, 255, 0.05)' }
          ])
        },
        itemStyle: { color: '#00d4ff' },
        data: data.map(d => d.food_level)
      }
    ]
  }
  
  trendChart.setOption(option)
}

const handleResize = () => {
  lineChart?.resize()
  barChart?.resize()
  pieChart?.resize()
  rankChart?.resize()
  trendChart?.resize()
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  lineChart?.dispose()
  barChart?.dispose()
  pieChart?.dispose()
  rankChart?.dispose()
  trendChart?.dispose()
})
</script>

<style scoped lang="scss">
.statistics-page {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.page-header {
  margin-bottom: 24px;
  
  h2 {
    color: #ffffff;
    font-size: 24px;
    font-weight: 600;
    margin: 0;
  }
}

.charts-row {
  margin-bottom: 20px;
}

.chart-card {
  background: rgba(26, 26, 46, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 12px;
  padding: 20px;
  height: 100%;
}

.chart-header {
  margin-bottom: 16px;
  
  h3 {
    color: #ffffff;
    font-size: 16px;
    font-weight: 600;
    margin: 0;
  }
}

.chart-container {
  width: 100%;
  height: 300px;
}

.chart-container-large {
  width: 100%;
  height: 400px;
}
</style>
