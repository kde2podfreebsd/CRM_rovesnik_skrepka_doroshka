import * as dayjs from "dayjs";
import {format} from "date-fns";
import {api_url} from "../api";
import {PromocodeType} from "../api/PromocodeService.ts";

export const promoCodeTypeParser = (string: string) => {
    switch (string) {
        case 'ONE_TIME_FREE_MENU_ITEM':
            return 'Одно бесплатное блюдо';
        case 'DISCOUNT_ON_ACCOUNT':
            return 'Скидка на счет';
        case 'DISCOUNT_ON_DISH':
            return 'Скидка на блюдо';
        case 'DISCOUNT_FOR_PAID_EVENT':
            return 'Скидка на оплаченное мероприятие';
        case 'FREE_EVENT_TICKET':
            return 'Бесплатный билет на мероприятие';
        case 'REFILLING_BALANCE':
            return 'Пополнение баланса';
        case 'PARTY_WITHOUT_DEPOSIT':
            return 'Вечеринка без депозита';
        case 'GIFT_FROM_PARTNER':
            return 'Подарок от партнера';
        case 'CUSTOM':
            return 'Пользовательский';
        default:
            return 'Неизвестный тип промокода';
    }
};

export const formatDate = (isoString: string) => {
    const months = [
        'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
        'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
    ];

    const date = new Date(isoString);

    const day = date.getDate();
    const month = months[date.getMonth()];
    const year = date.getFullYear();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');

    return `${day} ${month} ${year}, ${hours}:${minutes}`;
}

export const rowsColors = {
    first: 'bg-neutral-500',
    second: 'bg-neutral-600'
}

export const formatDateToSend = (date: Date) => {
    return format(date, "yyyy-MM-dd HH:mm:ss.SSS");
};

export const randomNum = () => parseInt((Math.random() * 100000).toFixed(0))

export const bgAdd = 'bg-neutral-700'

export const barIdParser = (id: number) => {
    const barNames: { [key: number]: string } = {
        1: 'Ровесник',
        2: 'Скрепка',
        3: 'Дорожка',
    };

    return barNames[id] || 'Неизвестный бар';
}

export const reservationStatusParser = (status: string) => {
    switch (status) {
        case 'reserved':
            return 'Забронировано';
        case 'cancelled':
            return 'Отменено';
        case 'expired':
            return 'Просрочено';
        case 'reserved_and_notified':
            return 'Забронировано';

    }
}

export const imageUrl = api_url + '/file/download/?path_to_file='

export const eventImageServUrl = '/events'

export const promocodeTypes: PromocodeType[] = [
    'ONE_TIME_FREE_MENU_ITEM',
    'DISCOUNT_ON_ACCOUNT',
    'DISCOUNT_ON_DISH',
    'DISCOUNT_FOR_PAID_EVENT',
    'FREE_EVENT_TICKET',
    'REFILLING_BALANCE',
    'PARTY_WITHOUT_DEPOSIT',
    'GIFT_FROM_PARTNER',
    'CUSTOM'
];
