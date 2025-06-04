import { Modal } from '@mui/material'
import React, { Suspense, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { v4 as uuidv4 } from 'uuid'

import Spinner from '../../compoments/Spinner'
import ReservationForm from '../../features/reservationForm'
const TableList = React.lazy(() => import('../../features/tableList'))
import {
  arrowLeftLight,
  arrowLeftDark,
  arrowRightLight,
  arrowRightDark,
  closeCross,
} from '../../shared/assets'
import {
  reservationsApiMockResponse,
} from '../../shared/constants'
import type { ReservationInfo } from '../../shared/types'
import Button from '../../shared/ui/button'
import Footer from '../../shared/ui/footer'
import Header from '../../shared/ui/header'
import { useTheme } from '../../shared/ui/themeContext/ThemeContext'
import { convertTimestampToDateString } from '../../shared/utils'

import styles from './styles.module.scss'
import { Field, Form, Formik } from 'formik'
import axios from 'axios'
import ReservationService from '../../api/ReservationService'
import { ITable } from '../../api/TablesService'
import floorImage from '../../../public/floor1.png'

export interface IReservationUserData {
  name: string
  phone: string
  guestsCount: number
  date: string
}

const ReserveTablePage = () => {
  const client_chat_id = window.Telegram.WebApp.initDataUnsafe?.user?.id ?? 272324534
  const navigate = useNavigate()
  const [isOpen, setIsOpen] = useState(false)
  const [currentStep, setCurrentStep] = useState(1)
  const [selectedFloor, setSelectedFloor] = useState(1)
  const selectedReservationDate: ReservationInfo =
      reservationsApiMockResponse[1] // useSelector(selectCurrentReservationDate(selectedTable.id))

  const [selectedTable, setSelectedTable] = useState<ITable | null>(null)
  const [availableTables, setAvailableTables] = useState<ITable[]>([])
  const [receivedClient, setReceivedClient] = useState<any>()
  const [reservationUserData, setReservationUserData] =
      useState<IReservationUserData>({
        name: '',
        phone: '',
        guestsCount: 2,
        date: '',
      })
  const [phoneError, setPhoneError] = useState(false)
  const [twiceBookError, setTwiceBookError] = useState(false)

  useEffect(() => {
    (async () => {
      const clientRes = await axios.get(
          'https://rovesnik-bot.ru/api/client/' + client_chat_id,
      )
      setReceivedClient(clientRes.data)
      setReservationUserData((prevState) => ({
        ...prevState,
        name: clientRes.data.first_name + ' ' + clientRes.data.last_name,
        phone: clientRes.data.phone,
      }))
    })()
  }, [])

  const handleTableSelection = (table: ITable) => {
    setSelectedTable(table)
  }

  const reserveTable = async (values: any) => {
    console.log(reservationUserData)
    if (!/^\+7\d{10}$/.test(values.phone)) {
      console.log(/^\+7\d{10}$/.test(values.phone))
      setPhoneError(true)
      return
    }

    try {
      const dataToSend = {
        client_chat_id: client_chat_id,
        table_uuid: selectedTable.table_uuid,
        reservation_start: reservationUserData.date + '.000',
        deposit: 0,
        order_uuid: uuidv4().toString(),
      }
      const res = await ReservationService.create(dataToSend)
      if (res.data.Status === 'Failed' && res.data.Message.includes('ability')) {
        setTwiceBookError(true)
        return
      }
      const [firstName, ...lastNameParts] = values.name.split(' ')
      const lastName = lastNameParts.join(' ')

      const clientFirstRes = await axios.patch(
          'https://rovesnik-bot.ru/api/client/update_first_name',
          {
            chat_id: client_chat_id,
            first_name: firstName,
          },
      )
      const clientLastNameRes = await axios.patch(
          'https://rovesnik-bot.ru/api/client/update_last_name',
          {
            chat_id: client_chat_id,
            last_name: lastName,
          },
      )

      const clientPhoneRes = await axios.patch(
          'https://rovesnik-bot.ru/api/client/update_phone', {
            chat_id: client_chat_id,
            phone: values.phone,
          }
      )

      console.log(clientFirstRes)
      console.log(clientLastNameRes)
      console.log(clientPhoneRes)
      navigate('/skrepka/my/reservations?barId=2')
    } catch (e) {
      console.log(e)
    }
  }
  const handleOpen = () => setIsOpen(true)
  const handleClose = () => {
    setIsOpen(false)
    if (currentStep === 2) navigate('/skrepka/my/reservations?barId=2')
  }

  const { theme } = useTheme()
  const rootClassName = theme === 'dark' ? styles.darkRoot : styles.lightRoot
  const mainClassName1 = theme === 'dark' ? styles.darkMain : styles.lightMain
  const arrowLeftTheme = theme === 'dark' ? arrowLeftDark : arrowLeftLight
  const arrowRightTheme = theme === 'dark' ? arrowRightDark : arrowRightLight
  const modalContentTheme =
      theme === 'dark' ? styles.modalContentDark : styles.modalContentLight
  const floorImages = ['/floor1.png', '/floor2.png', '/floor3.png']

  const handleInputSubmit = (values: any) => {
    setReservationUserData((prevState) => ({
      ...prevState,
      name: values.name,
      phone: values.phone,
    }))
  }

  const findAvailableFloor = (availableTables: ITable[]) => {
    for (let i = 1; i <= 3; i++) {
      const tablesOnFloor = availableTables.filter(table => table.storey === i);
      if (tablesOnFloor.length > 0) {
        return i;
      }
    }
    return null;
  }

  useEffect(() => {
    const floor = findAvailableFloor(availableTables);
    if (floor !== null) {
      setSelectedFloor(floor);
    }
  }, [availableTables]);

  const formatDate = (dateTimeString: string) => {
    const date = new Date(dateTimeString);
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return date.toLocaleDateString('ru-RU', options);
  }

  const formatTime = (dateTimeString: string) => {
    const date = new Date(dateTimeString);
    const options = { hour: 'numeric', minute: 'numeric' };
    return date.toLocaleTimeString('ru-RU', options);
  }

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
        <div className={`${styles.root} ${rootClassName}`}>
          <Header type="reservations" />
          <div className={`${styles.main} ${mainClassName1}`}>
            <h1>{'Забронировать стол'}</h1>
            {/*<p>*/}
            {/*  {*/}
            {/*    'Обратите внимание! Если вы хотите забронировать стол на 2+ часа, тогда свяжитесь с нашим менеджером.'*/}
            {/*  }*/}
            {/*</p>*/}
            <ReservationForm
                setReservationUserData={setReservationUserData}
                setAvailableTables={setAvailableTables}
                setSelectedTable={setSelectedTable}
            />
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <img src={floorImage} alt="" className={ styles.floor}/>
              {availableTables.length > 0 && availableTables ? (
                      availableTables.filter(table => table.storey === selectedFloor).length > 0 &&
                      <TableList
                          onTableSelect={handleTableSelection}
                          tables={availableTables.filter(table => table.storey === selectedFloor)}
                          selectedFloor={selectedFloor}
                          setSelectedTable={setSelectedTable}
                          selectedTable={selectedTable}
                      />
              ) : (
                  <p className={'text-center font-bold text-xl mb-10'}>
                    Выберите время, количество гостей и нажмите поиск
                  </p>
              )}
            </div>
            {availableTables.find((table) => table.storey === selectedFloor) ? (
                <button
                    className='rounded-full w-full bg-blue-500 py-4 text-white font-semibold my-6'
                    onClick={handleOpen}
                >
                  Забронировать стол
                </button>
            ) : (
                availableTables.length > 0 ? <p>Нет свободных столов на данном этаже</p> : null
            )}

            <Modal
                open={isOpen}
                onClose={handleClose}
                className="w-4/5 mx-10 flex justify-center items-center"
            >
              <div
                  className={`${theme === 'dark' ? 'bg-neutral-900 text-neutral-100 border-blue-500 border' : 'bg-white'} p-6 rounded-2xl flex flex-col justify-center items-center`}
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
                            name:
                                receivedClient
                                    ? `${receivedClient?.first_name} ${receivedClient?.last_name}`
                                    : '',
                            phone: receivedClient?.phone ?? '+7'
                          }}
                          onSubmit={(values) => {
                            handleInputSubmit(values)
                            reserveTable(values)
                          }}
                      >
                        {({ handleSubmit }) => (
                            <Form onSubmit={handleSubmit}>
                              {' '}
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
                                    phoneError &&
                                    <p className="text-red-500">Неверный формат номера телефона. <br/> Например:
                                      +79999999999</p>
                                }
                                {
                                    twiceBookError && <p className="text-red-500">Вы уже бронировали стол сегодня</p>
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
                              <div className={styles.buttons}>
                                <button
                                    className={'rounded-full w-full bg-blue-500 py-4 text-white font-semibold'}
                                    onClick={handleSubmit}
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
                        <img src={closeCross} alt="closeBtn"/>
                      </button>
                      <h1>Спасибо!</h1>
                      <p>{`Стол забронирован для Вас на ${convertTimestampToDateString(selectedReservationDate.date)} в ${selectedReservationDate.time}. Ждём в нашем заведении!`}</p>
                    </div>
                )}
              </div>
            </Modal>
          </div>
          <Footer />
        </div>
  )
}

export default ReserveTablePage
