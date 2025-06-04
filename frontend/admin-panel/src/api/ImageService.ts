import { AxiosResponse } from 'axios';
import $api from "./index.ts";

export default class ImageService {

    static async uploadImage(image: FormData, dir: string): Promise<AxiosResponse> {
        return $api.post('/file/upload_static' + dir, image);
    }

    static async getImage(path: string): Promise<AxiosResponse> {
        return $api.get(`file/download/?path_to_file=${path}`);
    }
}