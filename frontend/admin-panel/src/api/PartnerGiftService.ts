import { AxiosResponse } from 'axios';
import $api from "./index.ts";

export interface IPartnerGift {
    short_name: string;
    promotion_text: string;
    got_gift?: number[];
    id: number;
}

export default class PartnerGiftService {
    static async getAll(): Promise<AxiosResponse<{Status: string; Message: IPartnerGift[]}>> {
        return $api.get('/partner_gift/get_all');
    }

    static async create(data: {
        short_name: string;
        promotion_text: string;
        got_gift: number[]
    }): Promise<AxiosResponse> {
        return $api.post('/partner_gift/create', data);
    }

    static async delete(id: number): Promise<AxiosResponse> {
        return $api.delete(`/partner_gift/delete/${id}`);
    }

    static async update(data: {
        partner_gift_id: number;
        short_name: string;
        promotion_text: string;
    }) {
        return $api.post('/partner_gift/update', {...data});
    }
}