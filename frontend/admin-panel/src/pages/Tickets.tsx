import React, { useEffect, useState } from 'react';
import {Button, Card, Option, Select, Typography} from "@material-tailwind/react";
import TicketService, { ITicket } from "../api/TicketsService.ts";
import {barIdParser, formatDate, rowsColors} from "../shared/funcsNconsts.ts";
import EventService, { IEvent } from "../api/EventService.ts";

const Tickets = () => {
    const [events, setEvents] = useState<IEvent[]>([]);
    const [barId, setBarId] = useState<number>(1);
    const [event, setEvent] = useState<IEvent>();
    const [tickets, setTickets] = useState<ITicket[]>([]);
    const [noTicketsId, setNoTicketsId] = useState<number>(0);

    useEffect(() => {
        const fetchEvents = async () => {
            const res = await EventService.getBarEvents(barId);
            setEvents(res.data);
        };

        fetchEvents();
    }, [barId]);

    useEffect(() => {
        (async () => {
            setNoTicketsId(0)
           const res = await TicketService.getByEventId(event?.event_id);
            console.log(res.data.message)
            if (Array.isArray( res.data.message )) {
                setTickets(res.data.message);
            } else {
                setNoTicketsId(event?.event_id)
            }
        })()
    }, [event]);

    const handleChangeBarId = async (selectedBarId: string) => {
        const barIdNumber = parseInt(selectedBarId, 10);
        setBarId(barIdNumber);
        const res = await EventService.getBarEvents(barIdNumber);

    };

    const handleActivateTicket = async (hash: string, id: number) => {
        try {
            await TicketService.activate(hash);
            setTickets(prev => prev.map(ticket => ticket.id === id ? {...ticket, activation_status: true} : ticket))
        } catch (e) {
            throw new Error(e)
        }
    }

    const TABLE_HEAD = ["ID", "Client Chat ID", "Activation Status", "Friends", "Event"];

    return (
        <div>
            {tickets.length > 0 ? (
                <div className='p-2'>
                    <Card className="h-full w-full overflow-scroll">
                        <table className="w-full min-w-max table-auto text-left">
                            <thead>
                            <tr>
                                {TABLE_HEAD.map((head) => (
                                    <th key={head} className="border-b border-blue-gray-100 bg-neutral-700 p-4">
                                        <Typography
                                            variant="small"
                                            color="blue-gray"
                                            className="leading-none opacity-70 text-white font-bold text-xl"
                                        >
                                            {head}
                                        </Typography>
                                    </th>
                                ))}
                            </tr>
                            </thead>
                            <tbody>
                            {tickets.map((ticket, index) => (
                                <tr key={index} className={`${index % 2 === 0 ? rowsColors.first : rowsColors.second}`}>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {ticket.id}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {ticket.client_chat_id}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Button
                                            disabled={ticket.activation_status}
                                            color={ ticket.activation_status ? 'red' : 'green'}
                                            onClick={() => handleActivateTicket(ticket.hashcode, ticket.id)}>
                                            {ticket.activation_status ? 'Активирован' : 'Активировать'}
                                        </Button>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {ticket.friends ? (
                                                ticket.friends.map((friend) => `${friend.name} (${friend.username})`).join(', ')
                                            ) : 'None'}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {event?.short_name}
                                        </Typography>
                                    </td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                    </Card>
                    <Button
                        className='mt-4'
                        color='blue-gray'
                        onClick={() => setTickets([])}>Выбрать другое событие</Button>
                </div>
            ) : (
                <div className={'p-4 flex flex-col gap-8'}>
                    <h1 className='text-2xl text-white font-bold'>Выберите событие на которое хотите посмотреть билеты:</h1>
                    <div>
                        <h1 className='text-2xl text-white font-bold'>Бар: </h1>
                        <div className='w-60'>
                            <Select onChange={handleChangeBarId} value={barId.toString()} className='text-white text-xl'>
                                <Option value='1'>Ровесник</Option>
                                <Option value='2'>Скрепка</Option>
                                <Option value='3'>Дорожка</Option>
                            </Select>
                        </div>
                        <div className=' flex flex-wrap gap-4 w-4/5 mt-8'>
                            {events.length > 0 && events?.map((event) => (
                                <div
                                    key={event.event_id} // добавляем ключ для корректного рендеринга в React
                                    className={`w-80 p-4 rounded-lg text-white shadow-md cursor-pointer ${event.event_id === noTicketsId ? 'bg-red-500' : 'bg-neutral-700'} transition-all`}
                                    onClick={() => {
                                        setEvent(event);
                                        console.log('clicked', event.event_id);
                                    }}
                                >
                                    {noTicketsId !== event.event_id ? (
                                        <>
                                            <p className='text-cl font-bold'>{event.short_name}</p>
                                            <p>{barIdParser(event.bar_id)}</p>
                                            <p>{formatDate(event.dateandtime)}</p>
                                        </>
                                    ) : (
                                        <p className='text-l font-bold text-center flex justify-center items-center'>Нет билетов</p>
                                    )}
                                </div>
                            ))}
                    </div>
                </div>
                </div>
                )}
        </div>
    );
};

export default Tickets;
