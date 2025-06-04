import { AxiosResponse } from 'axios';
import $api from "./index.ts";

export interface IArtist {
    id: number
    artist_id: number;
    name: string;
    description: string;
    img_path: string;
}


export default class ArtistService {

    static async getAll(): Promise<AxiosResponse<IArtist[]>> {
        return $api.get('artists/get_all');
    }

    static async getById(id: number): Promise<AxiosResponse<IArtist>> {
        return $api.get(`artist/${id}`);
    }

    static async delete(id: number): Promise<AxiosResponse> {
        return $api.delete(`artist/delete?artist_id=${id}`);
    }

    static async create(data: {
        name: string;
        description: string;
        img_path: string;
    }): Promise<AxiosResponse> {
        return $api.post(`artist/create`,{...data});
    }

    static async update(data: {
        artist_id: number;
        name: string;
        description: string;
        img_path?: string;
    }): Promise<AxiosResponse> {
        return $api.patch(`/artist/update`, {...data});
    }

    static async addToEvent(data: {
        artist_id: number,
        event_id: number
    }): Promise<AxiosResponse> {
        return $api.post(`/artist/create_relationship?event_id=${data.event_id}&artist_id=${data.artist_id}`);
    }

    static async deleteRelationship(relationshipId: number): Promise<AxiosResponse> {
        return $api.delete(`/artist/delete_relationship/`+ relationshipId);
    }
}