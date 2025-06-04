import React from 'react'
import styles from './styles.module.scss'
import descriptionStyles from './styles2.module.scss'
import { Optional, TEvent, Timestamp } from '../../shared/types'
import classNames from 'classnames'
import { arrow } from '../../shared/assets'
import { convertTimestampToDateString } from '../../shared/utils'
import { useTheme } from '../../shared/ui/themeContext/ThemeContext'

type Props = {
    data: Pick<TEvent, 'dateandtime' | 'short_name' | 'place' | 'age_restriction'>
    cardType: 'base' | 'description' | 'userPage'
    fullWidth?: boolean
    className?: string
}
const EventInfoText = ({ data, className, cardType = 'base' }: Props) => {
    const { dateandtime, short_name, place, age_restriction } = data;
    const date = dateandtime.split('T')[0] as Timestamp;

    const { theme } = useTheme();

    return (
        <div className={`p-2 flex flex-col w-full h-4/5 justify-between pb-4`}>
            <h1 className={`text-2xl w-4/5 p-2`}>{short_name}</h1>
            <div className={`flex gap-2 items-center px-2 py-1 rounded-md bg-white text-black`}>
                <p className='text-xs'>
                    {convertTimestampToDateString(date)}
                </p>
                <p className='flex items-center gap-4 text-xs justify-between'>{place}</p>
                <p className='font-bold text-xl'>{age_restriction}+</p>
            </div>
        </div>
    )
}

export default EventInfoText