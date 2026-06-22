import request from './request'
import type { DeviceConfig, ApiResponse } from '@/types'

export const getDeviceConfig = async (deviceId: string): Promise<DeviceConfig> => {
  const res = await request<ApiResponse<DeviceConfig>>({
    method: 'GET',
    url: `/device/config/${deviceId}`
  })
  return res.data
}

export const updateDeviceConfig = async (
  deviceId: string,
  config: Partial<DeviceConfig>
): Promise<{ success: boolean; message: string }> => {
  const res = await request<ApiResponse<DeviceConfig>>({
    method: 'POST',
    url: `/device/config/${deviceId}`,
    data: config
  })
  return {
    success: res.ok === true || res.code === 200 || res.code === 0,
    message: res.message
  }
}
