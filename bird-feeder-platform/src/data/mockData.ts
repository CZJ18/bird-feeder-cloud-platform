export type Tone = 'cyan' | 'green' | 'blue' | 'amber' | 'orange'
export type DeviceState = '在线' | '离线'
export type ReviewStatus = 'pending' | 'approved' | 'rejected'

export interface OverviewStat {
  label: string
  value: string
  unit: string
  icon: 'species' | 'activity' | 'device' | 'weather'
  tone: Tone
  detail: string
}

export interface DashboardMetric {
  label: string
  value: string
  unit: string
  refresh: string
  tone: Tone
  description: string
}

export interface SpeciesBar {
  name: string
  value: number
  latin: string
  confidence: number
  protection: string
}

export interface NetworkNode {
  label: string
  x: number
  y: number
  status: DeviceState
  lastSeen: string
  throughput: string
}

export interface ProtectionStat {
  label: string
  value: string
  detail: string
}

export interface MapPoint {
  name: string
  x: number
  y: number
  heat: number
  deviceId: string
  species: number
  events: number
  status: DeviceState
}

export interface AnnualAreaStat {
  name: string
  value: number
}

export interface VideoCard {
  title: string
  duration: string
  tone: Tone
  camera: string
  species: string
  time: string
  image: string
  description: string
}

export interface DeviceStatusRow {
  deviceId: string
  name: string
  location: string
  status: DeviceState
  lastSeen: string
  temperature: string
  battery: string
  foodLevel: string
  todayEvents: number
}

export interface LowConfidenceRow {
  id: string
  deviceId: string
  species: string
  confidence: string
  time: string
  status: ReviewStatus
  image: string
}

const makeBirdImage = (label: string, mainColor: string, accentColor: string) => {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 500">
      <defs>
        <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#071426"/>
          <stop offset="0.55" stop-color="#0b3042"/>
          <stop offset="1" stop-color="#08111f"/>
        </linearGradient>
        <radialGradient id="glow" cx="58%" cy="42%" r="48%">
          <stop offset="0" stop-color="${accentColor}" stop-opacity="0.62"/>
          <stop offset="1" stop-color="${accentColor}" stop-opacity="0"/>
        </radialGradient>
      </defs>
      <rect width="900" height="500" fill="url(#bg)"/>
      <rect width="900" height="500" fill="url(#glow)"/>
      <path d="M0 350 C160 285 255 390 430 320 C590 256 705 278 900 214 L900 500 L0 500 Z" fill="#0f2f32" opacity="0.92"/>
      <path d="M0 380 C180 332 310 420 512 360 C670 314 760 330 900 282 L900 500 L0 500 Z" fill="#143f35" opacity="0.75"/>
      <g transform="translate(448 132)">
        <ellipse cx="55" cy="94" rx="84" ry="42" fill="${mainColor}"/>
        <path d="M25 82 C-80 22 -168 54 -244 118 C-138 122 -54 128 44 108 Z" fill="${mainColor}" opacity="0.88"/>
        <path d="M92 84 C168 30 238 48 298 104 C220 106 154 112 82 104 Z" fill="${mainColor}" opacity="0.82"/>
        <circle cx="120" cy="70" r="34" fill="${mainColor}"/>
        <path d="M148 68 L210 50 L156 88 Z" fill="#ffd76a"/>
        <circle cx="130" cy="62" r="5" fill="#04101d"/>
        <path d="M52 132 L26 188 M88 132 L112 188" stroke="#ffd76a" stroke-width="9" stroke-linecap="round"/>
      </g>
      <g opacity="0.78">
        <circle cx="92" cy="86" r="3" fill="#35e8ff"/>
        <circle cx="148" cy="122" r="2" fill="#57ffad"/>
        <circle cx="760" cy="86" r="3" fill="#35e8ff"/>
        <circle cx="812" cy="144" r="2" fill="#57ffad"/>
      </g>
      <text x="40" y="64" fill="#ecfbff" font-family="Arial, sans-serif" font-size="34" font-weight="700">${label}</text>
      <text x="40" y="102" fill="#87a4ba" font-family="Arial, sans-serif" font-size="18">BirdCam intelligent monitoring snapshot</text>
    </svg>
  `
  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`
}

const egretImage = makeBirdImage('EGRET MOMENT', '#f2fbff', '#35e8ff')
const magpieImage = makeBirdImage('MAGPIE GROUP', '#8fb4c9', '#57ffad')
const swallowImage = makeBirdImage('SWALLOW TRACK', '#243c4c', '#ffd76a')
const reviewImage = makeBirdImage('LOW CONFIDENCE', '#b8c8d6', '#ff5f86')

