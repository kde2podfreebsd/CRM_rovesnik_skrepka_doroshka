import { AxiosResponse } from 'axios'
import $api from './index'

interface IRes {
    Status: string
    Message: IReservation[]
}

export interface IReservation {
    client_chat_id: number
    table_uuid: string
    reserve_id: string
    reservation_start: string
    status?: string
    deposit: number
    order_uuid?: string
}

export default class ReservationService {
    static async getAll(): Promise<AxiosResponse<IRes>> {
        return $api.get(`reservation/get_all/`)
    }

    static async create(data: {
        client_chat_id: number
        table_uuid: string
        reservation_start: string
        deposit: number
        order_uuid: string
    }): Promise<AxiosResponse> {
        return $api.post('reservation/create', { ...data })
    }

    static async cancel(reserve_id: string): Promise<AxiosResponse> {
        return $api.post('reservation/cancel', {
            reserve_id,
            cancel_reason: 'Other',
        })
    }

    static async update(data: {
        reserve_id: string
        reservation_start: string
        client_chat_id: number
        table_uuid: string
        deposit: number
    }): Promise<AxiosResponse> {
        return $api.post('reservation/update', { ...data })
    }

    static async uuid(
        order_uuid: string,
    ): Promise<AxiosResponse<IReservation[]>> {
        return $api.get(`reservation/get_by_order_uuid/${order_uuid}`)
    }

    static async delete(reservation_id: string): Promise<AxiosResponse> {
        return $api.delete(`reservation/delete/${reservation_id}`)
    }

    static async getUserReservaations(chat_id: number): Promise<AxiosResponse<IReservation[]>> {
        return $api.post(`reservation/get_all_by_chat_id/${chat_id}`)
    }
}
