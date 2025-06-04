import React, {useEffect, useState} from 'react';
import { Dialog, DialogHeader, DialogBody, DialogFooter, Button, Typography } from "@material-tailwind/react";
import ImageService from "../../api/ImageService";
import UserService, {ILog, IUser, LoyaltyInfo} from "../../api/UserService.ts";
import './../loader/loader.css'
import {
    barIdParser,
    formatDate,
    imageUrl,
    promoCodeTypeParser,
    reservationStatusParser
} from "../../shared/funcsNconsts.ts";
import axios from "axios";
import TicketService, {ITicket} from "../../api/TicketsService.ts";
import {ITableReservation} from "../reservations/Reservations.tsx";
import PromocodeService, {IPromocode} from "../../api/PromocodeService.ts";
import ReservationService, {IReservation} from "../../api/ReservationService.ts";
import ReferralsService from "../../api/ReferralsService.ts";
import EventService, {IEvent} from "../../api/EventService.ts";
import TablesService, {ITable} from "../../api/TablesService.ts";

interface Props {
    isOpen: boolean;
    handleClose: () => void;
    qrCodePath: string | null;
    client: IUser;
}

const LoyaltyInfoModal = ({ isOpen, handleClose, client, loyaltyInfo }: Props) => {
    const [reviews, setReviews] = useState([]);
    const [tickets, setTickets] = useState<ITicket[]>([]);
    const [events , setEvents] = useState<IEvent[]>([]);
    const [reservations, setReservations] = useState<IReservation[]>([]);
    const [promocodes, setPromocodes] = useState<IPromocode[]>([]);
    const [referrals, setReferrals] = useState<string[]>([]);
    const [showAddInfo, setShowAddInfo] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [filteredReservations, setFilteredReservations] = useState<ITableReservation[]>([]);
    const [logs, setLogs] = useState<ILog[]>([]);
    const [showLogs, setShowLogs] = useState(false);

    const handleShowAddInfo = async () => {
        if (showAddInfo) {
            setShowAddInfo(false)
            return
        }
        setShowAddInfo(true)
        setIsLoading(true)
        const ticketRes = await TicketService.getUserTickets(client.chat_id)
        const eventPromises = ticketRes.data.map(ticket => EventService.getById(ticket.event_id));
        const eventsRes = await Promise.all(eventPromises);
        setEvents(eventsRes.map(event => event.data) );
        const res = await ReservationService.getUserReservaations(client.chat_id)
        const groupedReservationTable: ITableReservation[] = []
        if (res.data.Status !== 'Failed') {
            for (const reservation of res.data.Message) {
                const tableRes = await TablesService.getByUuid(reservation.table_uuid)
                groupedReservationTable.push({
                    reservation,
                    table: tableRes.data.Message,
                })
            }

            const mergedReservations: ITableReservation[] = []
            const orderUuidMap = new Map<string, ITableReservation>()

            for (const item of groupedReservationTable) {
                const { order_uuid } = item.reservation
                if (!orderUuidMap.has(order_uuid!)) {
                    orderUuidMap.set(order_uuid!, item)
                    mergedReservations.push(item)
                } else {
                    const existingItem = orderUuidMap.get(order_uuid!)
                    existingItem!.table.capacity += item.table.capacity
                }
            }
            setFilteredReservations(mergedReservations)
        }
        const promocodeRes = await PromocodeService.getUserPromocodes(client.chat_id)
        const referralsRes = await ReferralsService.getByUserId(client.chat_id)
        const logsRes = await UserService.getLogs(client.chat_id)
        setLogs(logsRes.data.message)
        setTickets(ticketRes.data)
        setPromocodes(promocodeRes.data)
        setReferrals(referralsRes.data)
        setIsLoading(false)
    }
    return (
        <Dialog open={isOpen} handler={handleClose} className='bg-neutral-800 max-h-full overflow-y-auto' onCLose={handleClose}>
            <DialogHeader className=' text-white'>Информация о пользователе</DialogHeader>
            <DialogBody>
                <img src={imageUrl + '/home/admin/CRM-Rovesnik-Doroshka-Screpka/BackendApp/static/user_qrcode/' + client.iiko_card + '.png'} alt="QR-код" className='w-40 h-40 shadow-md p-4 bg-white rounded-md' />
                <p className='text-white text-lg font-normal mt-2'>Имя: {client.first_name}</p>
                <p className='text-white text-lg font-normal'>Фамилия: {client.last_name ?? ''}</p>
                <p className='text-white text-lg font-normal'>Телефон: {client.phone}</p>
                <p className='text-white text-lg font-normal' >Юзернейм: <a href={`https://t.me/${client.username}`} target='_blank' className='text-blue-300 underline'>@{client.username}</a></p>
                <div >
                    <p className="mt-4 text-xl font-bold text-white">Информация о лояльности:</p>
                    <ul>
                        {client.loyalty_info.map((info) => (
                            <li key={info.id} className='text-white'>
                                <Typography color="white"><span className='capitalize'>Уровень {info.level}</span>: {info.cashback}% кэшбэк</Typography>
                                <Typography color={`${info.isActive ? 'green' : 'red'}`}>{info.isActive ? 'Активный' : 'Не активеный'}</Typography>
                                <Typography color="white">Потрачено денег: {info.spend_money_amount} руб.</Typography>
                            </li>
                        ))}
                    </ul>
                    <Button color='blue-gray' className='mt-4' onClick={handleShowAddInfo}>
                        {showAddInfo ? 'Скрыть доп. информацию' : 'Показать доп. информацию'}
                    </Button>
                    {showAddInfo && (
                        <div className='mt-4'>
                            {isLoading ? (
                                <div className='w-full mt-8 h-full flex justify-center items-center'><div className={"loader"}></div></div>
                            ) : (
                                <div className='flex flex-col gap-2'>
                                    <p className='text-white font-bold text-xl'>Билеты: </p>
                                    <div className='flex flex-col gap-2'>
                                        {tickets.length > 0 ? tickets.map((ticket) => (
                                            <div className='bg-neutral-600 rounded-lg p-2 max-w-60 flex flex-col gap-2'>
                                                <p className='text-white font-bold'>{events.find(event => event.event_id === ticket.event_id)?.short_name}</p>
                                                <p className={`font-bold ${ticket.activation_status ? 'text-green-500' : 'text-red-500'}`}>{ticket.activation_status ? 'Активирован' : 'Не активирован'}</p>
                                                <img
                                                    src={imageUrl + `${events.find(event => event.event_id === ticket.event_id)?.img_path}`}
                                                    alt={ticket.id.toString()}
                                                    className='w-40 h-20 object-cover rounded-md'/>
                                            </div>
                                        )) : (
                                            <p className='text-white font-normal'>У пользователя нет билетов</p>
                                        )}
                                    </div>
                                    <p className='text-white font-bold text-xl'>Резервации: </p>
                                    <div>
                                        {filteredReservations.length > 0 ? filteredReservations.map((reservation) => (
                                            (
                                                <div className='flex flex-col font-normal bg-neutral-600 rounded-lg p-2 text-white'>
                                                    <p className='font-bold'>Бар {reservation.table.bar_id} </p>
                                                    <p>Дата: {formatDate(reservation.reservation.reservation_start)}</p>
                                                    <p>Стол № {reservation.table.table_id} на {reservation.table.storey} этаже, на {reservation.table.capacity} чел.</p>
                                                    <p>Статус: {reservationStatusParser(reservation.reservation.status)}</p>
                                                </div>
                                            )
                                        )) : (
                                            <p className='text-white font-normal'>У пользователя нет резерваций</p>
                                        )}
                                    </div>
                                    <p className='text-white font-bold text-xl'>Промокоды: </p>
                                    <div className='flex flex-col gap-2'>
                                        {promocodes.length > 0 ? promocodes.map((promocode) => (
                                                <div className='font-normal bg-neutral-600 rounded-lg p-2 text-white'>
                                                    <p className='text-lg'>{promocode.name}</p>
                                                    <p>Тип: {promoCodeTypeParser(promocode.type)}</p>
                                                    <p className={`font-bold ${promocode.is_activated ? 'text-green-500' : 'text-red-500'}`}>{promocode.is_activated ? 'Активирован' : 'Не активирован'}</p>
                                                </div>
                                            )) : (
                                            <p className='text-white font-normal'>У пользователя нет промокодов</p>
                                        )}
                                    </div>
                                    <p className='text-white font-bold text-xl'>Рефералы: </p>
                                    <div>
                                        {referrals.length > 0 ? (
                                            <div>
                                                referrals
                                            </div>
                                        ) : (
                                            <p className='text-white font-normal'>У пользователя нет рефералов</p>
                                        )}
                                    </div>
                                    {logs.length > 0 && (
                                        <div>
                                            <Button onClick={() => setShowLogs(!showLogs)} color='blue-gray'>
                                                {showLogs ? 'Скрыть логи' : 'Показать логи'}
                                            </Button>
                                            {showLogs && (
                                                <div className='flex flex-col gap-2 mt-2'>
                                                    <div className='flex flex-col gap-2'>
                                                        {logs.map((log) => (
                                                            <div className='font-normal bg-neutral-600 rounded-lg p-2 text-white'>
                                                                <p className='text-sm text-wrap'>Действие: {log.action}</p>
                                                                <p>Дата: {formatDate(log.created_at)}</p>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </DialogBody>
            <DialogFooter>
                <Button color="red" onClick={handleClose}>Закрыть</Button>
            </DialogFooter>
        </Dialog>
    );
};

export default LoyaltyInfoModal;
