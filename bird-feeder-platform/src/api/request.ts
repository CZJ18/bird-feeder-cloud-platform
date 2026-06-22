import { ElMessage } from 'element-plus'

type RequestMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

export interface FetchRequestConfig {
  url?: string
  method?: RequestMethod
  params?: object
  data?: unknown
  headers?: Record<string, string>
  responseType?: 'json' | 'blob' | 'text'
}

const DEFAULT_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const API_TOKEN =
  import.meta.env.VITE_DASHBOARD_API_TOKEN ||
  localStorage.getItem('dashboard_api_token') ||
  'e7a9341f78ad2c6c1107a3566fac30eb'

let currentBaseURL = DEFAULT_BASE_URL

const buildURL = (url: string, params?: object) => {
  const baseURL = currentBaseURL.replace(/\/$/, '')
  const pathname = url.startsWith('/') ? url : `/${url}`
  const query = new URLSearchParams()

  Object.entries(params || {}).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return
    query.set(key, String(value))
  })

  return `${baseURL}${pathname}${query.size ? `?${query.toString()}` : ''}`
}

const readResponseBody = async (response: Response, responseType?: FetchRequestConfig['responseType']) => {
  if (responseType === 'blob') return response.blob()
  if (responseType === 'text') return response.text()

  const text = await response.text()
  if (!text) return null

  try {
    return JSON.parse(text)
  } catch {
    return text
  }
}

export const request = async <T = any>(config: FetchRequestConfig): Promise<T> => {
  const method = config.method || 'GET'
  const headers: Record<string, string> = {
    Accept: 'application/json',
    'X-API-Token': API_TOKEN,
    ...config.headers
  }

  const init: RequestInit = {
    method,
    headers
  }

  if (config.data !== undefined && method !== 'GET') {
    if (config.data instanceof FormData) {
      init.body = config.data
    } else {
      headers['Content-Type'] = 'application/json'
      init.body = JSON.stringify(config.data)
    }
  }

  try {
    const response = await fetch(buildURL(config.url || '', config.params), init)
    const body = await readResponseBody(response, config.responseType)

    if (!response.ok) {
      const message =
        typeof body === 'object' && body && 'message' in body
          ? String((body as { message?: unknown }).message)
          : `请求失败: ${response.status}`
      ElMessage.error(message)
      return Promise.reject(body || new Error(message))
    }

    if (body && typeof body === 'object') {
      const apiBody = body as { ok?: boolean; code?: number; message?: string }

      if (apiBody.ok === false) {
        ElMessage.error(apiBody.message || '请求失败')
        return Promise.reject(apiBody)
      }

      if (apiBody.code !== undefined && apiBody.code !== 0 && apiBody.code !== 200) {
        ElMessage.error(apiBody.message || '请求失败')
        return Promise.reject(apiBody)
      }
    }

    return body as T
  } catch (error) {
    if (error instanceof TypeError) {
      ElMessage.warning('后端未连接，请检查 API 地址和 FastAPI 服务')
    }
    return Promise.reject(error)
  }
}

export const resolveAssetUrl = (url: string) => {
  if (!url || /^https?:\/\//i.test(url)) return url
  const apiRoot = currentBaseURL
  if (apiRoot.startsWith('/')) return url
  const origin = apiRoot.replace(/\/api\/?$/, '')
  return `${origin}${url.startsWith('/') ? url : `/${url}`}`
}

export const setBaseURL = (url: string) => {
  currentBaseURL = url || DEFAULT_BASE_URL
}

export default request
