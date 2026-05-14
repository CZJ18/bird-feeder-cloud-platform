import request from './request'
import type { SystemLog, ApiResponse } from '@/types'

const mockLogs: SystemLog[] = [
  { id: 1, device_id: 'BF-001', type: 'INFO', message: '设备上线', created_at: '2026-05-14 10:30:00' },
  { id: 2, device_id: 'BF-001', type: 'INFO', message: '识别到鸟类: 麻雀, 置信度: 0.96', created_at: '2026-05-14 10:30:01' },
  { id: 3, device_id: 'BF-002', type: 'WARNING', message: '电池电量低于30%', created_at: '2026-05-14 10:25:00' },
  { id: 4, device_id: 'BF-002', type: 'INFO', message: '识别到鸟类: 鸽子, 置信度: 0.92', created_at: '2026-05-14 10:20:00' },
  { id: 5, device_id: 'BF-003', type: 'INFO', message: '设备上线', created_at: '2026-05-14 10:28:00' },
  { id: 6, device_id: 'BF-003', type: 'INFO', message: '识别到鸟类: 麻雀, 置信度: 0.97', created_at: '2026-05-14 10:15:00' },
  { id: 7, device_id: 'BF-004', type: 'ERROR', message: '设备离线，网络连接失败', created_at: '2026-05-14 08:15:00' },
  { id: 8, device_id: 'BF-004', type: 'WARNING', message: '电池电量低于20%', created_at: '2026-05-14 08:10:00' },
  { id: 9, device_id: 'BF-005', type: 'INFO', message: '设备上线', created_at: '2026-05-14 10:20:00' },
  { id: 10, device_id: 'BF-005', type: 'INFO', message: '识别到鸟类: 啄木鸟, 置信度: 0.85', created_at: '2026-05-14 10:10:00' },
  { id: 11, device_id: 'BF-001', type: 'INFO', message: '图片上传成功', created_at: '2026-05-14 10:30:02' },
  { id: 12, device_id: 'BF-002', type: 'WARNING', message: '饲料余量低于35%', created_at: '2026-05-14 10:15:00' },
  { id: 13, device_id: 'BF-003', type: 'INFO', message: '配置更新成功', created_at: '2026-05-14 09:50:00' },
  { id: 14, device_id: 'BF-004', type: 'ERROR', message: '识别模型加载失败', created_at: '2026-05-14 08:00:00' },
  { id: 15, device_id: 'BF-005', type: 'INFO', message: '识别到鸟类: 画眉, 置信度: 0.88', created_at: '2026-05-14 09:45:00' }
]

export const getLogs = async (params?: {
  device_id?: string
  type?: 'INFO' | 'WARNING' | 'ERROR'
  page?: number
  page_size?: number
}): Promise<{ items: SystemLog[]; total: number }> => {
  try {
    const res = await request<ApiResponse<{ logs: SystemLog[] }>>({
      method: 'GET',
      url: '/device/logs',
      params: {
        device_id: params?.device_id,
        type: params?.type
      }
    })
    const page = params?.page || 1
    const pageSize = params?.page_size || 20
    const start = (page - 1) * pageSize
    return {
      items: res.data.logs.slice(start, start + pageSize),
      total: res.data.logs.length
    }
  } catch (error) {
    console.warn('使用Mock数据')
    let filtered = [...mockLogs]
    
    if (params?.device_id) {
      filtered = filtered.filter(log => log.device_id === params.device_id)
    }
    if (params?.type) {
      filtered = filtered.filter(log => log.type === params.type)
    }
    
    const page = params?.page || 1
    const pageSize = params?.page_size || 20
    const start = (page - 1) * pageSize
    
    return {
      items: filtered.slice(start, start + pageSize),
      total: filtered.length
    }
  }
}
