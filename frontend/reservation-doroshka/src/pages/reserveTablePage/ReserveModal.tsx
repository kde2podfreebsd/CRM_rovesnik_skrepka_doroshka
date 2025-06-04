import React, {useEffect, useState} from 'react';
import styles from "./styles.module.scss";
import { closeCross } from "../../shared/assets";
import { Field, Form, Formik } from "formik";
import { Checkbox, FormControlLabel, FormGroup, MenuItem, Modal, Select } from "@mui/material";
import { convertTimestampToDateString } from "../../shared/utils";
import { useTheme } from "../../shared/ui/themeContext/ThemeContext";
import axios from 'axios';
import { reservationPayment } from "../../shared/constants";
import { v4 as uuidv4 } from 'uuid';
import ReservationService from "../../api/ReservationService";
import { useNavigate } from 'react-router-dom';
import { IReservationUserData } from "./ReserverveTablePage";
import { ReservationInfo } from "../../shared/types";
import TablesService, { ITable } from "../../api/TablesService";
import BowlingSvg from "../../shared/BowlingSVG";
import PoolSvg from "../../shared/PoolSVG";

interface props {
    isOpen: boolean
    handleClose: () => void
    receivedClient: any
    currentStep: number
    setCurrentStep: React.Dispatch<React.SetStateAction<number>>
    selectedTable: ITable
    phoneError: string
    twiceBookError: string
    setTwiceBookError: React.Dispatch<React.SetStateAction<boolean>>
    setPhoneError: React.Dispatch<React.SetStateAction<boolean>>
    reservationUserData: IReservationUserData
    isBowling: boolean
    isPool: boolean
    setIsBowling: React.Dispatch<React.SetStateAction<boolean>>
    setIsPool: React.Dispatch<React.SetStateAction<boolean>>
    selectedReservationDate: ReservationInfo
    setReservationUserData: React.Dispatch<React.SetStateAction<IReservationUserData>>
    client_chat_id: number
    availableTables: ITable[]
}

