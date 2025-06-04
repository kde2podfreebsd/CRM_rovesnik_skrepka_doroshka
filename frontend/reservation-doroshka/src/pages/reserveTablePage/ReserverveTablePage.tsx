import {Checkbox, FormControlLabel, FormGroup, Modal, Radio, RadioGroup} from '@mui/material'
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
  reservationPayment,
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
import {useQuery} from "@tanstack/react-query";
import ReserveModal from "./ReserveModal";
import floorImage from '../../shared/assets/floor.png'

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
  const [isBowling, setIsBowling] = useState(false)
  const [phoneError, setPhoneError] = useState(false)
  const [twiceBookError, setTwiceBookError] = useState(false)
  const [isPool, setIsPool] = useState(false)
  const [paymentURL, setPaymentURL] = useState('');
  const [paymentStatus, setPaymentStatus] = useState('');

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

  const handleOpen = () => {
    setIsOpen(true)
  }
  const handleClose = () => {
    setIsOpen(false)
    if (currentStep === 2) navigate('/my/reservations?barId=3')
  }

  const { theme } = useTheme()
  const rootClassName = theme === 'dark' ? styles.darkRoot : styles.lightRoot
  const mainClassName1 = theme === 'dark' ? styles.darkMain : styles.lightMain
  const arrowLeftTheme = theme === 'dark' ? arrowLeftDark : arrowLeftLight
  const arrowRightTheme = theme === 'dark' ? arrowRightDark : arrowRightLight
  const modalContentTheme =
      theme === 'dark' ? styles.modalContentDark : styles.modalContentLight


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

  return (
        <div className={`${styles.root} ${rootClassName} min-h-screen`}>
          <Header type="reservations" />
          <div className={`${styles.main} ${mainClassName1}`}>
            <h1>{'Забронировать стол'}</h1>
            <ReservationForm
                setReservationUserData={setReservationUserData}
                setAvailableTables={setAvailableTables}
                setSelectedTable={setSelectedTable}
            />
            <img src={floorImage} alt="" className={ styles.floor}/>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
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
                  <div>
                    <p className={'text-center font-bold text-xl mb-10'}>
                      Выберите время, количество гостей и нажмите поиск
                    </p>
                  </div>
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
            <ReserveModal
                isOpen={isOpen}
                handleClose={handleClose}
                receivedClient={ receivedClient }
                currentStep={currentStep}
                setCurrentStep={setCurrentStep}
                selectedTable={selectedTable}
                phoneError={phoneError}
                twiceBookError={twiceBookError}
                setTwiceBookError={setTwiceBookError}
                setPhoneError={setPhoneError}
                reservationUserData={reservationUserData}
                setReservationUserData={setReservationUserData}
                selectedReservationDate={selectedReservationDate}
                isBowling={isBowling}
                setIsBowling={setIsBowling}
                isPool={isPool}
                setIsPool={setIsPool}
                selectedFloor={selectedFloor}
                client_chat_id={client_chat_id}
                availableTables={availableTables}
            />
          </div>
          <div className='bot-0'>
            <Footer />
          </div>
        </div>
  )
}

export default ReserveTablePage
