export interface Device {
  device_id: string
  name: string
  location: string
  status: 'online' | 'offline'
  battery: number
  food_level: number
  network: '4G' | 'WiFi' | 'Ethernet'
  last_online: string
}

export interface BirdEvent {
  id: number
  device_id: string
  bird_name: string
  class_id?: number | null
  track_id?: number | null
  event_type?: string | null
  confidence: number
  image_url: string
  video_path?: string
  box?: {
    x1: number
    y1: number
    x2: number
    y2: number
  }
  temperature?: number | null
  humidity?: number | null
  battery: number
  food_level: number
  created_at: string
}

export interface HistoryRecord extends BirdEvent {
  location: string
}

export interface DeviceConfig {
  device_id: string
  capture_interval: number
  confidence_threshold: number
  upload_image: boolean
  night_mode: boolean
  low_battery_threshold: number
}

export interface SystemLog {
  id: number
  device_id: string
  type: 'INFO' | 'WARNING' | 'ERROR'
  message: string
  created_at: string
}

export interface Statistics {
  total_devices: number
  online_devices: number
  today_recognitions: number
  today_images: number
  total_bird_species: number
  average_confidence: number
}

export interface DailyRecognition {
  date: string
  count: number
}

export interface BirdDistribution {
  name: string
  value: number
}

export interface DeviceUploadRank {
  device_id: string
  device_name: string
  upload_count: number
}

export interface ApiResponse<T = any> {
  ok?: boolean
  code?: number
  message: string
  data: T
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  summary?: {
    total_count: number
    species_count: number
    today_count: number
    avg_confidence: number
  }
}

export interface FilterParams {
  device_id?: string
  bird_name?: string
  start_date?: string
  end_date?: string
  min_confidence?: number
  max_confidence?: number
  page?: number
  page_size?: number
}
