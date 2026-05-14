import request, { resolveAssetUrl } from './request'
import type { HistoryRecord, FilterParams, PaginatedResponse, ApiResponse } from '@/types'

const mockHistoryRecords: HistoryRecord[] = Array.from({ length: 100 }, (_, i) => {
  const birds = ['麻雀', '燕子', '鸽子', '画眉', '斑鸠', '翠鸟', '啄木鸟', '鹦鹉', '乌鸦', '喜鹊']
  const devices = ['BF-001', 'BF-002', 'BF-003', 'BF-004', 'BF-005']
  const locations = ['后山林区', '湿地保护区', '大学校园', '国家森林公园', '郊区果园']
  const randomDate = new Date(2026, 4, Math.floor(Math.random() * 14) + 1, Math.floor(Math.random() * 24), Math.floor(Math.random() * 60))
  
  return {
    id: i + 1,
    device_id: devices[Math.floor(Math.random() * devices.length)],
    bird_name: birds[Math.floor(Math.random() * birds.length)],
    confidence: 0.75 + Math.random() * 0.24,
    image_url: `https://via.placeholder.com/200x150/666666/FFFFFF?text=Bird+${i + 1}`,
    battery: Math.floor(Math.random() * 100),
    food_level: Math.floor(Math.random() * 100),
    location: locations[Math.floor(Math.random() * locations.length)],
    created_at: randomDate.toISOString().replace('T', ' ').substring(0, 19)
  }
}).sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

export const getHistoryRecords = async (
  params: FilterParams
): Promise<PaginatedResponse<HistoryRecord>> => {
  try {
    const res = await request<ApiResponse<{
      total: number
      records: HistoryRecord[]
      summary: PaginatedResponse<HistoryRecord>['summary']
    }>>({
      method: 'GET',
      url: '/bird/history',
      params: {
        ...params,
        start_time: params.start_date,
        end_time: params.end_date,
        start_date: undefined,
        end_date: undefined
      }
    })
    return {
      items: res.data.records.map(record => ({
        ...record,
        image_url: resolveAssetUrl(record.image_url)
      })),
      total: res.data.total,
      page: params.page || 1,
      page_size: params.page_size || 10,
      summary: res.data.summary
    }
  } catch (error) {
    console.warn('使用Mock数据')
    let filtered = [...mockHistoryRecords]
    
    if (params.device_id) {
      filtered = filtered.filter(r => r.device_id === params.device_id)
    }
    if (params.bird_name) {
      filtered = filtered.filter(r => r.bird_name.includes(params.bird_name!))
    }
    if (params.start_date) {
      filtered = filtered.filter(r => r.created_at >= params.start_date!)
    }
    if (params.end_date) {
      filtered = filtered.filter(r => r.created_at <= params.end_date!)
    }
    if (params.min_confidence !== undefined) {
      filtered = filtered.filter(r => r.confidence >= params.min_confidence!)
    }
    if (params.max_confidence !== undefined) {
      filtered = filtered.filter(r => r.confidence <= params.max_confidence!)
    }
    
    const page = params.page || 1
    const pageSize = params.page_size || 10
    const start = (page - 1) * pageSize
    const end = start + pageSize
    
    return {
      items: filtered.slice(start, end),
      total: filtered.length,
      page,
      page_size: pageSize
    }
  }
}

export const exportHistoryCSV = async (params: FilterParams): Promise<string> => {
  try {
    const res = await request<ApiResponse<string>>({
      method: 'GET',
      url: '/bird/history/export',
      params,
      responseType: 'blob'
    })
    return URL.createObjectURL(new Blob([res.data]))
  } catch (error) {
    console.warn('使用Mock数据')
    const records = mockHistoryRecords
    const headers = ['ID', '设备ID', '鸟类名称', '置信度', '电池', '饲料余量', '位置', '时间']
    const rows = records.map(r => [
      r.id,
      r.device_id,
      r.bird_name,
      r.confidence.toFixed(2),
      r.battery,
      r.food_level,
      r.location,
      r.created_at
    ])
    
    const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n')
    return URL.createObjectURL(new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8' }))
  }
}
