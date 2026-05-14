import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const axiosInstance: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

axiosInstance.interceptors.response.use(
  (response) => {
    const body = response.data

    if (body?.ok === true || body?.code === 200 || body?.code === 0) {
      return body
    }

    if (body?.ok === false) {
      ElMessage.error(body.message || '请求失败')
      return Promise.reject(body)
    }

    if (response.status >= 200 && response.status < 300) {
      return body
    }

    ElMessage.error(body?.message || '请求失败')
    return Promise.reject(body)
  },
  (error) => {
    if (error.response) {
      const status = error.response.status
      switch (status) {
        case 401:
          ElMessage.error('未授权，请重新登录')
          break
        case 403:
          ElMessage.error('拒绝访问')
          break
        case 404:
          ElMessage.error('请求资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(`请求失败: ${status}`)
      }
    } else if (error.request) {
      ElMessage.warning('网络未连接或请求超时，已启用Mock数据')
    } else {
      ElMessage.error('请求配置错误')
    }
    return Promise.reject(error)
  }
)

export const request = async <T = any>(config: AxiosRequestConfig): Promise<T> => {
  return axiosInstance(config) as Promise<T>
}

export const resolveAssetUrl = (url: string) => {
  if (!url || /^https?:\/\//i.test(url)) return url
  const apiRoot = axiosInstance.defaults.baseURL || BASE_URL
  if (apiRoot.startsWith('/')) {
    return url
  }
  const origin = apiRoot.replace(/\/api\/?$/, '')
  return `${origin}${url.startsWith('/') ? url : `/${url}`}`
}

export const setBaseURL = (url: string) => {
  axiosInstance.defaults.baseURL = url
}

export default request
