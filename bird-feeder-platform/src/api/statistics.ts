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

const fetchBackendStatistics = async () => {
  const res = await request<ApiResponse<BackendStatistics>>({
    method: 'GET',
    url: '/statistics'
  })
  return res.data
}

export const getStatistics = async (): Promise<Statistics> => {
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
}

export const getDailyRecognitions = async (days: number = 30): Promise<DailyRecognition[]> => {
  const stats = await fetchBackendStatistics()
  return stats.daily_counts.slice(-days)
}

export const getBirdDistribution = async (): Promise<BirdDistribution[]> => {
  const stats = await fetchBackendStatistics()
  return stats.species_counts.map(item => ({
    name: item.name,
    value: item.count
  }))
}

export const getDeviceUploadRank = async (): Promise<DeviceUploadRank[]> => {
  const stats = await fetchBackendStatistics()
  return stats.device_upload_counts
}

export const getFoodLevelTrend = async (deviceId?: string): Promise<Array<{ date: string; device_id: string; food_level: number }>> => {
  const stats = await fetchBackendStatistics()
  return stats.food_level_trend.map(item => ({
    ...item,
    device_id: deviceId || 'all'
  }))
}
