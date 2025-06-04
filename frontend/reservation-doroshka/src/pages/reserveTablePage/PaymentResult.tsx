import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { v4 as uuidv4 } from 'uuid';
import ReservationService from "../../api/ReservationService";

const PaymentResult = () => {
    const [isTwiceBookError, setTwiceBookError] = useState(false);
    const location = useLocation();
    const navigate = useNavigate();
    const [isSuccess, setIsSuccess] = useState(false);

    useEffect(() => {
        const searchParams = new URLSearchParams(location.search);
        const status = searchParams.get('status');
        const table_uuid = searchParams.get('table_uuid');
        const barId = searchParams.get('barId');
        const amount = searchParams.get('amount');
        const client_chat_id = searchParams.get('client_chat_id');
        const date = searchParams.get('date');
        const order_uuid = searchParams.get('order_uuid');
        const bowlingTimes = searchParams.get('bowlingTimes');
        const poolTimes = searchParams.get('poolTimes');

        const parseTimes = (timesString: string | null): { start_time: string, table_uuid: string }[] => {
            if (!timesString) return [];
            return timesString.split(',').map(item => {
                const [start_time, table_uuid] = item.split('|');
                return { start_time, table_uuid };
            });
        };

        const bowlingList = parseTimes(bowlingTimes);
        const poolList = parseTimes(poolTimes);

        console.log(bowlingList, poolList);

        if (status === 'success') {
            handleSuccessfulPayment(table_uuid, barId, amount, client_chat_id, date, order_uuid, bowlingList, poolList);
        } else {
            handleFailedPayment();
        }
    }, [location.search]);

    const handleSuccessfulPayment = async (table_uuid, barId, amount, client_chat_id, date, order_uuid, bowlingList, poolList) => {
        console.log('Payment successful');
        try {
            const res = await ReservationService.create({
                client_chat_id,
                table_uuid,
                reservation_start: date,
                deposit: amount,
                order_uuid,
            });
            if (res.data.Status === 'Failed' && res.data.Message.includes('ability')) {
                setTwiceBookError(true);
                // return;
            }

            const poolsPromises = poolList.map(pool => ReservationService.create({
                client_chat_id,
                table_uuid: pool.table_uuid,
                reservation_start: date.slice(0, 10) + ' ' + pool.start_time + ':00.000',
                deposit: 0,
                order_uuid,
            }));

            const bowlingPromises = bowlingList.map(bowling => ReservationService.create({
                client_chat_id,
                table_uuid: bowling.table_uuid,
                reservation_start: date.slice(0, 10) + ' ' +  bowling.start_time + ':00.000',
                deposit: 0,
                order_uuid,
            }));

            await Promise.all([...poolsPromises, ...bowlingPromises]);
            setIsSuccess(true)
            // setTimeout(() => {
            //     navigate('/doroshka/my/reservations?barId=3');
            // }, 10000);
        } catch (e) {
            console.log(e);
        }
    };

    const handleFailedPayment = () => {
        console.log('Payment failed');
        alert('Оплата не удалась, попробуйте снова.');
    };

    if (isTwiceBookError) {
        // setTimeout(() => {
        //     navigate('/doroshka/reservation?barId=3');
        // }, 10000);
        return (
            <div className='text-center w-full h-full min-h-screen flex flex-col gap-2 justify-center items-center'>
                <p className='text-xl'>
                    Ошибка <br/> Вы можете бронировать 1 раз в день <br /> Вы будете перенаправлены на главную страницу через 10 секунд
                </p>
                <button onClick={() => navigate('/doroshka/my/reservations?barId=3')} className=' px-8 w-40 mx-4 text-center text-white font-bold text-lg py-2 bg-blue-500 rounded-full'>
                    Вернуться
                </button>
            </div>
        );
    }

    if (isSuccess) {
        // setTimeout(() => {
        //     navigate('/doroshka/reservation?barId=3');
        // }, 10000);
        return (
            <div className='text-center w-full h-full min-h-screen flex flex-col gap-2 justify-center items-center'>
                <p className='text-xl'>
                    Оплата прошла успешно <br/>Столик забронирован<br /> Вы будете перенаправлены на главную страницу через 10 секунд
                </p>
                <button onClick={() => navigate('/doroshka/my/reservations?barId=3')} className=' px-8 w-40 mx-4 text-center text-white font-bold text-lg py-2 bg-blue-500 rounded-full'>
                    Вернуться
                </button>
            </div>
        );
    }


    return <div>Processing payment...</div>;
};

export default PaymentResult;
