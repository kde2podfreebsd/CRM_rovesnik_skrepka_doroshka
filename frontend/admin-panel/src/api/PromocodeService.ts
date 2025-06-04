import { AxiosResponse } from 'axios';
import $api from "./index.ts";

export interface IPromocode {
    client_chat_id: number;
    type: PromocodeType;
    name: string;
    operational_info: string;
    description: string;
    number: number;
    end_time: string;
    is_activated: boolean;
}
export type PromocodeType =
    | 'ONE_TIME_FREE_MENU_ITEM'
    | 'DISCOUNT_ON_ACCOUNT'
    | 'DISCOUNT_ON_DISH'
    | 'DISCOUNT_FOR_PAID_EVENT'
    | 'FREE_EVENT_TICKET'
    | 'REFILLING_BALANCE'
    | 'PARTY_WITHOUT_DEPOSIT'
    | 'GIFT_FROM_PARTNER'
    | 'CUSTOM';


export default class PromocodeService {

    static async getAll(): Promise<AxiosResponse<IPromocode[]>> {
        return $api.get('promocodes/get_all_promocodes');
    }

    static async create(data: {
        client_chat_id: number;
        type: PromocodeType;
        name: string;
        operational_info: string;
        description: string;
        number: number;
        end_time: string;
        is_activated: boolean;
    }): Promise<AxiosResponse> {
        return $api.post('promocodes/create', {...data});
    }

    static async delete(number: number): Promise<AxiosResponse> {
        return $api.delete(`promocodes/delete/` + number);
    }

    static async getUserPromocodes(id: number): Promise<AxiosResponse<IPromocode[]>> {
        return $api.post(`promocodes/get_user_promocodes/${id}`);
    }

    static async addUserToPromocode(client_chat_id: number, number: number): Promise<AxiosResponse> {
        return $api.patch(`promocodes/add_user_to_promocode`, {client_chat_id, number});
    }

    static activate(number: number): Promise<AxiosResponse> {
        return $api.patch(`promocodes/activate_promocode/` + number);
    }

    static async update(data: {
        client_chat_id: number;
        type: PromocodeType;
        name: string;
        operational_info: string;
        description: string;
        number: number;
        is_activated: boolean;
    }) {
        return $api.patch('promocodes/update/' + data.number, {...data});
    }
}