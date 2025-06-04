import { AxiosResponse } from 'axios';
import $api from "./index.ts";

export interface IPromotion {
    id: number;
    channel_link: string;
    promotion_text: string;
    promocode_type: 'ONE_TIME_FREE_MENU_ITEM';
    short_name: string;
    sub_chat_id: string[];
}

export default class PromotionsService {
    static async getAll(): Promise<AxiosResponse<IPromotion[]>> {
        return $api.get('/affilate_promotions/');
    }

    static async getById(id: number): Promise<AxiosResponse<IPromotion>> {
        return $api.get(`/affilate_promotion/${id}`);
    }

    static async create(data: {
        channel_link: string;
        promotion_text: string;
        promocode_type: 'ONE_TIME_FREE_MENU_ITEM';
        short_name: string;
        sub_chat_id: string[];
    }): Promise<AxiosResponse> {
        return $api.post('/affilate_promotion/create', {...data});
    }

    static async update(data: {
        channel_link: string;
        promotion_text: string;
        promocode_type: 'ONE_TIME_FREE_MENU_ITEM';
        short_name: string;
        sub_chat_id: string[];
    }): Promise<AxiosResponse> {
        return $api.patch(`/affilate_promotion/update`, {...data});
    }

    static async delete(id: number): Promise<AxiosResponse> {
        return $api.delete(`/affilate_promotion/delete?promotion_id=${id}`);
    }

}