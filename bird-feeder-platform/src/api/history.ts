import request, { resolveAssetUrl } from './request'
import type { HistoryRecord, FilterParams, PaginatedResponse, ApiResponse } from '@/types'

export const getHistoryRecords = async (
  params: FilterParams
): Promise<PaginatedResponse<HistoryRecord>> => {
  const res = await request<ApiResponse<{
    total: number
    records: HistoryRecord[]
    summary: PaginatedResponse<HistoryRecord>['summary']
  }>>({
    method: 'GET',
    url: '/bird/history',
    params: {
      ...params,
      start_time: params.start_date,
      end_time: params.end_date,
      start_date: undefined,
      end_date: undefined
    }
  })

  return {
    items: res.data.records.map(record => ({
      ...record,
      image_url: resolveAssetUrl(record.image_url)
    })),
    total: res.data.total,
    page: params.page || 1,
    page_size: params.page_size || 10,
    summary: res.data.summary
  }
}

export const exportHistoryCSV = async (params: FilterParams): Promise<string> => {
  const blob = await request<Blob>({
    method: 'GET',
    url: '/bird/history/export',
    params,
    responseType: 'blob'
  })
  return URL.createObjectURL(blob)
}
