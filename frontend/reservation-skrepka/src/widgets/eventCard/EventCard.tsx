import React, { useEffect, useState } from 'react';
import styles from './styles.module.scss';
import descriptionStyles from './styles2.module.scss';
import { TEvent } from '../../shared/types';
import Button from '../../shared/ui/button';
import EventInfoText from '../eventInfoText';
import classNames from 'classnames';
import { Drawer } from '@mui/material';
const EventDetailsPage = React.lazy(() => import('../../pages/eventDetailsPage'));
import EventQr from '../eventQr';
import { splitDatetimeString } from '../../shared/utils';
import { useQuery } from '@tanstack/react-query';
import { uploadImage } from '../../entities/event/api';

type Props = {
  data: TEvent
  hasInfoButton?: boolean
  showUpperBubble: boolean
  customUpperBubbleText?: string
  customActionButtonText?: string
  customActionButtonAction?: (
      e?: React.MouseEvent<HTMLDivElement, MouseEvent>,
  ) => void
  showActionButton?: boolean
  cardType: 'base' | 'description' | 'userPage'
  purchasedTickets?: number[]
}

const EventCard = ({
                     data,
                     showUpperBubble,
                     customUpperBubbleText,
                     showActionButton,
                     customActionButtonAction,
                     customActionButtonText,
                     cardType = 'base',
                     hasInfoButton = false,
                   }: Props) => {
  const [isQrModalOpen, setIsQrModalOpen] = useState(false);
  const [isEventModalOpen, setIsEventModalOpen] = useState(false);
  const [purchaseType, setPurchaseType] = useState('');
  const [isLoadingEventDetails, setIsLoadingEventDetails] = useState(false);

  const toggleEventModal = (value: boolean) => {
    setIsEventModalOpen(value);
    if (!value) setPurchaseType('');
  }

  let { dateandtime, short_name, place, event_id, age_restriction, img_path, event_type } = data;
  const buyTickets = () => {
    if (event_type === 'event' || event_type === 'deposit') {
        setIsQrModalOpen(true)
    } else {
        setIsQrModalOpen(true);
        toggleEventModal(true);
    }
  };

  const { data: imgData, isLoading: isImgDataLoading } = useQuery({
    queryKey: [`imgData-${event_id}`, img_path],
    queryFn: () => uploadImage(img_path),
    staleTime: 120000,
    refetchOnMount: false,
  });

  place = place.split('/')[0];
  const time = `с ${splitDatetimeString(dateandtime)[1]}`;

  return (
      <>
          <div
              className={`${classNames(
                  cardType === 'description' ? descriptionStyles.root : styles.root,
              )} h-full`}
              style={isImgDataLoading ?
                  {backgroundImage: `url()`} :
                  {backgroundImage: `url(${imgData && URL.createObjectURL(imgData)})`}
              }
          >
              {showUpperBubble && (
                  <div
                      className={cardType === 'description' ? `${descriptionStyles.rootTime} -p-2` : styles.rootTime}
                  >
                      {customUpperBubbleText ?? time}
                  </div>
              )}
              <EventInfoText data={{dateandtime, short_name, place, age_restriction}} cardType={cardType}/>
              {!!showActionButton && !hasInfoButton && (
                  <Button
                      className={cardType === 'description' ? descriptionStyles.buttonBuy : styles.buttonBuy}
                      text={customActionButtonText ?? 'Купить билет'}
                      type="realBlue"
                      onClick={() => {
                          if (cardType === 'userPage') {
                              setIsQrModalOpen(true);
                          } else {
                              setIsEventModalOpen(true);
                          }
                      }}
                  />
              )}
              {!!showActionButton && hasInfoButton && (
                  <div className={styles.multiButtonContainer}>
                      <Button
                          className={cardType === 'description' ? descriptionStyles.buttonBuy : styles.buttonBuy}
                          text={'Информация'}
                          type="realBlue"
                          onClick={() => {
                              setIsQrModalOpen(true)
                          }}
                      />
                      <Button
                          className={cardType === 'description' ? descriptionStyles.buttonBuy : styles.buttonBuy}
                          text={customActionButtonText ?? 'Купить билет'}
                          type="realBlue"
                          onClick={() => {
                              if (cardType === 'description') {
                                  setIsQrModalOpen(true);
                                  console.log('click description')
                              } else {
                                  setIsEventModalOpen(true);
                              }
                          }}
                      />
                  </div>
              )}

              {cardType === 'userPage' && (
                  <EventQr
                      eventId={event_id}
                      isModalOpen={isQrModalOpen}
                      setIsModalOpen={setIsQrModalOpen}
                  />
              )}
          </div>

          {cardType !== 'description' && (
              <div className={'w-10/12 h-4/5'}>
                  {isEventModalOpen && (
                      <React.Suspense fallback={<div>{null}</div>}>
                          <EventDetailsPage
                              eventId={event_id}
                              pageType={cardType === 'userPage' ? cardType : 'default'}
                        purchaseType={purchaseType}
                        setPurchaseType={setPurchaseType}
                        isEventModalOpen={isEventModalOpen}
                        setIsEventModalOpen={setIsEventModalOpen}
                        onLoadStart={() => setIsLoadingEventDetails(true)}
                        onLoad={() => setIsLoadingEventDetails(false)}
                    />
                  </React.Suspense>
              )}
            </div>
        )}
      </>
  )
}

export default EventCard;
