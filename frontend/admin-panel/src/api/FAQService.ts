import { AxiosResponse } from 'axios';
import $api from "./index.ts";
export interface IFaq {
    faq_id: number;
    bar_id: number;
    text: string;
}

export default class FAQService {
    static async getAll(): Promise<AxiosResponse<IFaq[]>> {
        return $api.get('/faq/get_all');
    }

    static async delete(id: number): Promise<AxiosResponse> {
        return $api.delete(`/faq/delete/${id}`);
    }

    static async create(text: string, barId: number): Promise<AxiosResponse> {
        return $api.post('/faq/create', {
            bar_id: barId,
            text: text
        });
    }

    static async update(id: number, text: string): Promise<AxiosResponse> {
        return $api.post(`/faq/update/`, {
            faq_id: id,
            text: text
        });
    }

    static async getByid(id: number): Promise<AxiosResponse<IFaq>> {
        return $api.get(`/faq/get_by_id/${id}`);
    }
}