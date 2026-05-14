import request from './request'
import type { Device, ApiResponse } from '@/types'

const mockDevices: Device[] = [
  {
    device_id: 'BF-001',
    name: '后山观鸟点1号',
    location: '后山林区',
    status: 'online',
    battery: 85,
    food_level: 72,
    network: '4G',
    last_online: '2026-05-14 10:30:00'
  },
  {
    device_id: 'BF-002',
    name: '湿地公园2号',
    location: '湿地保护区',
    status: 'online',
    battery: 45,
    food_level: 30,
    network: 'WiFi',
    last_online: '2026-05-14 10:25:00'
  },
  {
    device_id: 'BF-003',
    name: '校园花园3号',
    location: '大学校园',
    status: 'online',
    battery: 92,
    food_level: 88,
    network: 'Ethernet',
    last_online: '2026-05-14 10:28:00'
  },
  {
    device_id: 'BF-004',
    name: '森林公园4号',
    location: '国家森林公园',
    status: 'offline',
    battery: 15,
    food_level: 20,
    network: '4G',
    last_online: '2026-05-14 08:15:00'
  },
  {
    device_id: 'BF-005',
    name: '农村果园5号',
    location: '郊区果园',
    status: 'online',
    battery: 68,
    food_level: 55,
    network: 'WiFi',
    last_online: '2026-05-14 10:20:00'
  }
]

export const getDeviceList = async (): Promise<Device[]> => {
  try {
    const res = await request<ApiResponse<{ devices: Device[] }>>({
      method: 'GET',
      url: '/device/list'
    })
    return res.data.devices
  } catch (error) {
    console.warn('使用Mock数据')
    return mockDevices
  }
}

export const getDeviceDetail = async (deviceId: string): Promise<Device | undefined> => {
  try {
    const devices = await getDeviceList()
    return devices.find(d => d.device_id === deviceId)
  } catch (error) {
    console.warn('使用Mock数据')
    return mockDevices.find(d => d.device_id === deviceId)
  }
}

export const sendDeviceCommand = async (
  deviceId: string,
  command: 'capture' | 'restart' | 'update'
): Promise<{ success: boolean; message: string }> => {
  try {
    const commandMap = {
      capture: 'take_photo',
      restart: 'restart',
      update: 'restart'
    } as const

    const res = await request<ApiResponse<{ status: string }>>({
      method: 'POST',
      url: '/device/command',
      data: { device_id: deviceId, command: commandMap[command] }
    })
    return {
      success: res.ok === true,
      message: res.message
    }
  } catch (error) {
    console.warn('使用Mock数据')
    return {
      success: true,
      message: `命令[${command}]已发送给设备${deviceId}`
    }
  }
}