export const dashboardMetrics: DashboardMetric[] = [
  { label: '累计识别总数', value: '23,456', unit: '条', refresh: '30秒', tone: 'cyan', description: '统计所有高置信度 leave 事件。' },
  { label: '累计物种数', value: '28', unit: '种', refresh: '30秒', tone: 'green', description: '统计事件表中不同 class_id。' },
  { label: '在线设备数', value: '3', unit: '台', refresh: '5分钟', tone: 'blue', description: '最近 5 分钟内有状态上报的设备。' },
  { label: '今日新增', value: '128', unit: '条', refresh: '30秒', tone: 'amber', description: '今天发生的有效 leave 事件。' },
  { label: '今日活跃设备', value: '3', unit: '台', refresh: '1分钟', tone: 'cyan', description: '今天有事件或状态上报的设备。' },
  { label: '待审核图片', value: '6', unit: '张', refresh: '手动', tone: 'orange', description: '低置信度图片表中 pending 记录。' },
  { label: '平均置信度', value: '92.4', unit: '%', refresh: '30秒', tone: 'green', description: '高置信度事件 confidence 平均值。' },
  { label: '今日观测物种数', value: '5', unit: '种', refresh: '30秒', tone: 'blue', description: '今天事件中不同 class_id 数量。' }
]

export const overviewStats: OverviewStat[] = [
  { label: '累计物种', value: '28', unit: '种', icon: 'species', tone: 'cyan', detail: '已归档的鸟类物种数量，来自高置信度 leave 事件。' },
  { label: '活跃物种', value: '5', unit: '种', icon: 'activity', tone: 'green', detail: '今天至少出现一次有效识别记录的物种。' },
  { label: '在线设备', value: '3', unit: '台', icon: 'device', tone: 'blue', detail: '最近 5 分钟内有状态上报的采集设备。' },
  { label: '实时温度', value: '28', unit: '°C', icon: 'weather', tone: 'amber', detail: '来自在线设备状态上报的平均 CPU 温度。' }
]

export const speciesBars: SpeciesBar[] = [
  { name: '白鹭', value: 45, latin: 'Egretta garzetta', confidence: 96, protection: '省级保护' },
  { name: '麻雀', value: 33, latin: 'Passer montanus', confidence: 91, protection: '常见留鸟' },
  { name: '喜鹊', value: 29, latin: 'Pica serica', confidence: 94, protection: '常见留鸟' },
  { name: '乌鸫', value: 23, latin: 'Turdus mandarinus', confidence: 90, protection: '常见留鸟' },
  { name: '斑鸠', value: 18, latin: 'Spilopelia chinensis', confidence: 89, protection: '常见留鸟' },
  { name: '燕子', value: 12, latin: 'Hirundo rustica', confidence: 93, protection: '夏候鸟' },
  { name: '杜鹃', value: 8, latin: 'Cuculus canorus', confidence: 88, protection: '季节性观测' }
]

export const networkNodes: NetworkNode[] = [
  { label: '摄像头监测点 1', x: 18, y: 24, status: '在线', lastSeen: '08:56:21', throughput: '2.4 MB/s' },
  { label: '摄像头监测点 2', x: 78, y: 23, status: '在线', lastSeen: '08:55:44', throughput: '1.9 MB/s' },
  { label: '鸟类识别终端 1', x: 16, y: 74, status: '在线', lastSeen: '08:56:03', throughput: '3.1 MB/s' },
  { label: '鸟类识别终端 2', x: 80, y: 72, status: '离线', lastSeen: '08:28:10', throughput: '0 MB/s' }
]

export const protectionStats: ProtectionStat[] = [
  { label: '一级保护', value: '2', detail: '需重点跟踪的珍稀保护鸟类。' },
  { label: '二级保护', value: '3', detail: '纳入重点生态监测的保护鸟类。' },
  { label: '省级保护', value: '3', detail: '地方保护名录内的观测记录。' },
  { label: '普通鸟类', value: '2,345', detail: '校园常见鸟类有效识别事件。' }
]

export const mapPoints: MapPoint[] = [
  { name: '艺苑小区', x: 22, y: 34, heat: 92, deviceId: 'CAM-01', species: 12, events: 680, status: '在线' },
  { name: '鸟人湖东岸', x: 45, y: 57, heat: 76, deviceId: 'CAM-02', species: 9, events: 512, status: '在线' },
  { name: '鸟人湖西岸', x: 58, y: 48, heat: 68, deviceId: 'CAM-03', species: 8, events: 420, status: '在线' },
  { name: '修业湖湿地', x: 67, y: 64, heat: 84, deviceId: 'CAM-04', species: 11, events: 604, status: '在线' },
  { name: '修业湖林缘', x: 74, y: 36, heat: 58, deviceId: 'CAM-05', species: 7, events: 288, status: '离线' },
  { name: '十教学楼北侧', x: 36, y: 26, heat: 46, deviceId: 'CAM-06', species: 5, events: 194, status: '在线' },
  { name: '十教学楼南侧', x: 52, y: 24, heat: 52, deviceId: 'CAM-07', species: 6, events: 236, status: '在线' }
]

