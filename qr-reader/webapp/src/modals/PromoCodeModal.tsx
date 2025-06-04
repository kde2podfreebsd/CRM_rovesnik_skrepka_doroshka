import {useEffect, useState} from "react";
import {useQrCodeContext} from "../QrReader.tsx";
import {api_url} from "../App.tsx";
import axios from "axios";
import IPromoCode from "../ types/IPromoCode.ts";
import './loader.css'
import {format} from "date-fns";
import GoBackToScanButton from "../components/GoBackToScanButton.tsx";

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

export const dateParser = (date: string) => {
    const dateObj = new Date(date);
    return format(dateObj, 'dd.MM.yyyy');
}

const PromoCodeModal = () => {

    const { qrCodeData } = useQrCodeContext();

    const testHash = '2aa46639050a6d6798319f2961548630'

    const isDev = false

    const promoCodeReqData = isDev ? testHash : qrCodeData

    const [receivedPromoCode, setReceivedPromoCode] = useState<IPromoCode>()

    const [isActivated, setIsActivated] = useState(false)


    useEffect(() => {
        (async () => {
            const res = await axios.post(api_url + "/promocodes/get_promocode_by_hashcode/" + promoCodeReqData);
            setIsActivated(res.data.is_activated)
            setReceivedPromoCode(res.data)
            console.log(res.data)
        })()
    }, []);

    const handleActivatePromoCode = async () => {
        setIsActivated(false)
        if (!receivedPromoCode?.is_activated) {
            try {
                await axios.patch(api_url + "/promocodes/activate_promocode_by_hash/" + promoCodeReqData);
            } catch (error) {
                console.error("Error activating promo code:", error);
            }
        }
    }


    if (!receivedPromoCode) {
        return <div className="w-full h-screen justify-center items-center flex"><div className='loader'></div></div>
    }

    return (
        <div className='flex justify-center flex-col items-center w-full h-full min-h-screen gap-2'>
            <h1 className='text-xl font-bold'>Промокод {receivedPromoCode.name}</h1>
            <div className='border-2 rounded-md border-black flex-col flex justify-start items-start p-4 w-4/5'>
                <p><span className='font-semibold'>Описание:</span> {receivedPromoCode.description}</p>
                <p><span className='font-semibold'>Информация для персонала:</span> {receivedPromoCode.operational_info}</p>
                <p><span className='font-semibold'>Тип промокода:</span> {promoCodeTypeParser(receivedPromoCode.type)}</p>
                <p><span className='font-semibold'>Срок действия:</span> {dateParser(receivedPromoCode.end_time)}</p>
                <button onClick={() => handleActivatePromoCode()}
                    className={`bg-blue-500 ${receivedPromoCode.is_activated ? '' : 'hover:bg-blue-700'} text-white font-bold py-2 px-4 rounded mt-4 ${receivedPromoCode.is_activated ? 'opacity-50' : ''}`}>
                    {isActivated ? 'Активирован' : 'Активировать'}
                </button>
            </div>
            <GoBackToScanButton />
        </div>
    );
};

export default PromoCodeModal;
