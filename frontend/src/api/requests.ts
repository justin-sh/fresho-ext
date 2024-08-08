import {axios} from '@/utils/axios'
import {type User} from "@/api/interfaces";

export const getUserInfo = () => axios.get<User>('/auth/user-info')
export const uploadOrderCsv = (f) => axios.postForm('/api/orders/upload/', {"orderFile":f})