import { AxiosResponse } from 'axios';
import $api from "./index.ts";

export default class ReferralsService {
    static async getAll(): Promise<AxiosResponse<string[]>> {
        return $api.get('referrals/get_all_referrals');
    }

    static async getByLink(link: string): Promise<AxiosResponse<string>> {
        return $api.get(`referrals/get_all_referrals_by_link/`+ link);
    }

    static getByUserId(id: number): Promise<AxiosResponse<string[]>> {
        return $api.get(`referrals/get_referral/${id}`);
    }

    static async isGotBonus(chatId: number): Promise<AxiosResponse<boolean>> {
        return $api.get(`referrals/get_referral_got_bonus/${chatId}`);
    }
}