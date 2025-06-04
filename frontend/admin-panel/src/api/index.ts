import axios from 'axios';

export const api_url = 'https://rovesnik-bot.ru/api';

const $api = axios.create({
    baseURL: api_url,
});

export default $api;