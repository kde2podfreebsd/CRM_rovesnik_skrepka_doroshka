import { AxiosResponse } from 'axios';
import $api from "./index.ts";

export interface IUser {
    chat_id: number;
    iiko_id: string;
    iiko_card: string;
    username: string;
    first_name: string;
    last_name: string | null;
    phone: string | null;
    spent_amount: number;
    qr_code_path: string | null;
    referral_link: string;
    balance: number;
    loyalty_info: LoyaltyInfo[];
}

export interface LoyaltyInfo {
    id: string;
    name: string;
    isActive: boolean;
    isDefaultForNewGuests: boolean;
    cashback: number;
    category: string;
    spend_money_amount: number;
    level: number;
}

export interface ILog {
    action: string
    created_at: string
}

export default class UserService {
    static async getAll(): Promise<AxiosResponse<IUser[]>> {
        return $api.get('clients/get_all');
    }

    static async getById(id: number): Promise<AxiosResponse<IUser>> {
        return $api.get(`client/${id}`);
    }

    static refillBalance(chat_id: number, amount: number): Promise<AxiosResponse> {
        return $api.post(`client/refill_balance`, {chat_id, amount});
    }

    static async updatePhone(chat_id: number, phone: string): Promise<AxiosResponse> {
        return $api.patch(`client/update_phone`, {chat_id, phone});
    }

    static async updateFirstName(chat_id: number, first_name: string): Promise<AxiosResponse> {
        return $api.patch(`client/update_first_name`, {chat_id, first_name});
    }

    static async updateLastName(chat_id: number, last_name: string): Promise<AxiosResponse> {
        return $api.patch(`client/update_last_name`, {chat_id, last_name});
    }

    static async getLogs(chat_id: number) : Promise<AxiosResponse<{status: string, message: ILog[]}>>
    {
        return $api.post(`client_log/get_by_chat_id/` + chat_id);
    }

    static async getAllUsernames(): Promise<AxiosResponse<string[]>> {
        return $api.get('clients/get_all_chat_id_and_username/');
    }

    static async getUserName(chat_id: number): Promise<AxiosResponse<{chat_id: string, username: string}[]>> {
        return $api.get(`/clients${chat_id}/username`);
    }
}