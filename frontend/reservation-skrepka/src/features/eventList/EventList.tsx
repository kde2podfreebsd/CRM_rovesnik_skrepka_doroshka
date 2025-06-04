import React, {useEffect, useState} from 'react';
import { useAppSelector } from '../../app/hooks/redux';
import {selectBarFilter, selectEvents, selectEventsByBarId, selectFilter} from '../../entities/event/eventSlice';
import EventCard from '../../widgets/eventCard';
import styles from './styles.module.scss';
import { splitDatetimeString } from '../../shared/utils';
import dayjs from 'dayjs';
import { fetchUserTicketsByUID } from '../../entities/user/api';
import { useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import useGetBarData from '../../app/hooks/useGetBarData';
import axios from "axios";
import {TEvent} from "../../shared/types";
import {barFilterList, barList} from "../../shared/constants";

const EventList = () => {
    const barFilter = useAppSelector(selectBarFilter);
    const filter = useAppSelector(selectFilter)
    const userId = window.Telegram.WebApp?.initDataUnsafe?.user?.id ? window.Telegram.WebApp.initDataUnsafe.user.id : '272324534';
    const [searchParams] = useSearchParams();
    const [barId] = useGetBarData(searchParams);
    const [events, setEvents] = useState<TEvent[]>([]);
    const uid = (searchParams.get('uid') || Telegram.WebApp.initDataUnsafe.user?.id) ?? 272324534;
    const {data: userTickets, isLoading} = useQuery({
        queryKey: ['getUserTickets', uid],
        queryFn: () => fetchUserTicketsByUID(uid)
    })

    const [purchasedTickets, setPurchasedTickets] = useState<number[]>([]);
    useEffect(() => {
        (async () => {
            const res = await axios.get(`https://rovesnik-bot.ru/api/tickets/` + userId)
            setPurchasedTickets(prevState => [...prevState, ...res.data.map((ticket: any) => ticket.event_id)])
            console.log(res.data.map((ticket: any) => ticket.event_id))
        })()
    }, [])

    useEffect(() => {
        const fetchEvents = async (barId: number) => {
            try {
                const res = await axios.get(`https://rovesnik-bot.ru/api/${barId}/upcoming_events/`);
                return res.data.message;
            } catch (error) {
                console.error(`Failed to fetch events for barId ${barId}:`, error);
                return [];
            }
        };

        const loadEvents = async () => {
            setEvents([]);
            if (barFilter === 0) {
                const barIds = [1, 2, 3];
                try {
                    const results = await Promise.all(barIds.map(barId => fetchEvents(barId)));
                    setEvents(results.flat());
                } catch (error) {
                    console.error("Failed to fetch events:", error);
                }
            } else {
                const fetchedEvents = await fetchEvents(barFilter);
                setEvents(fetchedEvents);
            }
            if (filter === 'dateandtime') {
                setEvents(prevState => [...prevState].sort((a, b) => new Date(a.dateandtime).getTime() - new Date(b.dateandtime).getTime()));
            }
            if (filter === 'price') {
                setEvents(prevState => [...prevState].sort((a, b) => a.price - b.price));
            }
        };

        loadEvents();
    }, [barFilter, filter]);

    useEffect(() => {
        console.log('[EVENTS3]',typeof events)
    }, [])

    if (!events) {
        return <div className='w-full h-full min-h-screen bg-white'></div>
    }

    return (
        <div>
            {!isLoading && events.length > 0 && (
                events.filter(event => {
                    const eventDate = dayjs(splitDatetimeString(event.dateandtime)[0]);
                    const now = dayjs();

                    return now.diff(eventDate, 'day', true) < 1;
                }).map((event) => {
                    const userHasTicket = (userTickets ?? []).some(ticket => ticket.event_id === event.event_id);
                    let buttonText = '';

                    if (userHasTicket) {
                        buttonText = event.event_type === 'free' ? 'Вы зарегистрированы' : event.event_type === 'deposit' ? 'Депозит внесен' : 'Билет куплен';
                    } else {
                        switch (event.event_type) {
                            case 'free':
                                buttonText = 'Зарегистрироваться';
                                break;
                            case 'event':
                                buttonText = 'Купить билет';
                                break;
                            case 'deposit':
                                buttonText = 'Внести депозит';
                                break;
                            default:
                                buttonText = 'Действие';
                                break;
                        }
                    }

                    const additionalProps = {
                        customActionButtonText: buttonText
                    };

                    return (
                        <div key={event.event_id} className={styles.container}>
                            <EventCard
                                key={event.event_id}
                                data={event}
                                showUpperBubble
                                showActionButton
                                cardType='base'
                                {...additionalProps}
                                purchasedTickets={purchasedTickets}
                            />
                        </div>
                    )
                })
            )}                
        </div>
    );
};

export default EventList;