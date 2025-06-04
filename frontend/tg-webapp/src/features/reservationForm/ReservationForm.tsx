import React, {useEffect, useState} from 'react'

import {Input, MenuItem, Modal, Select, TextField} from '@mui/material'
import { Formik, Form, Field } from 'formik'
import Button from '../../shared/ui/button'
import { useTheme } from '../../shared/ui/themeContext/ThemeContext'
import { dateSelectRange, maxGuestCount } from '../../shared/constants'
import { addDaysToDate } from '../../shared/utils'

import styles from './styles.module.scss'
import { IReservationUserData } from '../../pages/reserveTablePage/ReserverveTablePage'
import TablesService, { ITable } from '../../api/TablesService'

const ReservationForm = ({
  setReservationUserData,
  setAvailableTables,
    setSelectedTable,
}: {
  setReservationUserData: React.Dispatch<
    React.SetStateAction<IReservationUserData>
  >
  setAvailableTables: React.Dispatch<React.SetStateAction<ITable[]>>
  setSelectedTable: React.Dispatch<React.SetStateAction<ITable | null>>
}) => {
  const date = new Date()
  const currentHoursPlus3 = () => {
    let hoursPlus3 = date.getHours() + 3;
    if (hoursPlus3 >= 24) {
      hoursPlus3 -= 24;
    }
    return hoursPlus3 >= 14 ? hoursPlus3 : 14;
  };


  const currentDate = new Date();
  const nextDay = new Date();
  nextDay.setDate(currentDate.getDate() + 1);
  const currentDateString = `${(currentDate.getHours() >= 21 ? nextDay : currentDate).getFullYear()}-${((currentDate.getHours() >= 21 ? nextDay : currentDate).getMonth() + 1).toString().padStart(2, '0')}-${((currentDate.getHours() >= 21 ? nextDay : currentDate).getDate()).toString().padStart(2, '0')}`;
  const [inputGuestCount, setInputGuestCount] = useState(1)
  const [inputDate, setInputDate] = useState(currentDateString)
  const [inputTime, setInputTime] = useState(currentHoursPlus3().toString().padStart(2, '0') + ':00')

  const getTimeSelectList = (date: Date) => {
    const currentDate = new Date();
    const currentDateString = `${currentDate.getFullYear()}-${(currentDate.getMonth() + 1).toString().padStart(2, '0')}-${currentDate.getDate().toString().padStart(2, '0')}`;

    const isCurrentDate = inputDate === currentDateString;

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
      for (let minute = 0; minute < 60; minute += 30) {
        const hourText = hour < 10 ? `0${hour}` : `${hour}`;
        const minuteText = minute === 0 ? '00' : `${minute}`;
        const time = `${hourText}:${minuteText}`;
        timeList.push(time);
      }
    }

    return timeList;
  };


  const timeSelectList = getTimeSelectList(date )
  const { theme } = useTheme()

  const [isOpen, setIsOpen] = useState(false)
  const [message, setMessage] = useState('1')
  const [buttonText, setButtonText] = useState('1')
  const [isSelectDateOpen, setIsSelectDateOpen] = useState(false)

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const options: Intl.DateTimeFormatOptions = {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
    }
    return new Intl.DateTimeFormat('ru-RU', options).format(date)
  }

  const handleInputSubmit = async (data?: { strInputGuestCount?: string | undefined; strInputDate?: string | undefined; strInputTime?: string | undefined;}) => {
    const values = {
      guestCount: data?.strInputGuestCount ? data?.strInputGuestCount : inputGuestCount,
      dateSelect: data?.strInputDate ? new Date(data?.strInputDate) : new Date(inputDate),
      timeSelect: data?.strInputTime ? data?.strInputTime : inputTime,
    };

    console.log(values);

    const findAvailableTable = async (guestCount) => {
      if (guestCount === 9) {
        setMessage('Нет доступных столиков для данного количества гостей');
        setButtonText('Изменить параметры');
        setIsOpen(true)
        setAvailableTables([])
        return
      }
      const dateWithoutTime = new Date(values.dateSelect);
      const time = values.timeSelect.split(':');

      let hour = parseInt(time[0], 10) + 1;
      const minute = parseInt(time[1], 10);

      if (hour >= 24) {
        hour -= 24;
        dateWithoutTime.setDate(dateWithoutTime.getDate() + 1);
      }

      dateWithoutTime.setHours(hour + 2); // Учитываем часовой пояс
      dateWithoutTime.setMinutes(minute);

      const formattedDateTime = dateWithoutTime
          .toISOString()
          .slice(0, 19)
          .replace('T', ' ');

      console.log(formattedDateTime);

      setReservationUserData((prevState) => ({
        ...prevState,
        date: formattedDateTime,
        capacity: guestCount,
      }));

      const res = await TablesService.getAll(formattedDateTime, guestCount);

      if (res.data.Status === 'Failed' && res.data.Message.includes('ongoing')) {
        setMessage(
            'К сожалению, в это время у нас будет проходить ивент, выберите другое время'
        );
        setButtonText('Изменить параметры');
        setIsOpen(true);
      } else if (res.data.Status === 'Failed' && res.data.Message.includes('capacity')) {
        await findAvailableTable(guestCount + 1);
      } else if (res.data.Status === 'Failed' && res.data.Message.includes('available')) {
        setMessage(
            'К сожалению, мы не нашли столы которые соответствуют вашему запросу, выберите другое время'
        );
        setButtonText('Изменить параметры');
        setIsOpen(true);
      } else {
        setAvailableTables(res.data.Message);
        setSelectedTable(res.data.Message[0]);
        console.log(res.data.Message[0]);
      }
    };

    if (values.guestCount < 10) {
      await findAvailableTable(values.guestCount);
    } else {
      setMessage(
          'Если вы хотите забронировать стол на 10+ человек, вам нужно связаться с менеджером'
      );
      setButtonText('Связаться');
      setIsOpen(true);
    }
  };


  const handleButton = () => {
    if (buttonText === 'Связаться') {
      const formattedDate = inputDate.replace(/-/g, '_');
      const formattedTime = inputTime.replace(/:/g, '_');
      window.open(`https://t.me/crm_head_test_bot?start=support_reserve_capacity_${inputGuestCount}_date_${formattedDate}_${formattedTime}`, '_blank');
    }
    setIsOpen(false)
  }
  return (
    <>
      <div className='w-full flex flex-col gap-3 mb-4'>
        <div>
          <Select
              type="text"
              className='w-full rounded-full bg-white'
              sx={{borderRadius: '40px', height: '40px'}}
              value={inputGuestCount}
              onChange={(e) => {
                handleInputSubmit( {strInputGuestCount: e.target.value} )
                setInputGuestCount(Number(e.target.value))
              }
          }
          >
            {[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15].map((value) => (
                <MenuItem key={value} value={value}>{value}</MenuItem>
            ))}
          </Select>
        </div>
        <div className='flex gap-2'>
          <Select
              type="text"
              className='w-full rounded-full bg-white'
              sx={{borderRadius: '40px', height: '40px'}}
              value={inputDate}
              renderValue={value => formatDate(value as string) || 'Дата'}
              onChange={(e) => {
                setInputDate(e.target.value as string)
                handleInputSubmit({strInputDate: e.target.value as string})
              }}
          >

          {Array.from({ length: dateSelectRange }).map((_, i) => {
              const newDateTimestamp = addDaysToDate(date, i)
                  .toISOString()
                  .split('T')[0] as string
              return (
                  <MenuItem key={i} value={newDateTimestamp}>
                    {formatDate(newDateTimestamp)}
                  </MenuItem>
              )
            })}
          </Select>
          <Select
              type="text"
              className='w-full rounded-full bg-white'
              size='small'
              sx={{borderRadius: '40px', height: '40px'}}
              value={inputTime}
              onChange={(e) => {
                handleInputSubmit({strInputTime: e.target.value as string})
                setInputTime(e.target.value as string)
                setIsSelectDateOpen(false)
              }}
              renderValue={value => value || 'Время'}
              open={isSelectDateOpen}
              onClose={() => setIsSelectDateOpen(false)}
              onOpen={() => setIsSelectDateOpen(true)}
              onSelect={() => setIsSelectDateOpen(false)}
          >

          {timeSelectList.map((time) => (
                <MenuItem value={time}>{time}</MenuItem>
            ))}
          </Select>
        </div>
        <div>
          <button className='rounded-full w-full bg-blue-500 py-2 text-white font-semibold active:scale-95 transition-all' onClick={() => handleInputSubmit(null)}>
            Найти
          </button>
        </div>
      </div>

      <Modal
        open={isOpen}
        className="w-4/5 mx-10 flex justify-center items-center"
      >
        <div
          className={`${theme === 'dark' ? 'bg-neutral-900 text-neutral-100 border-blue-500 border' : 'bg-white'} p-6 rounded-2xl`}
        >
          <p
            className={`${theme === 'dark' ? 'text-neutral-100' : 'text-neutral-900'}`}
          >
            {message}
          </p>
          <Button
            text={buttonText}
            onClick={() => handleButton()}
            type="realBlue"
            className={`text-white mt-4`}
          />
        </div>
      </Modal>
    </>
  )
}

export default ReservationForm
