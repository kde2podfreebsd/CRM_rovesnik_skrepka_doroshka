import { AxiosResponse } from 'axios';
import $api from "./index.ts";

export interface IQuiz {
    quiz_id?: number;
    header: string;
    answers: string[];
    answer_cnt: number;
    correct_ans_id: number;
    test_id: number;
}

export default class QuizzesService {
    static async getAll(): Promise<AxiosResponse<IQuiz[]>> {
        return $api.get('quizzes');
    }

    static async create(data: {
        header: string;
        answers: string[];
        answer_count: number;
        correct_ans_id: number;
        test_id: number;
    })
    : Promise<AxiosResponse> {
        return $api.post('quiz/create', {...data});
    }

    static async update(data: IQuiz): Promise<AxiosResponse> {
        return $api.patch('quiz/update', {...data});
    }

    static async delete(id: number): Promise<AxiosResponse> {
        return $api.delete(`quiz/delete?quiz_id=${id}`);
    }
}