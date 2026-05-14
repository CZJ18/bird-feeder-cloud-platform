import request from './request'
import type {
  Statistics,
  DailyRecognition,
  BirdDistribution,
  DeviceUploadRank,
  ApiResponse,
  Device,
  HistoryRecord,
  PaginatedResponse
} from '@/types'

interface BackendStatistics {
  daily_counts: DailyRecognition[]
  species_counts: Array<{ name: string; count: number }>
  device_upload_counts: DeviceUploadRank[]
  food_level_trend: Array<{ date: string; food_level: number }>
}

const mockStatistics: Statistics = {
  total_devices: 5,
  online_devices: 4,
  today_recognitions: 128,
  today_images: 45,
  total_bird_species: 12,
  average_confidence: 0.91
}

const mockDailyRecognitions: DailyRecognition[] = Array.from({ length: 30 }, (_, i) => ({
  date: new Date(2026, 4, 14 - 29 + i).toISOString().split('T')[0],
  count: Math.floor(Math.random() * 100) + 50
}))

const mockBirdDistribution: BirdDistribution[] = [
  { name: 'Sparrow', value: 320 },
  { name: 'Swallow', value: 186 },
  { name: 'Dove', value: 145 },
  { name: 'Hwamei', value: 98 },
  { name: 'Turtledove', value: 76 },
  { name: 'Kingfisher', value: 54 },
  { name: 'Other', value: 121 }
]

const mockDeviceUploadRank: DeviceUploadRank[] = [
  { device_id: 'BF-001', device_name: 'Back Hill Feeder 1', upload_count: 1250 },
  { device_id: 'BF-003', device_name: 'Campus Garden Feeder 3', upload_count: 980 },
  { device_id: 'BF-002', device_name: 'Wetland Park Feeder 2', upload_count: 765 },
  { device_id: 'BF-005', device_name: 'Orchard Feeder 5', upload_count: 543 },
  { device_id: 'BF-004', device_name: 'Forest Park Feeder 4', upload_count: 320 }
]

const fetchBackendStatistics = async () => {
  const res = await request<ApiResponse<BackendStatistics>>({
    method: 'GET',
    url: '/statistics'
  })
  return res.data
}

export const getStatistics = async (): Promise<Statistics> => {
  try {
    const [stats, devicesRes, historyRes] = await Promise.all([
      fetchBackendStatistics(),
      request<ApiResponse<{ devices: Device[] }>>({
        method: 'GET',
        url: '/device/list'
      }),
      request<ApiResponse<{
        total: number
        records: HistoryRecord[]
        summary: PaginatedResponse<HistoryRecord>['summary']
      }>>({
        method: 'GET',
        url: '/bird/history',
        params: { page: 1, page_size: 1 }
      })
    ])

    const today = new Date().toISOString().split('T')[0]
    const todayCount = stats.daily_counts.find(item => item.date === today)?.count || 0
    const devices = devicesRes.data.devices

    return {
      total_devices: devices.length,
      online_devices: devices.filter(device => device.status === 'online').length,
      today_recognitions: todayCount,
      today_images: todayCount,
      total_bird_species: stats.species_counts.length,
      average_confidence: historyRes.data.summary?.avg_confidence || 0
    }
  } catch (error) {
    console.warn('浣跨敤Mock鏁版嵁')
    return mockStatistics
  }
}

export const getDailyRecognitions = async (days: number = 30): Promise<DailyRecognition[]> => {
  try {
    const stats = await fetchBackendStatistics()
    return stats.daily_counts.slice(-days)
  } catch (error) {
    console.warn('浣跨敤Mock鏁版嵁')
    return mockDailyRecognitions.slice(-days)
  }
}

export const getBirdDistribution = async (): Promise<BirdDistribution[]> => {
  try {
    const stats = await fetchBackendStatistics()
    return stats.species_counts.map(item => ({
      name: item.name,
      value: item.count
    }))
  } catch (error) {
    console.warn('浣跨敤Mock鏁版嵁')
    return mockBirdDistribution
  }
}

export const getDeviceUploadRank = async (): Promise<DeviceUploadRank[]> => {
  try {
    const stats = await fetchBackendStatistics()
    return stats.device_upload_counts
  } catch (error) {
    console.warn('浣跨敤Mock鏁版嵁')
    return mockDeviceUploadRank
  }
}

export const getFoodLevelTrend = async (deviceId?: string): Promise<any[]> => {
  try {
    const stats = await fetchBackendStatistics()
    return stats.food_level_trend.map(item => ({
      ...item,
      device_id: deviceId || 'all'
    }))
  } catch (error) {
    console.warn('浣跨敤Mock鏁版嵁')
    return Array.from({ length: 7 }, (_, i) => ({
      date: new Date(2026, 4, 14 - 6 + i).toISOString().split('T')[0],
      device_id: deviceId || 'BF-001',
      food_level: 100 - i * 10 + Math.floor(Math.random() * 20)
    }))
  }
}
