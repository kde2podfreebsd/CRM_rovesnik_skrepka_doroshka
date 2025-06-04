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
  static async getAll(chatId: number): Promise<AxiosResponse<IRes>> {
    return $api.post(`/reservation/get_all_reserved_statuses_by_chat_id`, {
      chat_id: chatId,
      bar_id: 2
    })
  }

  static async create(data: {
    client_chat_id: number
    table_uuid: string
    reservation_start: string
    deposit: number
  }): Promise<AxiosResponse> {
    return $api.post('/reservation/create', { ...data })
  }

  static async cancel(reserve_id: string): Promise<AxiosResponse> {
    return $api.post('/reservation/cancel', {
      reserve_id,
      cancel_reason: 'Other',
    })
  }

  static async update(data: {
    reserve_id: string
    reservation_start: string
  }): Promise<AxiosResponse> {
    return $api.post('/reservation/update', { ...data })
  }

  static async uuid(
    order_uuid: string,
  ): Promise<AxiosResponse<IReservation[]>> {
    return $api.get(`/reservation/get_by_order_uuid/${order_uuid}`)
  }

  static async checkAbility(
    reserve_id: string,
  ): Promise<AxiosResponse<IReservation[]>> {
    return $api.get(`/reservation/check_change_ability?reserve_id=${reserve_id}`)
  }
  static async getExpired(chat_id: number): Promise<AxiosResponse<IRes>> {
    return $api.post(`/reservation/get_expired_and_cancelled_by_chat_id`, {
      chat_id: chat_id,
        bar_id: 2
    })
  }
}
