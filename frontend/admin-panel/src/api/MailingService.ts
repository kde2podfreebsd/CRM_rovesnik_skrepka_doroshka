import { AxiosResponse } from 'axios';
import $api from "./index.ts";

export interface IMailing {
    mailing_name: string;
    text: string;
    preset: string;
    photo_paths?: string[];
    video_paths?: string[];
    document_paths?: string[];
    url_buttons: string[][];
    alpha: number;
    alpha_sent: number;
    alpha_delivered: number;
    beta: number;
    beta_sent: number;
    beta_delivered: number;
}

export interface IMailingNew {
    mailing_name: string;
    new_mailing_name: string;
    new_text: string;
    new_photo_name: string;
    new_video_name: string;
    new_document_name: string;
    new_url_button: {
        url: string;
        button_text: string;
    };
    new_preset: string;
    alpha: number;
    beta: number;
}

export interface UrlButton {
    url: string;
    button_text: string;
}

export interface ReceivedUrlButtons {
    url_buttons: string[]
}

export default class MailingService {

    static async create(mailing: IMailing): Promise<AxiosResponse> {
        return $api.post('/mailing/create', mailing);
    }

    static async getAll(): Promise<AxiosResponse<{status: string; message: IMailing[]}>> {
        return $api.get('/mailing/get_all');
    }

    static async update(mailing: IMailingNew): Promise<AxiosResponse> {
        return $api.post('/mailing/update', mailing);
    }

    static async delete(mailing_name: string): Promise<AxiosResponse> {
        return $api.delete('/mailing/delete?mailing_name=' + mailing_name);
    }

    static async sendMailingToUser(chat_id: number, mailing_name: string): Promise<AxiosResponse> {
        return $api.post('/mailing/send_message', { chat_id, mailing_name });
    }

    static async launchAlpha(mailing_name: string): Promise<AxiosResponse> {
        return $api.post('/mailing/launch_mailing_alpha/' + mailing_name );
    }

    static async launchBeta(mailing_name: string): Promise<AxiosResponse> {
        return $api.post('/mailing/launch_mailing_beta/' + mailing_name );
    }

    static async deletePhotoPath(mailing_name: string, photo_name: string): Promise<AxiosResponse> {
        return $api.patch('/mailing/delete_photo_path', { mailing_name, photo_name });
    }

    static async deleteVideoPath(mailing_name: string, video_name: string): Promise<AxiosResponse> {
        return $api.patch('/mailing/delete_video_path', { mailing_name, video_name });
    }

    static async deleteDocumentPath(mailing_name: string, document_name: string): Promise<AxiosResponse> {
        return $api.patch('/mailing/delete_document_path', { mailing_name, document_name });
    }

    static async getByName(mailing_name: string): Promise<AxiosResponse<IMailing>> {
        return $api.get('/mailing/get_by_name/' + mailing_name);
    }
}

