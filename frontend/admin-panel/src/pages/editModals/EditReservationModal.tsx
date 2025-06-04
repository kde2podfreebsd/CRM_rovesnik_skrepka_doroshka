import React, { useEffect, useState } from 'react';
import { Button, Dialog, DialogHeader, DialogBody, DialogFooter, Select, Option } from "@material-tailwind/react";
import ReservationService, { IReservation } from "../../api/ReservationService.ts";
import DatePicker from "../../components/DatePicker.tsx";
import reservations, { ITableReservation } from "../reservations/Reservations.tsx";
import {formatDateToSend} from "../../shared/funcsNconsts.ts";
import {formatDate} from "date-fns/format";

interface Props {
    isOpen: boolean;
    handleClose: () => void;
    editableReservation: ITableReservation | null;
    setEditableReservation: React.Dispatch<React.SetStateAction<ITableReservation | null>>;
    setReservations: React.Dispatch<React.SetStateAction<ITableReservation[]>>;
}

const EditReservationModal = ({ isOpen, handleClose, editableReservation, setEditableReservation, setReservations }: Props) => {
    const [reservationStart, setReservationStart] = useState<Date | null>(null);
    const [selectedTime, setSelectedTime] = useState<string>(''); // Добавляем состояние для выбранного времени

    useEffect(() => {
        if (editableReservation?.reservation.reservation_start) {
            const reservationDate = new Date(editableReservation.reservation.reservation_start);
            const hours = reservationDate.getHours().toString().padStart(2, '0');
            const minutes = reservationDate.getMinutes().toString().padStart(2, '0');
            setSelectedTime(`${hours}:${minutes}`);
            setReservationStart(reservationDate);
        }
    }, [editableReservation?.reservation.reservation_start]);


    const handleTimeChange = (e) => {
        setSelectedTime(e);
    };


    const handleSubmit = async () => {
        const dateToSend = formatDate( reservationStart?.toISOString().toString(), 'yyyy-MM-dd');
        console.log(dateToSend)
        if (editableReservation && reservationStart && selectedTime) {
            try {
                const dataToSend = {
                    reservation_start: dateToSend + ' ' + selectedTime + ':00.000',
                    reserve_id: editableReservation.reservation.reserve_id,
                    client_chat_id: editableReservation.reservation.client_chat_id,
                    table_uuid: editableReservation.reservation.table_uuid,
                    deposit: editableReservation.reservation.deposit
                };

                await ReservationService.update(dataToSend);
                setEditableReservation(null);
                setReservations(reservations =>
                    reservations.map(reservation =>
                        reservation.reservation.reserve_id === editableReservation.reservation.reserve_id
                            ? { ...reservation, reservation_start: dateTime }
                            : reservation
                    )
                );selectedTime
                handleClose();
            } catch (error) {
                console.error(error);
            }
        }
    };

    return (
        <Dialog open={isOpen} className='bg-neutral-800'>
            <DialogHeader className='text-white'>Изменить бронирование</DialogHeader>
            <DialogBody className='text-white flex flex-col gap-4'>
                <DatePicker
                    text='Дата'
                    setInputPCEndTime={setReservationStart}
                    inputPCEndTime={reservationStart}
                    value={reservationStart} />
                <Select
                    label="Выберите время"
                    value={selectedTime}
                    onChange={handleTimeChange}
                    className='text-white'
                    dismiss={undefined}
                >
                    {[...Array(10 * 2)].map((_, i) => {
                        const hour = Math.floor(14 + i / 2);
                        const minute = (i % 2) * 30;
                        const hourString = hour.toString().padStart(2, '0');
                        const minuteString = minute.toString().padStart(2, '0');
                        return (
                            <Option value={`${hourString}:${minuteString}`} >
                                {`${hourString}:${minuteString}`}
                            </Option>
                        );
                    })}
                </Select>
            </DialogBody>
            <DialogFooter>
                <Button color="red" variant={'text'} onClick={handleClose}>Отмена</Button>
                <Button color="green" variant={'filled'} onClick={handleSubmit}>Сохранить</Button>
            </DialogFooter>
        </Dialog>
    );
};

export default EditReservationModal;
