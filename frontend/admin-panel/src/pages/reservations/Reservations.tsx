import React, { useEffect, useState } from 'react';
import {Button, Card, Dialog, DialogBody, DialogHeader, Typography} from "@material-tailwind/react";
import {NoSymbolIcon, PencilIcon, TrashIcon} from "@heroicons/react/24/outline";
import ReservationService, {IReservation} from "../../api/ReservationService.ts";
import ButtonWithPopover from "../../components/ButtonWithPopover.tsx";
import {bgAdd, formatDate, reservationStatusParser, rowsColors} from "../../shared/funcsNconsts.ts";
import TablesService from "../../api/TablesService.ts";
import EditReservationModal from "../editModals/EditReservationModal.tsx";
import './../loader/loader.css'
import MergeTablesModal from "./MergeTablesModal.tsx";
import CreateReservation from "../createModals/CreateReservation.tsx";

export interface ITableReservation {
    reservation: IReservation
    table: ITable
}

export interface ITable {
    bar_id: number
    storey: number
    table_id: number
    table_uuid: string
    terminal_group_uuid: string
    capacity: number
    is_available: boolean
}

const Reservations = () => {
    const [isEditing, setIsEditing] = useState(false);
    const [editableReservation, setEditableReservation] = useState<ITableReservation>();
    const [filteredReservations, setFilteredReservations] = useState<ITableReservation[]>([]);
    const [isMerge, setIsMerge] = useState(false);
    const [isAdding, setIsAdding] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        (async () => {
            setIsLoading(true)
            const res = await ReservationService.getAll()
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
            setIsLoading(false)
        })()
    }, [])


    const TABLE_HEAD = ["", "Client ID", "Capacity", "Reservation Start", "Status", "Deposit", 'Floor'];

    const handleEditReservation = (reserveId: string) => {
        setEditableReservation(filteredReservations.find((reservation) => reservation.reservation.reserve_id === reserveId)!);
        setIsEditing(true);
        console.log('clicked', reserveId);
    };

    const handleDeleteReservation = async (reservation_id: number) => {
        try {
            await ReservationService.delete(reservation_id);
            setFilteredReservations( filteredReservations.filter((reservation) => reservation.reservation.reservation_id !== reservation_id)) //delete reservation
        } catch (e) {
            throw new Error(e);
        }
    };

    const handleCancelReservation = async (reserve_id: string) => {
        try {
            await ReservationService.cancel(reserve_id);
            setFilteredReservations(filteredReservations.find( (reservation) => reservation.reservation.reserve_id === reserve_id)?.reservation.status === 'cancelled' ? filteredReservations : filteredReservations.filter((reservation) => reservation.reservation.reserve_id !== reserve_id));
        } catch (e) {
            throw new Error(e);
        }
    };

    if (isLoading) {
        return <div className="w-full h-full min-h-screen justify-center items-center flex"><div className='loader'></div></div>;
    }

    return (
        <>
            <div className='p-2'>
                <div className='mb-2 flex gap-2'>
                    <Button color='blue-gray' onClick={() => setIsAdding(true)}>Создать</Button>
                    <Button color='blue-gray' onClick={() => setIsMerge(true)}>Обьеденить столы</Button>
                </div>
                {filteredReservations.length > 0 ? (
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
                            {filteredReservations.map((reservation, index) => (
                                <tr key={index} className={`${index % 2 === 0 ? rowsColors.first : rowsColors.second}`}>
                                    <td className="p-4">
                                        <div className="flex gap-2">
                                            <Button color='blue-gray'
                                                    onClick={() => handleEditReservation(reservation.reservation.reserve_id)}>
                                                <PencilIcon className=' w-5 h-5'/>
                                            </Button>
                                            <ButtonWithPopover
                                                color='blue-gray'
                                                onClick={() => handleDeleteReservation(reservation.reservation.reservation_id)}
                                                popoverText='Вы уверены что хотите удалить резервирование?'
                                            >
                                                <TrashIcon className='w-5 h-5'/>
                                            </ButtonWithPopover>
                                            <ButtonWithPopover
                                                color='blue-gray'
                                                onClick={() => handleCancelReservation(reservation.reservation.reserve_id)}
                                                popoverText='Вы уверены что хотите отменить резервирование?'
                                            >
                                                <NoSymbolIcon className='w-5 h-5'/>
                                            </ButtonWithPopover>
                                        </div>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {reservation.reservation.client_chat_id}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {reservation.table.capacity}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {formatDate(reservation.reservation.reservation_start)}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small"
                                                    color={`${reservation.reservation.status === 'reserved' || reservation.reservation.status === 'reserved_and_notified' ? 'green' : 'red'}`}
                                                    className="font-bold">
                                            {reservationStatusParser(reservation.reservation.status!)}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {reservation.reservation.deposit}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {reservation.table.storey}
                                        </Typography>
                                    </td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                    </Card>
                ) : (
                    <p className='text-white font-normal text-xl'>Пусто</p>
                )}
            </div>
            {isEditing && <EditReservationModal
                editableReservation={ editableReservation }
                setIsEditing={ setIsEditing }
                setReservations={setFilteredReservations}
                setEditableReservation={setEditableReservation} handleClose={ () => setIsEditing(false)} isOpen={isEditing}/>
            }
            {isMerge && (
                <MergeTablesModal
                    setIsMerge={setIsMerge}
                    isMerge={isMerge}
                    setFilteredReservations={setFilteredReservations}
                />
            )}
            {isAdding && (
                <CreateReservation isOpen={ isAdding} handleClose={ () => setIsAdding(false)} setReservations={ setFilteredReservations} />
            )}
        </>
    );
};

export default Reservations;
