import { AxiosResponse } from 'axios';
import $api from "./index.ts";

export interface ITicket {
    id: number;
    client_chat_id: number;
    qr_path: string;
    activation_status: boolean;
    friends: {
        name: string;
        username: string;
    }[];
    hashcode: string;
    event_id: number;
}

interface IFriend {
    name: string;
    username: string;
}

export default class TicketService {
    static async getUserTickets(id: number): Promise<AxiosResponse<ITicket[]>> {
        return $api.get('tickets/' + id);
    }

    static async getById(id: number): Promise<AxiosResponse<ITicket>> {
        return $api.get(`ticket/${id}`);
    }

    static async delete(id: number): Promise<AxiosResponse> {
        return $api.delete(`ticket/${id}`);
    }

    static async update(data: {
        client_chat_id: number;
        qr_path: string;
        activation_status: boolean;
        friends: IFriend[];
        hashcode: string;
        event_id: number;
    }): Promise<AxiosResponse> {
        return $api.patch(`ticket/update`, {...data});
    }

    static async getByEventId(id: number): Promise<AxiosResponse<ITicket[]>> {
        return $api.get(`ticket/get_by_event_id/${id}`);
    }

    static async activate(hash: string): Promise<AxiosResponse> {
        return $api.patch(`ticket/activate?hashcode=${hash}`);
    }
}
