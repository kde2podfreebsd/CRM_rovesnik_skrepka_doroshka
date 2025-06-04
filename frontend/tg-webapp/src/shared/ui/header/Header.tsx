import React, { memo } from 'react';
import styles from './styles.module.scss';
import { userPic } from '../../assets/';
import { Link, useSearchParams } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../../../app/hooks/redux';
import { barIdToBarNameMap, headerBarToLogoMap } from '../../constants';
import { selectCurrentBarId, setCurrentBar, setCurrentBarId } from '../../../entities/bar/barSlice';
import { useTheme } from '../../ui/themeContext/ThemeContext';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';
import { dorozhkaDarkHeaderLogo, dorozhkaLightHeaderLogo } from '../../assets/';
import { BarId } from '../../types';
import { setBarFilter } from '../../../entities/event/eventSlice';
import useGetBarData from '../../../app/hooks/useGetBarData';

type Props = {
    type?: 'afisha' | 'reservations'
}

const Header = ({ type = 'afisha' }: Props) => {
    const { theme, toggleTheme } = useTheme();
    const rootClassName = theme === 'dark' ? styles.darkRoot : styles.lightRoot;
    const [searchParams] = useSearchParams();
    const [barId, logoSrc] = useGetBarData(searchParams);

    const dispatch = useAppDispatch();
    dispatch(setCurrentBarId(barId));
    dispatch(setCurrentBar(barIdToBarNameMap.get(barId) || 'rovesnik'));
    dispatch(setBarFilter(barId));

    return (
        <div className={`${styles.root} ${rootClassName}`}>
            <div className={styles.container}>
                <div className={styles.headerLogo}>
                    <Link to={type === 'afisha' ? `/rovesnik/?barId=${barId}` : `/rovesnik/reservation?barId=${barId}`}>
                        <img src={logoSrc} alt='barLogo' />
                    </Link>
                </div>
                <div className={styles.headerNav}>
                    <button onClick={toggleTheme}>
                        {theme === 'light' ? <DarkModeIcon /> : <LightModeIcon />}
                    </button>
                    <Link to={type === 'afisha' ? `/rovesnik/my/events?barId=${barId}` : `/rovesnik/my/reservations?barId=${barId}`}>
                        <img src={userPic} alt='userPic' />
                    </Link>
                </div>
            </div>

        </div>
    );
}

export default Header;