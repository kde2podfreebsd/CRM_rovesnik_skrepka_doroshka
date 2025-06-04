import React, { useEffect } from "react";
import ReservationList from "../../features/reservationList";
import Header from "../../shared/ui/header";
import Footer from "../../shared/ui/footer";
import styles from './styles.module.scss';
import TableReservationList from "../../features/tableReservationList/TableReservationList";
import { useQuery } from "@tanstack/react-query";
import { fetchEvents } from "../../entities/event/api";
import { setEvents } from "../../entities/event/eventSlice";
import { useAppDispatch } from "../../app/hooks/redux";
import { useTheme } from "../../shared/ui/themeContext/ThemeContext";
import { setTickets, setUID } from "../../entities/user/userSlice";
import { useSearchParams } from "react-router-dom";
import { fetchUserTicketsByUID } from "../../entities/user/api";
import useGetBarData from "../../app/hooks/useGetBarData";
import { TEvent } from "../../shared/types";

type Props = {
    type?: 'afisha' | 'reservations',
}
const UserPage = ({type = 'afisha'}: Props) => {
    //if (Telegram.WebApp.platform === 'unknown') return;

    const dispatch = useAppDispatch();
    const [searchParams] = useSearchParams();
    const [barId] = useGetBarData(searchParams);
    const uid = searchParams.get('uid') || Telegram.WebApp.initDataUnsafe.user?.id;
    const reservationTypeToTextMap = new Map([
        ['afisha', 'Запланированные события:'],
        ['reservations', 'Забронированные столы:']
    ]);

    // вынести все фетчи даты в кастомные хуки
    const {data: events, isLoading} = useQuery({
        queryKey: ['events'],
        queryFn: () => Promise.all([fetchEvents(1), fetchEvents(2), fetchEvents(3)])
            .then(res => res.filter(response => response.length > 0))
            .then(res => {
                let allEvents: TEvent[] = [];
                res.forEach(barEvents => allEvents.push(...barEvents))

                return allEvents
            }),
        retry: false,
    });

    const {data: tickets, isLoading: isTicketListLoading} = useQuery({
        queryKey: ['tickets'],
        queryFn: () => fetchUserTicketsByUID(uid)
    });

    useEffect(() => {
        if (!isLoading && !isTicketListLoading) {
            dispatch(setEvents(events!));
            dispatch(setUID(uid));
            dispatch(setTickets(tickets!));
        }
    }, [isLoading])

    const { theme } = useTheme();
    const rootClassName = theme === 'dark' ? styles.darkRoot : styles.lightRoot;

    return (
        <div className={`${styles.root} ${rootClassName}`}>
            
            <Header type={type} />
            <div className={styles.main}>
                <h2>Личный кабинет</h2>
                {/* сделать две вкладки: предстоящие события и прошедшие */}
                <p>{reservationTypeToTextMap.get(type)}</p>
                {type === 'afisha' && !isLoading && !isTicketListLoading && <ReservationList />}
                {type === 'reservations' && !isLoading && !isTicketListLoading && <TableReservationList />}
            </div>
            <Footer />
        </div>
    )
};

export default UserPage;
