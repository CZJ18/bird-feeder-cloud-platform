import request, { resolveAssetUrl } from './request'
import type { BirdEvent, ApiResponse } from '@/types'

const mockBirdEvents: BirdEvent[] = [
  {
    id: 1,
    device_id: 'BF-001',
    bird_name: '麻雀',
    confidence: 0.96,
    image_url: 'https://via.placeholder.com/200x150/4CAF50/FFFFFF?text=Sparrow',
    battery: 85,
    food_level: 72,
    created_at: '2026-05-14 10:30:00'
  },
  {
    id: 2,
    device_id: 'BF-001',
    bird_name: '燕子',
    confidence: 0.89,
    image_url: 'https://via.placeholder.com/200x150/2196F3/FFFFFF?text=Swallow',
    battery: 84,
    food_level: 70,
    created_at: '2026-05-14 10:25:00'
  },
  {
    id: 3,
    device_id: 'BF-002',
    bird_name: '鸽子',
    confidence: 0.92,
    image_url: 'https://via.placeholder.com/200x150/9C27B0/FFFFFF?text=Dove',
    battery: 45,
    food_level: 30,
    created_at: '2026-05-14 10:20:00'
  },
  {
    id: 4,
    device_id: 'BF-003',
    bird_name: '麻雀',
    confidence: 0.97,
    image_url: 'https://via.placeholder.com/200x150/4CAF50/FFFFFF?text=Sparrow',
    battery: 92,
    food_level: 88,
    created_at: '2026-05-14 10:15:00'
  },
  {
    id: 5,
    device_id: 'BF-005',
    bird_name: '啄木鸟',
    confidence: 0.85,
    image_url: 'https://via.placeholder.com/200x150/F44336/FFFFFF?text=Woodpecker',
    battery: 68,
    food_level: 55,
    created_at: '2026-05-14 10:10:00'
  },
  {
    id: 6,
    device_id: 'BF-001',
    bird_name: '画眉',
    confidence: 0.91,
    image_url: 'https://via.placeholder.com/200x150/FF9800/FFFFFF?text=Hwamei',
    battery: 83,
    food_level: 68,
    created_at: '2026-05-14 10:05:00'
  },
  {
    id: 7,
    device_id: 'BF-002',
    bird_name: '斑鸠',
    confidence: 0.88,
    image_url: 'https://via.placeholder.com/200x150/795548/FFFFFF?text=Turtledove',
    battery: 44,
    food_level: 28,
    created_at: '2026-05-14 10:00:00'
  },
  {
    id: 8,
    device_id: 'BF-003',
    bird_name: '翠鸟',
    confidence: 0.93,
    image_url: 'https://via.placeholder.com/200x150/00BCD4/FFFFFF?text=Kingfisher',
    battery: 91,
    food_level: 86,
    created_at: '2026-05-14 09:55:00'
  }
]

export const getBirdEvents = async (params?: {
  device_id?: string
  bird_name?: string
  limit?: number
}): Promise<BirdEvent[]> => {
  try {
    const res = await request<ApiResponse<{ events: BirdEvent[] }>>({
      method: 'GET',
      url: '/bird/events',
      params
    })
    let events = res.data.events.map(event => ({
      ...event,
      image_url: resolveAssetUrl(event.image_url)
    }))
    if (params?.device_id) {
      events = events.filter(e => e.device_id === params.device_id)
    }
    if (params?.bird_name) {
      events = events.filter(e => e.bird_name.includes(params.bird_name!))
    }
    if (params?.limit) {
      events = events.slice(0, params.limit)
    }
    return events
  } catch (error) {
    console.warn('使用Mock数据')
    let events = [...mockBirdEvents]
    if (params?.device_id) {
      events = events.filter(e => e.device_id === params.device_id)
    }
    if (params?.bird_name) {
      events = events.filter(e => e.bird_name.includes(params.bird_name!))
    }
    if (params?.limit) {
      events = events.slice(0, params.limit)
    }
    return events
  }
}
