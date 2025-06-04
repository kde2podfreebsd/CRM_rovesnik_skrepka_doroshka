import { Modal } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import React, { useEffect, useState, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'

import { FormValidationContext } from '../../app/context'
import { useAppSelector } from '../../app/hooks/redux'
import useGetBarData from '../../app/hooks/useGetBarData'
import { getArtistsByEventId } from '../../entities/artist/api'
import { fetchEventDataById } from '../../entities/event/api'
import {
  defaultGuestListNumber,
  shortEventTypeToWordsMap,
} from '../../shared/constants'
import Button from "../../shared/ui/button";
import EventCard from "../../widgets/eventCard";
import GuestList from '../../widgets/guestList'

import styles from './styles.module.scss'

import {
  fetchTicketById,
  purchaseFreeTickets,
  purchaseTicket,
  updateTicket,
} from '../../entities/ticket/api'
import { selectTicketByEventId, selectUID } from '../../entities/user/userSlice'
import type {EventTypeShort, GuestInviteForm, TEvent} from '../../shared/types'
import { useTheme } from '../../shared/ui/themeContext/ThemeContext'
import Lineup from '../../features/lineup'
import {selectEventById, setEvents} from '../../entities/event/eventSlice'
import { fetchUserTicketsByUID } from '../../entities/user/api'
import Spinner from "../../compoments/Spinner";
import axios from "axios";

type Props = {
  eventId: number
  ticketId?: number
  pageType?: 'userPage' | 'default'
  purchaseType: string
  setPurchaseType: React.Dispatch<React.SetStateAction<string>>
  isEventModalOpen: boolean
  setIsEventModalOpen: React.Dispatch<React.SetStateAction<boolean>>
}

const EventDetailsPage = ({
                            eventId,
                            ticketId,
                            pageType = 'default',
                            purchaseType,
                            setPurchaseType,
                            isEventModalOpen,
                            setIsEventModalOpen,
                          }: Props) => {
  // const [userFirstName, userLastName, username] = [
  //   Telegram.WebApp.initDataUnsafe.user?.first_name,
  //   Telegram.WebApp.initDataUnsafe.user?.last_name,
  //   Telegram.WebApp.initDataUnsafe.user?.username,
  // ]
  const userId =
      Telegram.WebApp.initDataUnsafe.user?.id ?? useAppSelector(selectUID)
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [barId] = useGetBarData(searchParams)
  const ticketFriendsData =
      useAppSelector((state) => selectTicketByEventId(state, eventId))?.friends ||
      null
  const ticketID = useAppSelector( (state) => selectTicketByEventId(state, eventId))?.id
  const [eventData, setEventData] = useState<TEvent>()
  const eventType = eventData?.event_type

  const [guestList, setGuestList] = useState<GuestInviteForm[]>(
      ticketFriendsData
          ? ticketFriendsData
          : []
  )
  const [isValid, setIsValid] = useState(false)
  const [showErrorLabel, setShowErrorLabel] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [shouldBuyWithBonuses, setShouldBuyWithBonuses] = useState(false)
  const [purchaseResetter, setPurchaseResetter] = useState(false)
  const { data, isLoading } = useQuery({
    queryKey: ['fetchEvent', eventId],
    queryFn: async () =>
        ticketId === undefined
            ? fetchEventDataById(eventId)
            : fetchTicketById(ticketId),
  })

  const [artistData, setArtistData] = useState([])
  const [isArtistLoading, setIsArtistLoading] = useState(true)
  const [artistError, setArtistError] = useState(null)
  const okRef = useRef(null)

  useEffect(() => {
    (async () => {
      const res = await axios.get( `https://rovesnik-bot.ru/api/event/` + eventId);
      setEventData(res.data)
      console.log(res)
    })()

    return () => {
      setIsEventModalOpen(false)
    }
  }, []);

  useEffect(() => {
    const fetchArtists = async () => {
      try {
        setIsArtistLoading(true)
        const data = await getArtistsByEventId(eventId)
        setArtistData(data)
        setIsArtistLoading(false)
      } catch (error) {
        setArtistError(error)
        setIsArtistLoading(false)
      }
    }

    fetchArtists()
  }, [eventId])

  const {
    data: ticketStatusData,
    isLoading: isStatusLoading,
    refetch,
  } = useQuery({
    refetchOnWindowFocus: false,
    queryKey: ['ticketStatus', eventId, eventType],
    queryFn: async () => {
      if (eventType === 'free')
        return pageType === 'userPage'
            ? updateTicket(eventId, userId, guestList)
            : guestList !== undefined
            ? purchaseFreeTickets(eventId, userId, guestList)
            : purchaseFreeTickets(eventId, userId)
      else if (eventType === 'deposit')
        return purchaseTicket(userId, shouldBuyWithBonuses, eventData)
      else return purchaseTicket(userId, shouldBuyWithBonuses, eventData)
    },
    enabled: false,
  })

  const { data: isAlreadyPurchased, isLoading: alreadyPurchasedLoading } =
      useQuery({
        queryKey: ['checkIfUserHasTicketForThisEvent'],
        queryFn: async () => {
          const userTickets = await fetchUserTicketsByUID(userId)
          return (
              userTickets.filter((ticket) => ticket.event_id === eventId).length > 0
          )
        },
      })



  useEffect(() => {
    if (
        !isStatusLoading &&
        ticketStatusData &&
        eventType !== 'free' &&
        !shouldBuyWithBonuses &&
        ticketStatusData.PaymentURL
    ) {
      window.location = ticketStatusData.PaymentURL as Location & string
    }
  }, [isStatusLoading, ticketStatusData])

  useEffect(() => {
    if (!isLoading && purchaseType !== '') buyTickets(eventType)
  }, [shouldBuyWithBonuses, purchaseResetter])

  const buyTickets = (eventType: EventTypeShort = 'free') => {
    switch (eventType) {
      case 'free':
        refetch();
        break;
      case 'event':
      case 'deposit':
        refetch();
        break;
      default:
        break;
    }
    setIsModalOpen(true);
    okRef?.current?.click()
  }

  const redirectOnSuccess = () => {
    navigate(0)
  }

  const redoPurchase = () => {
    setPurchaseResetter((prev) => !prev)
  }

  const { theme } = useTheme()
  const mainClassName1 = theme === 'dark' ? styles.darkMain : styles.lightMain

  const handleClose = () => {
    setIsEventModalOpen(false)
  }

  const handleDeleteTicket = async () => {
      await axios.delete('https://rovesnik-bot.ru/api/ticket/delete/' +  ticketID)
      navigate(0)
  }

  if (!eventData) {
    return <Spinner />
  }

  return (
      <div className='overflow-x-hidden'>
        <Modal
            className={`w-full h-full min-h-screen flex justify-center items-center overflow-y-hidden overflow-x-hidden pb-8 font-sans`}
            open={isEventModalOpen}
            onClose={handleClose}
        >
          <div
              className={`w-10/12 h-4/5 ${theme === 'dark' ? 'bg-neutral-800' : 'bg-white'} overflow-y-scroll rounded-lg pb-2 border-4 border-blue-500`}
          >
            {!isLoading && (
                <div>
                  <div>
                    <EventCard data={data} showUpperBubble cardType="description" />
                  </div>
                  <div
                      className={`${styles.main} ${mainClassName1} p-2 ${theme === 'dark' ? 'text-neutral-100' : ''}`}
                  >
                    <div className={styles.mainAboutEvents}>
                      <h1 className="font-bold text-2xl py-4 pl-2">О событии</h1>
                      <p className="px-2">{data!.description}</p>
                    </div>
                    <div className="flex flex-col gap-4 justify-start items-start overflow-x-hidden">
                      {isArtistLoading && <Spinner />}
                      {artistError && <p>{artistError.message}</p>}
                      {!isArtistLoading && artistData && artistData.length > 0 && (
                          <>
                            <h2 className="font-bold text-2xl py-4 pl-2">Лайн-ап</h2>
                            <Lineup artists={artistData} />
                          </>
                      )}
                    </div>

                    <div className='w-full flex justify-center items-center'>
                      {!alreadyPurchasedLoading &&
                      isAlreadyPurchased &&
                      (pageType === 'userPage' ? eventType !== 'free' : true) ? (
                          <div className='w-full flex justify-center items-center'>
                            <button
                                className='w-full mx-4 text-center text-white font-bold text-lg py-2 bg-blue-500 rounded-full z-10 mt-8'
                            >
                              {shortEventTypeToWordsMap.get(eventType) ===
                              'Бесплатная вечеринка'
                                  ? 'Вы зарегистрированы'
                                  : 'У вас уже есть билет'}
                            </button>
                          </div>
                      ) : (
                          <div className={styles.btnIndentation}>
                            {shortEventTypeToWordsMap.get(eventType) ===
                                'Бесплатная вечеринка' && (
                                    <div className='flex justify-center items-center flex-col gap-4 p-4'>
                                      <GuestList
                                          pageType={pageType}
                                          guestList={guestList}
                                          setGuestList={setGuestList}
                                      />
                                      <button
                                          className='w-full mx-4 text-center text-white font-bold text-lg py-2 bg-blue-500 rounded-full z-10 mt-2'
                                          onClick={() => buyTickets('free')}
                                      >
                                        Зарегистрироваться
                                      </button>
                                    </div>
                                )}
                            {shortEventTypeToWordsMap.get(eventType) === 'Депозит' && (
                                <div className=' flex justify-center items-center flex-col gap-2 mt-4 w-full'>
                                  <h3 className={ 'font-bold text-2xl text-center'}>Цена: {data!.price}</h3>
                                  <button
                                      className='w-full text-center text-white font-bold text-lg py-2 bg-blue-500 rounded-full z-10 px-16'
                                      onClick={() => {
                                        setShouldBuyWithBonuses(false)
                                        setPurchaseType('deposit')
                                        redoPurchase()
                                      }}
                                  >
                                    Внести депозит
                                  </button>
                                </div>
                            )}
                            {shortEventTypeToWordsMap.get(eventType) === 'Ивент' && (
                                <div className='flex justify-center items-center'>
                                  <div className='w-4/5 flex flex-col gap-2 justify-center items-center'>
                                    <h3 className='font-bold text-2xl text-center'>Цена: {data!.price}</h3>
                                    <button
                                        className='px-8 w-full mx-4 text-center text-white font-bold text-lg py-2 bg-blue-500 rounded-full z-10'
                                        onClick={() => {
                                          setShouldBuyWithBonuses(false)
                                          setPurchaseType('event')
                                          redoPurchase()
                                        }}
                                    >
                                      Купить билет
                                    </button>
                                    <button
                                        className='px-8 w-full mx-4 text-center text-white font-bold text-md py-2 bg-blue-500 rounded-full z-10'
                                        onClick={() => {
                                          setShouldBuyWithBonuses(true)
                                          setPurchaseType('event')
                                          redoPurchase()
                                        }}
                                    >
                                      Купить билет баллами
                                    </button>
                                  </div>
                                </div>
                            )}
                          </div>
                      )}
                    </div>
                    {!alreadyPurchasedLoading &&
                        isAlreadyPurchased &&
                        eventType === 'free' && (
                            <div className='w-full flex justify-center items-center'>
                              <button
                                  className='w-full mx-4 text-center text-white font-bold text-lg py-2 bg-red-500 rounded-full z-10 mt-8'
                                  onClick={() => {
                                    handleDeleteTicket()
                                  }}
                              >
                                Отменить бронь
                              </button>
                            </div>
                        )}
                  </div>
                  <Modal
                      ref={okRef}
                      className={`w-full h-full min-h-screen flex justify-center items-center overflow-y-hidden overflow-x-hidden pb-8 font-sans`}
                      open={isModalOpen}>
                    <div
                        className={` w-3/5 ${theme === 'dark' ? 'bg-neutral-800 text-neutral-100' : 'bg-white text-black'} rounded-lg} p-6 rounded-lg`}>
                      {isStatusLoading && (
                          <Spinner>
                            <p>Ваш запрос обрабатывается</p>
                          </Spinner>
                      )}
                      {!isStatusLoading && (
                          <div>
                            {(ticketStatusData?.status === 'Success' ||
                                ticketStatusData?.message ===
                                'Ticket purchased successfully') && (
                                <div>
                                  <p>Готово!</p>
                                  <Button
                                      text="Ок"
                                      onClick={redirectOnSuccess}
                                      className="z-20"
                                  />
                                </div>
                            )}
                            {ticketStatusData?.status !== 'Success' &&
                                ticketStatusData?.message !==
                                'Ticket purchased successfully' &&
                                !ticketStatusData?.PaymentURL && (
                                    <div className='flex flex-col justify-center items-center gap-4'>
                                      <p className={'text-center'}>
                                        Не хватает средств на баласне, оплатите картой или пополните баланс через телеграм бота
                                      </p>
                                      <button className='w-full mx-4 text-center text-white font-bold text-lg py-2 bg-blue-500 rounded-full z-10' onClick={() => setIsModalOpen(false)}>
                                        Закрыть
                                      </button>
                                    </div>
                                )}
                            {ticketStatusData?.PaymentURL && (
                                <div className='flex flex-col justify-center items-center gap-4'>
                                  <p className={'text-center'}>Перейдите по ссылке для завершения покупки</p>
                                  <a
                                      href={ticketStatusData?.PaymentURL}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="w-full mx-4 text-center text-white font-bold text-lg py-2 bg-blue-500 rounded-full z-10"
                                  >
                                    Перейти
                                  </a>
                                  <button className='w-full mx-4 text-center text-white font-bold text-lg py-2 bg-blue-500 rounded-full z-10' onClick={() => setIsModalOpen(false)}>
                                    Закрыть
                                  </button>
                                </div>
                            )}
                          </div>
                      )}
                    </div>
                  </Modal>
                </div>
            )}
          </div>
        </Modal>
      </div>
  );
}

export default EventDetailsPage