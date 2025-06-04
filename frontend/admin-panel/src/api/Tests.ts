import { AxiosResponse } from 'axios';
import $api from "./index.ts";

export interface ITest {
    id?: number;
    name: string;
    correct_cnt: number;
    total_cnt: number;
    description: string;
    percent_to_add: number;
    test_id: number;
    promocode_type: 'ONE_TIME_FREE_MENU_ITEM';
}
export default class TestsService {

    static async getAll(): Promise<AxiosResponse> {
        return $api.get('tests/get_all');
    }

    static async getAllResults(): Promise<AxiosResponse<ITest[]>> {
        return $api.get('tests/results');
    }

    static async getUserResult(id: number): Promise<AxiosResponse<ITest[]>> {
        return $api.get(`tests/result_by_chat_id/${id}`);
    }

    static update(data: ITest): Promise<AxiosResponse> {
        return $api.patch('test/update', {...data});
    }

    static delete(id: number): Promise<AxiosResponse> {
        return $api.delete(`test/delete?test_id=${id}`);
    }

    static create(data: ITest): Promise<AxiosResponse> {
        return $api.post('test/create', {...data});
    }
}