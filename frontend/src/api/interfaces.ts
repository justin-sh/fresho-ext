import {type GenericAbortSignal} from "axios";

export interface User {
    id: number
    name: string
    passwd?: string
    sec_tip?: string
    sec_ans?: string
}

export interface OrderFilter {
    delivery_date: string
    customer: string
    product: string
    status: string[]
}

export interface OptionConfig{
    signal?: GenericAbortSignal
}