export const years = [2021, 2022, 2023, 2024, 2025]

export const annualAreaStats: AnnualAreaStat[] = [
  { name: '艺苑小区', value: 380 },
  { name: '梅林', value: 250 },
  { name: '七教学楼', value: 130 },
  { name: '十教学楼', value: 50 },
  { name: '守望湖', value: 380 },
  { name: '修业湖', value: 250 },
  { name: '鸟人湖', value: 130 },
  { name: '农大林带', value: 50 }
]

export const videoCards: VideoCard[] = [
  {
    title: '白鹭栖息瞬间回放',
    duration: '0:22',
    tone: 'cyan',
    camera: 'CAM-02',
    species: '白鹭',
    time: '2026-06-16 08:42',
    image: egretImage,
    description: '鸟人湖东岸捕捉到白鹭短暂停留，置信度 96%。'
  },
  {
    title: '灰喜鹊群居瞬间回放',
    duration: '0:22',
    tone: 'green',
    camera: 'CAM-04',
    species: '喜鹊',
    time: '2026-06-16 09:18',
    image: magpieImage,
    description: '修业湖湿地区域出现小规模群体活动，连续触发 7 条 leave 事件。'
  },
  {
    title: '燕子觅食视频',
    duration: '0:22',
    tone: 'amber',
    camera: 'CAM-06',
    species: '燕子',
    time: '2026-06-16 10:03',
    image: swallowImage,
    description: '十教学楼北侧记录到燕子低空觅食，轨迹完整。'
  }
]

export const behaviorData = {
  days: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
  observations: [72, 96, 81, 118, 132, 104, 145],
  activity: [36, 54, 48, 72, 82, 64, 91]
}

export const populationShare = [
  { name: '白鹭', value: 56 },
  { name: '麻雀', value: 51 },
  { name: '喜鹊', value: 40 },
  { name: '乌鸫', value: 25 },
  { name: '斑鸠', value: 25 },
  { name: '燕子', value: 25 },
  { name: '杜鹃', value: 25 }
]

export const monthlyTrends = {
  months: Array.from({ length: 12 }, (_, index) => `${index + 1}月`),
  series: [
    { name: '白鹭', data: [32, 38, 46, 62, 81, 88, 76, 72, 68, 54, 42, 36] },
    { name: '麻雀', data: [72, 69, 74, 78, 82, 86, 88, 84, 79, 76, 73, 70] },
    { name: '喜鹊', data: [42, 46, 51, 58, 62, 68, 73, 71, 64, 56, 49, 44] },
    { name: '燕子', data: [16, 24, 44, 68, 86, 92, 88, 76, 48, 24, 14, 12] },
    { name: '斑鸠', data: [35, 36, 38, 42, 45, 48, 51, 49, 46, 43, 39, 36] }
  ]
}

export const deviceStatusRows: DeviceStatusRow[] = [
  { deviceId: 'CAM-01', name: '摄像头 1 号', location: '艺苑小区', status: '在线', lastSeen: '08:56:21', temperature: '27.8°C', battery: '86%', foodLevel: '72%', todayEvents: 31 },
  { deviceId: 'CAM-02', name: '摄像头 2 号', location: '鸟人湖东岸', status: '在线', lastSeen: '08:55:44', temperature: '28.3°C', battery: '81%', foodLevel: '68%', todayEvents: 42 },
  { deviceId: 'EDGE-01', name: '识别终端 1 号', location: '修业湖湿地', status: '在线', lastSeen: '08:56:03', temperature: '31.2°C', battery: '外接', foodLevel: '64%', todayEvents: 55 },
  { deviceId: 'EDGE-02', name: '识别终端 2 号', location: '修业湖林缘', status: '离线', lastSeen: '08:28:10', temperature: '--', battery: '42%', foodLevel: '51%', todayEvents: 0 }
]

export const lowConfidenceRows: LowConfidenceRow[] = [
  { id: 'LC-240616-001', deviceId: 'CAM-02', species: '白鹭', confidence: '68%', time: '2026-06-16 08:43', status: 'pending', image: reviewImage },
  { id: 'LC-240616-002', deviceId: 'CAM-04', species: '喜鹊', confidence: '61%', time: '2026-06-16 09:22', status: 'pending', image: reviewImage },
  { id: 'LC-240616-003', deviceId: 'CAM-06', species: '燕子', confidence: '57%', time: '2026-06-16 10:08', status: 'pending', image: reviewImage },
  { id: 'LC-240616-004', deviceId: 'CAM-01', species: '斑鸠', confidence: '66%', time: '2026-06-16 10:37', status: 'approved', image: reviewImage }
]
