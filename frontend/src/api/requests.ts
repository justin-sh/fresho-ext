import {axios} from '@/utils/axios'
import {type OptionConfig, type OrderFilter, type User} from "@/api/interfaces";

export const getUserInfo = () => axios.get<User>('/auth/user-info')
// @ts-ignore
export const uploadOrdersCsv = (f) => axios.postForm('/api/orders/upload/', {"orderFile": f})
export const uploadOrdersDetailCsv = (f) => axios.postForm('/api/orders/detail-upload/', {"orderFile": f})
export const initOrders = (delivery_date: string) => axios.get('/api/orders/init/', {params: {delivery_date}})
export const getOrdersWithFilters = (params: OrderFilter, options?: OptionConfig) => axios.get('/api/orders/', {params, ...options})