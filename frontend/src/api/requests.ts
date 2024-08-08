import {axios} from '@/utils/axios'
import {type User} from "@/api/interfaces";

export const getUserInfo = () => axios.get<User>('/auth/user-info')
export const uploadOrdersCsv = (f) => axios.postForm('/api/orders/upload/', {"orderFile": f})
export const initOrders = (delivery_date: string) => axios.get('/api/orders/init/', {params: {delivery_date}})