const ReserveModal = ({
                          isOpen,
                          handleClose,
                          receivedClient,
                          currentStep,
                          selectedTable,
                          phoneError,
                          twiceBookError,
                          setTwiceBookError,
                          setPhoneError,
                          reservationUserData,
                          selectedReservationDate,
                          client_chat_id,
                          setReservationUserData,
                            availableTables
                      }: props) => {
    const getTimeSelectList = (date: Date) => {
        const currentDate = new Date();
        const currentDateString = `${currentDate.getFullYear()}-${(currentDate.getMonth() + 1).toString().padStart(2, '0')}-${currentDate.getDate().toString().padStart(2, '0')}`;
        const isCurrentDate = selectedReservationDate.date === currentDateString;

        const hoursToSet = () => {
            if (date.getHours() >= 14 && isCurrentDate) {
                return date.getHours() + 1;
            } else {
                return 14;
            }
        };

        const startHour = hoursToSet();
        const endHour = 23;

        const timeList = [];

        for (let hour = startHour; hour <= endHour; hour++) {
            const hourText = hour < 10 ? `0${hour}` : `${hour}`;
            const time = `${hourText}:00`;
            timeList.push(time);
        }

        return timeList;
    };


    const { theme } = useTheme();
    const navigate = useNavigate();
    const [bowlingList, setBowlingList] = React.useState<{ start_time: string, table_uuid?: string }[]>([]);
    const [poolList, setPoolList] = React.useState<{ start_time: string, table_uuid?: string }[]>([]);
    const [isAddNewBowling, setIsAddNewBowling] = useState(false);
    const [isAddNewPool, setIsAddNewPool] = useState(false);
    const [bowlingError, setBowlingError] = useState(false);
    const [poolError, setPoolError] = useState(false);
    const [availableBowlingTables, setAvailableBowlingTables] = useState<ITable[]>([]);
    const [availablePoolTables, setAvailablePoolTables] = useState<ITable[]>([]);

    const formatDate = (dateTimeString: string) => {
        const date = new Date(dateTimeString);
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        return date.toLocaleDateString('ru-RU', options);
    };

    const formatTime = (dateTimeString: string) => {
        const date = new Date(dateTimeString);
        const options = { hour: 'numeric', minute: 'numeric' };
        return date.toLocaleTimeString('ru-RU', options);
    };

    const handleInputSubmit = (values: any) => {
        setReservationUserData((prevState) => ({
            ...prevState,
            name: values.name,
            phone: values.phone,
        }));
    };

    useEffect(() => {

        return () => {
            setBowlingError(false);
            setPoolError(false);
        }
    }, []);

    const reserveTable = async (values: any) => {
        if (!/^\+7\d{10}$/.test(values.phone)) {
            console.log(/^\+7\d{10}$/.test(values.phone));
            setPhoneError(true);
            return;
        }

        const availableBowlingRes = await TablesService.getBowling()
        if (availableBowlingRes.data.Status === 'Failed') {
            setBowlingError(true);
            return
        }

        const availablePoolRes = await TablesService.getPool()
        if (availablePoolRes.data.Status === 'Failed') {
            setPoolError(true);
            return
        }

        try {
            const [firstName, ...lastNameParts] = values.name.split(' ');
            const lastName = lastNameParts.join(' ');

            await axios.patch('https://rovesnik-bot.ru/api/client/update_first_name', {
                chat_id: client_chat_id,
                first_name: firstName,
            });
            await axios.patch('https://rovesnik-bot.ru/api/client/update_last_name', {
                chat_id: client_chat_id,
                last_name: lastName,
            });

            await axios.patch('https://rovesnik-bot.ru/api/client/update_phone', {
                chat_id: client_chat_id,
                phone: values.phone,
            });

            const price = () => {
                if (bowlingList.length > 0 && poolList.length > 0) {
                    console.log(bowlingList.length * 2000 + poolList.length * 1000)
                    return bowlingList.length * 2000 + poolList.length * 1000;
                } else if (poolList.length > 0) {
                    console.log(poolList.length * 1000)
                    return poolList.length * 1000;
                } else if (bowlingList.length > 0) {
                    console.log(bowlingList.length * 2000)
                    return bowlingList.length * 2000;
                } else {
                    return 0;
                }
            };
            const serializePoolTables = (tables: {start_time: string, table_uuid: string}[]) => {
                for (let i = 0; i < tables.length; i++) {
                    tables[i].table_uuid = availablePoolRes.data.Message[0].table_uuid
                }
                return tables
            }

            const serializeBowlingTables = (tables: {start_time: string, table_uuid: string}[]) => {
                for (let i = 0; i < tables.length; i++) {
                    tables[i].table_uuid = availableBowlingRes.data.Message[0].table_uuid
                }
                return tables
            }
            const dataToSend = {
                client_chat_id: client_chat_id,
                table_uuid: selectedTable!.table_uuid,
                date: reservationUserData.date + '.000',
                order_uuid: uuidv4().toString(),
                price: price() * 2,
                text: 'Оплата резервации столика в Дорожке' + (poolList.length > 0 ? ', Бильярд' : '') + (bowlingList.length > 0 ? ', Боулинг' : ''),
                bar_id: 3,
                bowlingTables: serializeBowlingTables( bowlingList ),
                poolTables: serializePoolTables( poolList ),
            }
            console.log(dataToSend)
            if (poolList.length > 0 || bowlingList.length > 0) {
                try {
                    const paymentRes = await reservationPayment(dataToSend);
                    if (paymentRes.Success) {
                        window.location.href = paymentRes.PaymentURL;
                    } else {
                        setTwiceBookError(true);
                    }
                } catch (e) {
                    console.log(e);
                }
            } else {
                try {
                    await axios.patch('https://rovesnik-bot.ru/api/client/update_first_name', {
                        chat_id: client_chat_id,
                        first_name: firstName,
                    });
                    await axios.patch('https://rovesnik-bot.ru/api/client/update_last_name', {
                        chat_id: client_chat_id,
                        last_name: lastName,
                    });

                    await axios.patch('https://rovesnik-bot.ru/api/client/update_phone', {
                        chat_id: client_chat_id,
                        phone: values.phone,
                    });
                    const dataToSend = {
                        client_chat_id: client_chat_id,
                        table_uuid: selectedTable!.table_uuid,
                        reservation_start: reservationUserData.date + '.000',
                        deposit: 0,
                        order_uuid: uuidv4().toString(),
                    };
                    const res = await ReservationService.create(dataToSend);
                    if (res.data.Status === 'Failed' && res.data.Message.includes('ability')) {
                        setTwiceBookError(true);
                        return;
                    }


                    navigate('/doroshka/my/reservations?barId=3');
                } catch (e) {
                    console.log(e);
                }
            }
        } catch (e) {
            console.log(e);
        }
    };

    const handleAddBowling = () => {
        if (bowlingList.length <= 4) {
            setBowlingList([...bowlingList, { start_time: ''}]);
            setIsAddNewBowling(true);
        }
    };

    const handleAddPool = () => {
        if (poolList.length <= 2) {
            setPoolList([...poolList, { start_time: ''}]);
            setIsAddNewPool(true);
        }
    };

    const handleDeleteBowling = (index: number) => {
        setBowlingList(prev => prev.filter((_, i) => i !== index));
    };

    const handleDeletePool = (index: number) => {
        setPoolList(prev => prev.filter((_, i) => i !== index));
    };

    const handleSelectStartTime = async (index: number, time: string, isBowling: boolean) => {
        if (isBowling) {
            const updatedList = [...bowlingList];
            updatedList[index].start_time = time;
            setBowlingList(updatedList);
            const res = await TablesService.getAll( reservationUserData.date.slice( 0, 10 ) + ' ' + time + ':00.000', 2 );
            console.log(reservationUserData.date)
        } else {
            const updatedList = [...poolList];
            updatedList[index].start_time = time;
            setPoolList(updatedList);
        }
    };

    // const handleSelectEndTime = (index: number, time: string, isBowling: boolean) => {
    //     if (isBowling) {
    //         const updatedList = [...bowlingList];
    //         updatedList[index].end_time = time;
    //         setBowlingList(updatedList);
    //     } else {
    //         const updatedList = [...poolList];
    //         updatedList[index].end_time = time;
    //         setPoolList(updatedList);
    //     }
    // };

    const timeSelectList = getTimeSelectList(new Date());
    const formatDateToISO = (dateTimeString: string) => {
        const date = new Date(dateTimeString.replace( ' ', 'T'));
        return date.toISOString();
    }

    const increaseSecondDigitByThree = (timeString) => {
        let [hours, minutes] = timeString.split(':').map(Number);

        hours += 3;

        if (hours >= 24) {
            hours -= 24;
        }

        const newHours = hours.toString().padStart(2, '0');
        const newTimeString = `${newHours}:${minutes.toString().padStart(2, '0')}`;

        return newTimeString;
    };

    return (
        <div>
            <Modal
                open={isOpen}
                onClose={handleClose}
                className="w-4/5 mx-10 flex justify-center items-center h-auto overflow-y-auto"
            >
                <div
                    className={` ${theme === 'dark' ? 'bg-neutral-900 text-neutral-100 border-blue-500 border' : 'bg-white'} p-6 rounded-2xl flex flex-col justify-center items-center`}
                >
                    {currentStep === 1 && (
                        <div>
                            <button onClick={handleClose}>
                                <img
                                    className={styles.closeCrossButton1}
                                    src={closeCross}
                                    alt="closeBtn"
                                />
                            </button>
                            <h1 className="font-bold text-xl my-2">Бронь стола</h1>
                            <Formik
                                initialValues={{
                                    name: receivedClient ? `${receivedClient?.first_name} ${receivedClient?.last_name}` : '',
                                    phone: receivedClient?.phone ?? '+7'
                                }}
                                onSubmit={(values) => {
                                    handleInputSubmit(values);
                                    reserveTable(values);
                                }}
                            >
                                {({ handleSubmit }) => (
                                    <Form onSubmit={handleSubmit}>
                                        <div className={styles.formFieldInfo}>
                                            <Field
                                                name="name"
                                                placeholder="Имя Фамилия"
                                                className={`rounded-md ${theme === 'dark' ? 'bg-neutral-700 text-neutral-100' : 'bg-neutral-200'} ${styles.fieldName}`}
                                            />
                                            <Field
                                                name="phone"
                                                type="tel"
                                                placeholder="Номер телефона"
                                                className={`rounded-md ${theme === 'dark' ? 'bg-neutral-700 text-neutral-100' : 'bg-neutral-200'} ${styles.fieldName}`}
                                                style={{
                                                    marginTop: '10px',
                                                    marginBottom: '10px',
                                                }}
                                                pattern="^\+7\d{10}$"
                                            />
                                            {
                                                phoneError && <p className="text-red-500">Неверный формат номера
                                                    телефона. <br/> Например: +79999999999</p>
                                            }
                                            {
                                                twiceBookError &&
                                                <p className="text-red-500">Вы уже бронировали стол сегодня</p>
                                            }
                                            {
                                                bowlingError &&
                                                <p className="text-red-500">Нет свободных столов для боулинга на
                                                    выбранную дату</p>
                                            }
                                            {
                                                poolError &&
                                                <p className="text-red-500">Нет свободных столов для бильярда на
                                                    выбранную дату</p>
                                            }
                                        </div>
                                        <p
                                            className={'mt-2 font-semibold'}
                                        >{`Количество человек: ${selectedTable?.capacity}`}</p>
                                        <p
                                            className={'mt-1'}
                                        >{`Стол №${selectedTable?.table_id}`}</p>
                                        <p
                                            className={'mt-1'}
                                        >{`Дата: ${formatDate(formatDateToISO(reservationUserData.date))}`}</p>
                                        <p
                                            className={'mt-1 mb-4'}
                                        >{`Время: ${increaseSecondDigitByThree(formatDateToISO(reservationUserData.date).toString().slice(11, 16))}`}</p>
                                        <p className='font-bold'>Добавить к брони:</p>
                                        <div className='flex flex-col gap-2 my-2 max-h-80 overflow-y-scroll'>
                                            {bowlingList.map((bowling, index) => (
                                                <div key={index} className='mb-4'>
                                                    <div className='flex gap-2 items-center'>
                                                        <BowlingSvg/>
                                                        <p className='font-normal'>Дорожка боулинга</p>
                                                    </div>
                                                    <div>
                                                        <div className='flex gap-2 items-center'>
                                                            <p>Время</p>
                                                            <Select
                                                                type="text"
                                                                className='w-full rounded-full bg-white'
                                                                size='small'
                                                                sx={{borderRadius: '40px', height: '40px'}}
                                                                value={bowling.start_time}
                                                                onChange={(e) => {
                                                                    handleSelectStartTime(index, e.target.value as string, true);
                                                                }}
                                                                renderValue={value => value || 'Начало'}
                                                            >
                                                                {timeSelectList.map((time) => (
                                                                    <MenuItem key={time} value={time}>{time}</MenuItem>
                                                                ))}
                                                            </Select>
                                                        </div>
                                                        {/*<div className='flex gap-2 items-center'>*/}
                                                        {/*    <p>До</p>*/}
                                                        {/*    <Select*/}
                                                        {/*        type="text"*/}
                                                        {/*        className='w-full rounded-full bg-white mt-2'*/}
                                                        {/*        size='small'*/}
                                                        {/*        sx={{ borderRadius: '40px', height: '40px' }}*/}
                                                        {/*        value={bowling.end_time}*/}
                                                        {/*        onChange={(e) => {*/}
                                                        {/*            handleSelectEndTime(index, e.target.value as string, true);*/}
                                                        {/*        }}*/}
                                                        {/*        renderValue={value => value || 'Конец'}*/}
                                                        {/*    >*/}
                                                        {/*        {timeSelectList.map((time) => (*/}
                                                        {/*            <MenuItem key={time} value={time}>{time}</MenuItem>*/}
                                                        {/*        ))}*/}
                                                        {/*    </Select>*/}
                                                        {/*</div>*/}
                                                        <button
                                                            className='text-white w-full bg-red-500 rounded-full mt-2 py-2 px-4'
                                                            onClick={() => handleDeleteBowling(index)}>
                                                            Удалить
                                                        </button>
                                                    </div>
                                                </div>
                                            ))}
                                            {poolList.map((pool, index) => (
                                                <div key={index}>
                                                    <div className='flex gap-2 items-center'>
                                                        <PoolSvg/>
                                                        <p>Бильярдный стол</p>
                                                    </div>
                                                    <div>
                                                        <div className='flex gap-2 items-center'>
                                                            <p>Время</p>
                                                            <Select
                                                                type="text"
                                                                className='w-full rounded-full bg-white'
                                                                size='small'
                                                                sx={{borderRadius: '40px', height: '40px'}}
                                                                value={pool.start_time}
                                                                onChange={(e) => {
                                                                    handleSelectStartTime(index, e.target.value as string, false);
                                                                }}
                                                                renderValue={value => value || 'Начало'}
                                                            >
                                                                {timeSelectList.map((time) => (
                                                                    <MenuItem key={time} value={time}>{time}</MenuItem>
                                                                ))}
                                                            </Select>
                                                        </div>
                                                        {/*<div className=' flex gap-2 items-center'>*/}
                                                        {/*    <p>До</p>*/}
                                                        {/*    <Select*/}
                                                        {/*        type="text"*/}
                                                        {/*        className='w-full rounded-full bg-white mt-2'*/}
                                                        {/*        size='small'*/}
                                                        {/*        sx={{borderRadius: '40px', height: '40px'}}*/}
                                                        {/*        value={pool.end_time}*/}
                                                        {/*        onChange={(e) => {*/}
                                                        {/*            handleSelectEndTime(index, e.target.value as string, false);*/}
                                                        {/*        }}*/}
                                                        {/*        renderValue={value => value || 'Конец'}*/}
                                                        {/*    >*/}
                                                        {/*        {timeSelectList.map((time) => (*/}
                                                        {/*            <MenuItem key={time} value={time}>{time}</MenuItem>*/}
                                                        {/*        ))}*/}
                                                        {/*    </Select>*/}
                                                        {/*</div>*/}
                                                        <button
                                                            className='text-white w-full bg-red-500 rounded-full mt-2 py-2 px-4'
                                                            onClick={() => handleDeletePool(index)}>
                                                            Удалить
                                                        </button>
                                                    </div>
                                                </div>
                                            ))}
                                            <button
                                                type="button"
                                                onClick={handleAddBowling}
                                                className='border-2 border-solid border-blue-500 py-2 px-4 text-sm rounded-full'>+
                                                Добавить дорожку боулинга
                                            </button>
                                            <button
                                                type="button"
                                                onClick={handleAddPool}
                                                className='border-2 border-solid border-blue-500 py-2 px-4 text-sm rounded-full'>+
                                                Добавить бильярдный стол
                                            </button>
                                        </div>
                                        <div className={styles.buttons}>
                                            <button
                                                className={'rounded-full w-full bg-blue-500 py-4 text-white font-semibold'}
                                                type="submit"
                                            >
                                                Забронировать
                                            </button>
                                        </div>
                                    </Form>
                                )}
                            </Formik>
                        </div>
                    )}
                    {currentStep === 2 && (
                        <div className={`${styles.modalContent} ${modalContentTheme}`}>
                            <button onClick={handleClose}>
                                <img src={closeCross} alt="closeBtn" />
                            </button>
                            <h1>Спасибо!</h1>
                            <p>{`Стол забронирован для Вас на ${convertTimestampToDateString(selectedReservationDate.date)} в ${selectedReservationDate.time}. Ждём в нашем заведении!`}</p>
                        </div>
                    )}
                </div>
            </Modal>
        </div>
    );
};

export default ReserveModal;
