import { AxiosResponse } from 'axios'
import $api from './index'

interface IRes {
  Status: string
  Message: ITable[]
}

export interface ITable {
  bar_id: number
  storey: number
  table_id: number
  table_uuid: string
  terminal_group_uuid: string
  capacity: number
  is_available: boolean
}

export default class TablesService {
  static async getAll(
    date: string,
    capacity: number,
  ): Promise<AxiosResponse<IRes>> {
    return $api.post('/table/get_available_tables_by_capacity_and_time', {
      bar_id: 1,
      datetime: date,
      capacity: capacity,
    })
  }

  static async getByUuid(tableId: string): Promise<AxiosResponse> {
    return $api.get(`/table/get_by_uuid/${tableId}`)
  }

  static async update(data: ITable): Promise<AxiosResponse> {
    return $api.post('/table/update', { ...data })
  }

  static async checkAvailability(table_uuid, datetime): Promise<AxiosResponse> {
    return $api.post('/table/check_availability', {
      table_uuid: table_uuid,
      datetime: datetime,
    })
  }
}
