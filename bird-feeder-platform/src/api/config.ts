import request from './request'
import type { DeviceConfig, ApiResponse } from '@/types'

const mockConfigs: Record<string, DeviceConfig> = {
  'BF-001': {
    device_id: 'BF-001',
    capture_interval: 300,
    confidence_threshold: 0.85,
    upload_image: true,
    night_mode: true,
    low_battery_threshold: 20
  },
  'BF-002': {
    device_id: 'BF-002',
    capture_interval: 600,
    confidence_threshold: 0.80,
    upload_image: true,
    night_mode: false,
    low_battery_threshold: 15
  },
  'BF-003': {
    device_id: 'BF-003',
    capture_interval: 300,
    confidence_threshold: 0.90,
    upload_image: true,
    night_mode: true,
    low_battery_threshold: 25
  },
  'BF-004': {
    device_id: 'BF-004',
    capture_interval: 900,
    confidence_threshold: 0.75,
    upload_image: false,
    night_mode: false,
    low_battery_threshold: 30
  },
  'BF-005': {
    device_id: 'BF-005',
    capture_interval: 300,
    confidence_threshold: 0.85,
    upload_image: true,
    night_mode: true,
    low_battery_threshold: 20
  }
}

export const getDeviceConfig = async (deviceId: string): Promise<DeviceConfig> => {
  try {
    const res = await request<ApiResponse<DeviceConfig>>({
      method: 'GET',
      url: `/device/config/${deviceId}`
    })
    return res.data
  } catch (error) {
    console.warn('使用Mock数据')
    return mockConfigs[deviceId] || {
      device_id: deviceId,
      capture_interval: 300,
      confidence_threshold: 0.85,
      upload_image: true,
      night_mode: true,
      low_battery_threshold: 20
    }
  }
}

export const updateDeviceConfig = async (
  deviceId: string,
  config: Partial<DeviceConfig>
): Promise<{ success: boolean; message: string }> => {
  try {
    const res = await request<ApiResponse<DeviceConfig>>({
      method: 'POST',
      url: `/device/config/${deviceId}`,
      data: config
    })
    return {
      success: res.ok === true,
      message: res.message
    }
  } catch (error) {
    console.warn('使用Mock数据')
    mockConfigs[deviceId] = { ...mockConfigs[deviceId], ...config } as DeviceConfig
    return {
      success: true,
      message: '配置更新成功'
    }
  }
}
