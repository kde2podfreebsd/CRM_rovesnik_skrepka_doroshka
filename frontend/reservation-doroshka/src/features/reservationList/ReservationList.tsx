import React, { useEffect, useMemo, useState } from 'react'
import ReservationCard from '../reservationCard'
import { TEvent } from '../../shared/types'
import { mockApiResponse, msInADay, userPageEventTypes } from '../../shared/constants'
import EventCard from '../../widgets/eventCard'
import Button from '../../shared/ui/button'
import { useNavigate, useSearchParams } from 'react-router-dom'
import styles from './styles.module.scss'
import { useAppDispatch, useAppSelector } from '../../app/hooks/redux'
import { setTickets } from '../../entities/user/userSlice'
import { useQuery } from '@tanstack/react-query'
import { fetchUserTicketsByUID } from '../../entities/user/api'
import Spinner from '../../compoments/Spinner'
import { fetchEventDataById } from '../../entities/event/api'
import { splitDatetimeString } from '../../shared/utils'
import TabsSwitch from '../../shared/ui/tabsSwitch'
import { selectCurrentBarId } from '../../entities/bar/barSlice'

const ReservationList = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [searchParams] = useSearchParams();
  const currentBarId = searchParams.get('barId') === undefined ? useAppSelector(selectCurrentBarId): searchParams.get('barId');
  // todo
  const paymentSuccessEventId = searchParams.get('') ?? null;
  const uid = (searchParams.get('uid') || Telegram.WebApp.initDataUnsafe.user?.id) ?? undefined;
  const [activeTab, setActiveTab] = useState(userPageEventTypes[0]);
  const { data: userTickets, isLoading: ticketLoad } = useQuery({
    queryKey: ['userTickets'],
    queryFn: () => fetchUserTicketsByUID(uid),
  });
  const { data: userReservations, isLoading: resLoad } = useQuery({
    queryKey: ['userReservations'],
    queryFn: async () =>
      Promise.all(
        userTickets!.map(({ event_id }) => fetchEventDataById(event_id)),
      ),
    enabled: !!userTickets,
  });
  const { data: upcomingAndPastEvents, isLoading: areEventsLoading } = useQuery({
    queryKey: ['filterEventsByPastOrUpcoming'],
    queryFn: async () => Promise.resolve({
      // @ts-ignore
      upcoming: userReservations?.filter(event => (new Date(splitDatetimeString(event.dateandtime)[0]) - Date.now()) >= -msInADay),
      // @ts-ignore
      past: userReservations?.filter(event => (new Date(splitDatetimeString(event.dateandtime)[0]) - Date.now()) < -msInADay)
    }),
    enabled: !!userReservations,
  })

  useEffect(() => {
    if (!ticketLoad) dispatch(setTickets(userTickets!))
  }, [ticketLoad]);

  const handleEditReservation = (eventId: number) => {}
  const redirectToAfisha = () => navigate(`/?barId=${currentBarId}`)

  return (
    <div>
      {areEventsLoading && <Spinner>Загрузка...</Spinner>}
      <TabsSwitch tabs={userPageEventTypes} activeTab={activeTab} setActiveTab={setActiveTab} />

      {!areEventsLoading && userReservations && activeTab === userPageEventTypes[0] && (
        upcomingAndPastEvents!.upcoming!.map(event => (
            <EventCard
              key={event.event_id}
              data={event}
              hasInfoButton={event.event_type === 'free'}
              showActionButton
              customActionButtonText={event.event_type === 'free' ? 'Изменить бронь': 'Информация'}
              customActionButtonAction={event.event_type === 'free' ? () => {}: undefined}
              showUpperBubble
            />
        ))
      )}

      {!areEventsLoading && userReservations && activeTab === userPageEventTypes[1] && (
        upcomingAndPastEvents!.past!.map(event => (
            <EventCard
              key={event.event_id}
              data={event}
              customActionButtonText={'Мероприятие уже прошло'}
              customActionButtonAction={() => {}}
              showUpperBubble
              cardType="userPage"
            />
        ))
      )}
      
      {!areEventsLoading && userReservations && 
      (
        (activeTab === userPageEventTypes[0] && upcomingAndPastEvents!.upcoming!.length <= 0) ||
        (activeTab === userPageEventTypes[1] && upcomingAndPastEvents!.past!.length <= 0)
      ) && (
        <div className={styles.checkAfisha}>
          <p>
            {`У вас пока что нет билетов среди ${Array.from(activeTab).slice(0, -1).join('')}x событий`}
          </p>
          <Button
            text={'Посмотреть афишу'}
            type="blue"
            onClick={() => redirectToAfisha()}
          />
        </div>
      )}
    </div>
  )
}

export default ReservationList
