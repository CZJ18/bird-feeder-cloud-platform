import request, { resolveAssetUrl } from './request'
import type { BirdEvent, ApiResponse } from '@/types'

export const getBirdEvents = async (params?: {
  device_id?: string
  bird_name?: string
  limit?: number
}): Promise<BirdEvent[]> => {
  const res = await request<ApiResponse<{ events: BirdEvent[] }>>({
    method: 'GET',
    url: '/bird/events',
    params
  })

  return res.data.events.map(event => ({
    ...event,
    image_url: resolveAssetUrl(event.image_url)
  }))
}
