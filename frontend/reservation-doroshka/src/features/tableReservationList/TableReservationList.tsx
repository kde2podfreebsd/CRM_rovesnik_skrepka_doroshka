import React, {useEffect, useState} from 'react'
import { useNavigate } from 'react-router-dom'

import Button from '../../shared/ui/button'
import ReservationCard from '../reservationCard'

import styles from './styles.module.scss'
import { TableData } from '../../shared/types'
import ReservationService, { IReservation } from '../../api/ReservationService'
import TablesService, { ITable } from '../../api/TablesService'
import { selectUID } from '../../entities/user/userSlice'
import { useAppSelector } from '../../app/hooks/redux'
import {userPageEventTypes} from "../../shared/constants";
import TabsSwitch from "../../shared/ui/tabsSwitch/TabsSwitch";

export interface ITableReservation {
  reservation: IReservation
  table: ITable
}

const TableReservationList = () => {
  const navigate = useNavigate()
  const [filteredReservations, setFilteredReservations] =
    React.useState<ITableReservation[]>()
  const client_chat_id = Telegram.WebApp.initDataUnsafe.user?.id ?? 272324534;
  const [activeTab, setActiveTab] = useState(userPageEventTypes[0]);
  const [expiredReservations, setExpiredReservations] = useState<ITableReservation[]>([])

  useEffect(() => {
    (async () => {
      const res = await ReservationService.getAll(client_chat_id!)
      const expRes = await ReservationService.getExpired(client_chat_id!)
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
          }
        }
        setFilteredReservations(mergedReservations)
        const groupedExpiredReservationTable: ITableReservation[] = []
        if (expRes.data.Status !== 'Failed') {
          for (const reservation of expRes.data.Message) {
            const tableRes = await TablesService.getByUuid(reservation.table_uuid)
            groupedExpiredReservationTable.push({
              reservation,
              table: tableRes.data.Message,
            })
          }
          setExpiredReservations(groupedExpiredReservationTable)
        }
      }
    })()
  }, [])

  const handleReservation = ({}: {
    onTableSelect: (table: TableData) => void
  }) => navigate('/doroshka/reservation?barId=3')

  return (
      <div>
        <TabsSwitch tabs={userPageEventTypes} activeTab={activeTab} setActiveTab={setActiveTab} />
        {activeTab === userPageEventTypes[0] ? (
            <div>
              {filteredReservations && filteredReservations.length > 0 ? (
                  filteredReservations.map((reservation, i) => (
                      <ReservationCard key={i} data={reservation} setFilteredReservations={setFilteredReservations} />
                  ))
              ) : (
                  <div className={styles.noReserveTable}>
                    <p>
                      {'Вы пока что не бронировали стол в нашем заведении, но можете сделать это прямо сейчас.'}
                    </p>
                    <Button
                        type="blue"
                        text={'Забронировать стол'}
                        onClick={handleReservation}
                    />
                  </div>
              )}
            </div>
        ) : (
            <div>
              {expiredReservations && expiredReservations.length > 0 ? (
                  expiredReservations.map((reservation, i) => (
                      <ReservationCard key={i} data={reservation} setFilteredReservations={setExpiredReservations} block={true}/>
                  ))
              ) : <p className={styles.noReserveTable}>
                {'У вас нету прошедших резерваций'}
              </p>}
            </div>
        )}
      </div>
  );

}

export default TableReservationList
