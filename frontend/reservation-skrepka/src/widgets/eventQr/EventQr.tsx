import classNames from 'classnames';
import React, { useEffect, useState } from 'react';
import { Modal } from '@mui/material';
import { useQuery } from '@tanstack/react-query';

import { useAppSelector } from '../../app/hooks/redux';
import Spinner from '../../compoments/Spinner';
import { barAddressMap, barDisplayNameList, barQrTextMap } from '../../shared/constants';
import { convertTimestampToDateString, splitDatetimeString } from '../../shared/utils';
import {EventId, TEvent} from '../../shared/types';
import { fetchQrImg } from '../../entities/ticket/api';
import { selectEventById } from '../../entities/event/eventSlice';
import { selectTicketByEventId } from '../../entities/user/userSlice';
import { useTheme } from '../../shared/ui/themeContext/ThemeContext';
import styles from './styles.module.scss';
import axios from "axios";

type Props = {
    eventId: EventId,
    isModalOpen: boolean,
    setIsModalOpen: React.Dispatch<React.SetStateAction<boolean>>,
    className?: string,
}

const EventQr = ({ eventId, isModalOpen, setIsModalOpen, className }: Props) => {
    const ticket = useAppSelector((state) => selectTicketByEventId(state, eventId));
    const [event, setEvent] = useState<TEvent>();
    const [date, time] = event ? splitDatetimeString(event.dateandtime) : ['', ''];
    const readableDate = date ? convertTimestampToDateString(date) : '';
    const [copyAddressState, setCopyAddressState] = useState(true);
    const { theme } = useTheme();

    useEffect(() => {
        (async () => {
            const res = await axios.get( `https://rovesnik-bot.ru/api/event/` + eventId);
            setEvent(res.data)
            console.log(res)
        })()
    }, []);

    useEffect(() => {
        if (!copyAddressState) {
            navigator.clipboard.writeText(
                `${barDisplayNameList[event?.bar_id - 1]}\n${readableDate}\n${barAddressMap.get(barDisplayNameList[event?.bar_id - 1])}`
            );
            const timeout = setTimeout(() => setCopyAddressState(true), 1000);
            return () => clearTimeout(timeout);
        }
    }, [copyAddressState, event?.bar_id, readableDate]);

    const { data: qrImg, isLoading } = useQuery({
        queryKey: ['getQrImg'],
        queryFn: () => fetchQrImg(ticket?.qr_path),
        enabled: !!ticket?.qr_path,  // only run query if qr_path exists
    });

    const themeModalContainer = theme === 'dark' ? styles.darkThemeModal : styles.lightThemeModal;
    const themeContent = theme === 'dark' ? styles.darkTheme : styles.lightTheme;

    if (!isModalOpen) {
        return null;
    }

    return (
        <Modal
            className={classNames(`${styles.modalContainer} ${themeModalContainer}`, className)}
            open={isModalOpen}
            onClose={() => setIsModalOpen(false)}
        >
            <div className={`${styles.content} ${themeContent}`}>
                {isLoading && <Spinner />}
                {!isLoading && qrImg && (
                    <img src={URL.createObjectURL(qrImg)} alt='qr' />
                )}
                <div className={styles.status}>
                    <div className={ticket.activation_status ? styles.statusActive : styles.statusCompleted}>
                        {ticket.activation_status ? 'активен' : 'не активен'}
                    </div>
                    <div
                        className={copyAddressState ? styles.statusActive : styles.statusCompleted}
                        onClick={() => setCopyAddressState(prev => !prev)}
                    >
                        {copyAddressState ? 'скопировать адрес' : 'скопировано!'}
                    </div>
                </div>
                <p className={styles.shortName}>{event.short_name}</p>
                <div className={styles.dateTime}>
                    <p>Дата: {readableDate}</p>
                    <p>Время: {time}</p>
                </div>
                <div className={styles.barInfo}>
                    <p>{barQrTextMap.get(barDisplayNameList[event.bar_id - 1])}</p>
                    <p><span>{barAddressMap.get(barDisplayNameList[event.bar_id - 1])}</span></p>
                </div>
            </div>
        </Modal>
    );
};

export default EventQr;
