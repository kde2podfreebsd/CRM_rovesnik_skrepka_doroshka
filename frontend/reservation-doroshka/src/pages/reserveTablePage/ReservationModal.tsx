import { Modal, Select, MenuItem } from '@mui/material'
import { Field, Form, Formik } from 'formik'
import React, { useEffect, useState } from 'react'

import { closeCross } from '../../shared/assets'
import { dateSelectRange, maxGuestCount } from '../../shared/constants'
import Button from '../../shared/ui/button'
import {
    addDaysToDate,
    getTimeSelectList,
    convertTimestampToDateString,
} from '../../shared/utils'

import styles from './styles.module.scss'

import { useTheme } from '../../shared/ui/themeContext/ThemeContext'
import ReservationService, { IReservation } from '../../api/ReservationService'
import TablesService, { ITable } from '../../api/TablesService'
import axios from 'axios'
import { ITableReservation } from '../../features/tableReservationList/TableReservationList'
import BowlingSvg from "../../shared/BowlingSVG";
import PoolSvg from "../../shared/PoolSVG";
import {current} from "@reduxjs/toolkit";

const ReservationModal = ({
                              isOpen,
                              handleClose,
                              tableReservation,
                              errorDate,
                              setErrorDate,
                              setErrorPhone,
                              errorPhone,
                              setFilteredReservations,
                              errorBook,
                              setErrorBook,
                              setErrorBefore2hours,
                              errorBefore2hours,
                              errorSupport,
                              setErrorSupport,
                          }) => {
    const [allTablesByUUID, setAllTablesByUUID] = useState([]);
    const [receivedTable, setReceivedTable] = useState(null);
    const [receivedClient, setReceivedClient] = useState(null);
    const [selectedTimes, setSelectedTimes] = useState({});
    const { theme } = useTheme();
    const [tableIdError, setTableIdError] = useState(0);
    const [selectedDate, setSelectedDate] = useState(tableReservation.reservation.reservation_start.split('T')[0]);

    useEffect(() => {
        (async () => {
            const tableRes = await TablesService.getByUuid(
                tableReservation.reservation.table_uuid
            );
            const clientRes = await axios.get(
                'https://rovesnik-bot.ru/api/client/' +
                tableReservation.reservation.client_chat_id
            );
            const orderuuidsPromises = await ReservationService.getByOrderUUIDWithTables(tableReservation.reservation.order_uuid);
            setAllTablesByUUID(orderuuidsPromises.data.Message);
            setReceivedTable(tableRes.data.Message);
            setReceivedClient(clientRes.data);

            const initialTimes = orderuuidsPromises.data.Message.reduce((acc, table) => {
                acc[table.table_uuid] = table.reservation_start.split('T')[1].slice(0, 5);
                return acc;
            }, {});
            setSelectedTimes(initialTimes);
        })();
    }, [tableReservation]);

    useEffect(() => {
        console.log(tableReservation.reservation.reservation_start.slice(11, 16))
    }, [])

    const handleInputSubmit = async (values) => {
        if (!/^\+7\d{10}$/.test(values.phone)) {
            setErrorPhone(true);
            return;
        }
        const formattedDateTime = `${values.dateSelect} ${values.timeSelect}:00`;

        const clientPhoneRes = await axios.patch(
            'https://rovesnik-bot.ru/api/client/update_phone',
            {
                chat_id: tableReservation.reservation.client_chat_id,
                phone: values.phone,
            }
        );
        if (clientPhoneRes.data.Status === 'Failed') {
            setErrorPhone(true);
            return;
        }
        try {
            const newTableData = {
                ...receivedTable,
                is_available: true,
            };
            // const uuidRes = await ReservationService.uuid(
            //     tableReservation.reservation.order_uuid
            // );
            //
            // const checkAbility = await ReservationService.checkAbility(
            //     tableReservation.reservation.reserve_id
            // );
            //
            // if (checkAbility.data.Status === 'Failed') {
            //     setErrorBefore2hours(true);
            //     return;
            // }
            const promises = allTablesByUUID.map(async (table) => {
                const formattedDateTime = `${values.dateSelect} ${selectedTimes[table.table_uuid]}:00`;
                return await ReservationService.update({
                    reserve_id: tableReservation.reservation.reserve_id,
                    reservation_start: values.dateSelect + ' ' + selectedTimes[table.table_uuid] + '.000',
                    table_uuid: table.table_uuid,
                    client_chat_id: table.client_chat_id
                });
            });

            const resRes = await Promise.all(promises);

            const failedResponse = resRes.find((res) => res.data.Status === 'Failed');

            if (failedResponse) {
                (failedResponse.data.Message.includes('rebook') ? setErrorBook(true) : failedResponse.data.Message.includes('behavior') ? setErrorSupport(true) : setErrorDate(true));
            } else {
                handleClose();
                window.location.reload();
            }

            await TablesService.update(newTableData);
            await axios.patch(
                'https://rovesnik-bot.ru/api/client/update_first_name',
                {
                    chat_id: tableReservation.reservation.client_chat_id,
                    first_name: values.name.split(' ')[0],
                }
            );
            await axios.patch(
                'https://rovesnik-bot.ru/api/client/update_last_name',
                {
                    chat_id: tableReservation.reservation.client_chat_id,
                    last_name: values.name.split(' ')[1],
                }
            );

        } catch (e) {
            console.log(e);
        }
    };

    const handleTableTimeChange = async (uuid, time) => {
        setSelectedTimes(prevState => ({
            ...prevState,
            [uuid]: time
        }));
        const dateToSend = allTablesByUUID.find((table) => table.table_uuid === uuid).reservation_start.slice(0, 10) + ' ' + time + ':00.000';
        const res = await TablesService.checkAvailability( uuid, dateToSend);
        if (res.data.status == 'Failed') {
            setTableIdError(uuid)
        }
    };

    const handleCancelReservation = async () => {
        try {
            await ReservationService.cancel(tableReservation.reservation.reserve_id);
            setFilteredReservations(prevState => prevState.filter((item) => item.reservation.reserve_id !== tableReservation.reservation.reserve_id));
        } catch (e) {
            console.log(e);
        } finally {
            handleClose();
            setErrorDate(false);
        }
    };

    const formatDate = (isoString) => {
        const months = [
            'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
            'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
        ];

        const date = new Date(isoString);

        const day = date.getDate();
        const month = months[date.getMonth()];
        const year = date.getFullYear();
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');

        return `${day} ${month} ${year}, ${hours}:${minutes}`;
    };

    const getTimeSelectList = (initialTime) => {
        const timeSelectList = [];
        const isSameDate = selectedDate === tableReservation.reservation.reservation_start.split('T')[0];

        let initialDate;
        if (isSameDate) {
            initialDate = new Date(`1970-01-01T${initialTime}:00`);
        } else {
            initialDate = new Date(`1970-01-01T14:00:00`);
        }

        const maxDate = new Date(`1970-01-01T23:00:00`);
        const incrementHours = isSameDate ? 1 : 1;

        while (initialDate <= maxDate) {
            const hours = initialDate.getHours().toString().padStart(2, '0');
            const minutes = initialDate.getMinutes().toString().padStart(2, '0');
            timeSelectList.push(`${hours}:${minutes}`);
            initialDate = new Date(initialDate.getTime() + incrementHours * 60 * 60 * 1000);
        }

        return timeSelectList;
    };

    return (
        <Modal
            open={isOpen}
            onClose={handleClose}
            className="w-4/5 mx-10 flex justify-center items-center"
        >
            <div
                className={`${theme === 'dark' ? 'bg-neutral-900 text-neutral-100 border-blue-500 border' : 'bg-white'} p-6 rounded-2xl`}
            >
                <Formik
                    initialValues={{
                        dateSelect:
                            tableReservation.reservation.reservation_start.split('T')[0],
                        timeSelect: tableReservation.reservation.reservation_start
                            .split('T')[1]
                            .slice(0, 5),
                        name: receivedClient?.first_name + ' ' + receivedClient?.last_name,
                        phone: receivedClient?.phone,
                    }}
                    onSubmit={(values) => {
                        handleInputSubmit(values);
                    }}
                >
                    {({ handleSubmit, handleChange, values, setFieldValue }) => (
                        <Form>
                            <button onClick={handleClose}>
                                <img
                                    className={styles.closeCrossButton1}
                                    src={closeCross}
                                    alt="closeBtn"
                                />
                            </button>
                            <h1 className="font-bold text-xl">Бронь стола №{tableReservation.table.table_id}</h1>
                            <div
                                className={`mt-2`}
                                style={{ display: 'flex', marginBottom: '10px' }}
                            >
                                <Field
                                    name="name"
                                    placeholder="Имя Фамилия"
                                    className={`rounded-md ${theme === 'dark' ? 'bg-neutral-700 text-neutral-100' : 'bg-neutral-200'} ${styles.fieldName}`}
                                    style={{
                                        width: '100%',
                                        textColor: 'black',
                                    }}
                                />
                            </div>
                            <div
                                className={'mt-2'}
                                style={{ display: 'flex', marginBottom: '10px' }}
                            >
                                <Field
                                    name="phone"
                                    placeholder="Номер телефона"
                                    type="tel"
                                    className={`rounded-md ${theme === 'dark' ? 'bg-neutral-700 text-neutral-100' : 'bg-neutral-200'} ${styles.fieldName}`}
                                    style={{ width: '100%' }}
                                    pattern="^\+7\d{10}$"
                                />
                            </div>
                            <div
                                className={styles.inputRow}
                                style={{ display: 'flex', marginBottom: '10px' }}
                            >
                                <Field
                                    name="dateSelect"
                                    as={Select}
                                    displayEmpty={true}
                                    label="Дата"
                                    className={`rounded-md ${theme === 'dark' ? 'bg-neutral-400 text-neutral-100' : 'bg-white'}`}
                                    style={{ width: '50%', marginRight: '5px' }}
                                    value={selectedDate}
                                    onChange={(e) => {
                                        setFieldValue('dateSelect', e.target.value);
                                        setSelectedDate(e.target.value);
                                    }}
                                >
                                    {Array.from({ length: 20 }).map((_, i) => {
                                        const newDateTimestamp = addDaysToDate(new Date(tableReservation.reservation.reservation_start), i)
                                            .toISOString()
                                            .split('T')[0];
                                        return (
                                            <MenuItem key={i} value={newDateTimestamp}>
                                                {convertTimestampToDateString(newDateTimestamp)}
                                            </MenuItem>
                                        );
                                    })}
                                </Field>
                                <Select
                                    name="timeSelect"
                                    displayEmpty
                                    label="Время"
                                    className={`rounded-md ${theme === 'dark' ? 'bg-neutral-400 text-neutral-100' : 'bg-white'}`}
                                    style={{ width: '50%' }}
                                    value={values.timeSelect}
                                    onChange={handleChange}
                                    renderValue={(value) => value || 'Время'}
                                >
                                    {getTimeSelectList(tableReservation.reservation.reservation_start.slice(11, 16)).map((time) => (
                                        <MenuItem key={time} value={time}>
                                            {time}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </div>
                            <div className='flex flex-col gap-2'>
                                <h2>Столы:</h2>
                                {allTablesByUUID.length > 0 && Array.isArray(allTablesByUUID) && allTablesByUUID.filter(table => table.table.is_bowling === true || table.table.is_pool === true).map((table) => (
                                    <div key={table.table_uuid} className={`p-2 rounded-lg ${theme === 'dark' ? 'bg-neutral-700 text-neutral-100' : 'bg-neutral-200 bg-neutral-300'}`}>
                                        <div className='flex gap-2 items-center'>
                                            {table.table.is_bowling ? <BowlingSvg /> : <PoolSvg />}
                                            <p className='font-bold'>{table.table.is_bowling === true ? 'Боулинг' : 'Бильярд'}</p>
                                        </div>
                                        <p>
                                            {formatDate(selectedDate).toString().slice(0, 12)}
                                        </p>
                                        <Select
                                            value={selectedTimes[table.table_uuid] || table.reservation_start.split('T')[1].slice(0, 5)}
                                            onChange={(e) => handleTableTimeChange(table.table_uuid, e.target.value)}
                                            displayEmpty
                                            renderValue={(value) => value || 'Выберите время'}
                                            className={`rounded-md ${theme === 'dark' ? 'bg-neutral-400 text-neutral-100' : 'bg-white'}`}
                                            style={{ width: '100%' }}
                                        >
                                            {getTimeSelectList(table.reservation_start.split('T')[1].slice(0, 5)).map((time) => (
                                                <MenuItem key={time} value={time}>
                                                    {time}
                                                </MenuItem>
                                            ))}
                                        </Select>
                                        {tableIdError === table.table_uuid && <div className="mt-4 text-red-500">Стол недоступен в данное время</div>}
                                    </div>
                                ))}
                            </div>
                            {errorBook && <div className="mt-4 text-red-500">Стол уже забронирован.</div>}
                            {errorDate && <div className="mt-4 text-red-500">Нельзя забронировать на выбранную дату.</div>}
                            {errorPhone && <div className="mt-4 text-red-500">Неверный номер телефона.</div>}
                            {errorBefore2hours && <div className="mt-4 text-red-500">Заказ нельзя изменить менее чем за 2 часа.</div>}
                            {errorSupport && <div className="mt-4 text-red-500">Ошибка. Свяжитесь с техподдержкой.</div>}
                            <div className="mt-4 flex justify-end">
                                <button
                                    type="button"
                                    className="mr-2 py-2 px-4 bg-gray-300 hover:bg-gray-400 text-gray-800 font-semibold rounded-lg shadow-md"
                                    onClick={handleCancelReservation}
                                >
                                    Отменить бронирование
                                </button>
                                <button
                                    type="submit"
                                    className="py-2 px-4 bg-blue-500 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md"
                                    onClick={() => handleSubmit()}
                                >
                                    Обновить бронь
                                </button>
                            </div>
                        </Form>
                    )}
                </Formik>
            </div>
        </Modal>
    );
};

export default ReservationModal;
