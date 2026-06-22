import request from './request'
import type { Device, ApiResponse } from '@/types'

export const getDeviceList = async (): Promise<Device[]> => {
  const res = await request<ApiResponse<{ devices: Device[] }>>({
    method: 'GET',
    url: '/device/list'
  })
  return res.data.devices
}

export const getDeviceDetail = async (deviceId: string): Promise<Device | undefined> => {
  const devices = await getDeviceList()
  return devices.find(device => device.device_id === deviceId)
}

export const sendDeviceCommand = async (
  deviceId: string,
  command: 'capture' | 'restart' | 'update'
): Promise<{ success: boolean; message: string }> => {
  const commandMap = {
    capture: 'take_photo',
    restart: 'restart',
    update: 'update_config'
  } as const

  const res = await request<ApiResponse<{ status: string }>>({
    method: 'POST',
    url: '/device/command',
    data: { device_id: deviceId, command: commandMap[command] }
  })

  return {
    success: res.ok === true || res.code === 200 || res.code === 0,
    message: res.message
  }
}
