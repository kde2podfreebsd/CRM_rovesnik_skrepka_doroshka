import { AxiosResponse } from 'axios';
import $api from "./index.ts";

export interface IEvent {
    event_id?: number;
    short_name: string;
    description: string;
    img_path: string;
    event_datetime: string;
    end_datetime: string;
    bar_id: number;
    place: string;
    age_restriction: number;
    event_type: string;
    price: number;
    notification_time: string[];
}

export default class EventService {

    static async getBarEvents(barId: number): Promise<AxiosResponse<IEvent[]>> {
        return $api.get(barId + '/events');
    }

    static async getById(id: number): Promise<AxiosResponse<IEvent>> {
        return $api.get(`event/${id}`);
    }

    static async create(data: {
        short_name: string;
        description: string;
        img_path: string;
        dateandtime: string;
        end_datetime: string;
        bar_id: number;
        place: string;
        age_restriction: number;
        event_type: string;
        price: number;
        notification_time: string[];
    }): Promise<AxiosResponse<IEvent>> {
        return $api.post('event/create', {...data});
    }

    static async update(data: {
        short_name: string;
        description: string;
        img_path: string;
        dateandtime: string;
        end_datetime: string;
        bar_id: number;
        place: string;
        age_restriction: number;
        event_type: string;
        price: number;
        notification_time: string[];
    }): Promise<AxiosResponse> {
        return $api.patch(`event/update`, {...data});
    }

    static async delete(id: number): Promise<AxiosResponse> {
        return $api.delete(`event/delete?event_id=${id}`);
    }

    static async getArtists(id: number): Promise<AxiosResponse> {
        return $api.get(`event/get_related_artists?event_id=${id}`);
    }
}