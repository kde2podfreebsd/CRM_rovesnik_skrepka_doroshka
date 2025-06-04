import React, { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';

import AfishaPageTitle from '../../shared/ui/afishaPageTitle';
import EventList from '../../features/eventList';
import EventSearchField from '../../features/eventSearchField';
import Footer from '../../shared/ui/footer';
import Header from '../../shared/ui/header';
import Spinner from '../../compoments/Spinner';
import { addNewTicketForUser } from '../../entities/ticket/api';
import { applyFilters, setBarFilter, setEvents } from '../../entities/event/eventSlice';
import { barFullNameMap } from '../../shared/constants';
import { fetchEvents } from '../../entities/event/api';
import { selectCurrentBar } from '../../entities/bar/barSlice';
import { selectUID, setTickets, setUID } from '../../entities/user/userSlice';
import { useAppDispatch, useAppSelector } from '../../app/hooks/redux';
import { useTheme } from '../../shared/ui/themeContext/ThemeContext';
import styles from './styles.module.scss';
import { createTransaction, increaseBalanceByEventCost, increaseLoaltyByCost, increaseLoyaltyByEventCost, refillUserBalance } from '../../entities/acquiring/api';
import useGetBarData from '../../app/hooks/useGetBarData';
import { TEvent } from '../../shared/types';
import { fetchUserTicketsByUID } from '../../entities/user/api';

const AfishaPage = () => {
    //if (Telegram.WebApp.platform === 'unknown') return;

    const dispatch = useAppDispatch();
    const [searchParams] = useSearchParams();
    const [barId] = useGetBarData(searchParams);
    const uid = Telegram.WebApp.initDataUnsafe.user?.id || useAppSelector(selectUID);

    const {data: events, isLoading, refetch} = useQuery({
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
        queryFn: () => fetchUserTicketsByUID(uid),
    });

    useEffect(() => {
        if (!isLoading && !isTicketListLoading) {
            dispatch(setEvents(events!));
            dispatch(setBarFilter(barId));
            dispatch(setTickets(tickets!));
            dispatch(setUID(uid));
            if (searchParams.get('successEventId')) {
                addNewTicketForUser(Number(searchParams.get('successEventId')), uid)
                    .then(() =>
                        increaseLoyaltyByEventCost(uid, Number(searchParams.get('successEventId')))
                    )
                    .then(() => searchParams.get('amount') !== null ?
                        createTransaction(
                            uid,
                            barId,
                            Number(searchParams.get('amount')!),
                            searchParams.get('eventType') === 'deposit' ? 'increase_balance' : 'reduce_balance'
                        ) :
                        Promise.resolve({status: 'success'})
                    )
                    .then(() => {
                        if (searchParams.get('eventType') === 'deposit') {
                            increaseBalanceByEventCost(uid, Number(searchParams.get('successEventId')))
                            Promise.resolve({Success: true})
                        } else {
                            Promise.resolve({Success: true})
                        }
                    })
                    .then(() => refetch())
            }
        }
    }, [isLoading, isTicketListLoading])

    const { theme } = useTheme();
    const rootClassName = theme === 'dark' ? styles.darkRoot : styles.lightRoot;
    const mainClassName1 = theme === 'dark' ? styles.darkMain : styles.lightMain;

    return (
        <div className={`${styles.root} ${rootClassName}`}>
            <Header />
                <div className={`${styles.main} ${mainClassName1}`}>
                    <AfishaPageTitle text={`${barFullNameMap.get(useAppSelector(selectCurrentBar))}.\n`} />
                    <EventSearchField />
                    <p>Ближайшие события:</p>
                    {isLoading && <Spinner />}
                    {!isLoading && !isTicketListLoading && <EventList />}
                </div>
            <Footer />
        </div>
    );

};



export default AfishaPage;
