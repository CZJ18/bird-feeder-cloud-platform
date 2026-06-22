import request from './request'
import type { SystemLog, ApiResponse } from '@/types'

export const getLogs = async (params?: {
  device_id?: string
  type?: 'INFO' | 'WARNING' | 'ERROR'
  page?: number
  page_size?: number
}): Promise<{ items: SystemLog[]; total: number }> => {
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
}
