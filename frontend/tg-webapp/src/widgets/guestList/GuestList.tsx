import React, { useContext, useState } from "react"
import { plusSignIconDark, plusSignIconLight } from "../../shared/assets";
import { GuestInviteForm } from "../../shared/types";
import { maxEventGuestCount } from "../../shared/constants";
import GuestForm from "../../shared/ui/guestForm";
import styles from './styles.module.scss';
import { useTheme } from "../../shared/ui/themeContext/ThemeContext";

type Props = {
    guestList: GuestInviteForm[],
    setGuestList: React.Dispatch<React.SetStateAction<GuestInviteForm[]>>,
    pagetype?: 'userPage' | 'default'
}
const GuestList = ({ guestList, setGuestList, pagetype }: Props) => {
    const addGuest = () => setGuestList(prev => {
        let newObj = structuredClone(prev);
        if (newObj.length < maxEventGuestCount) newObj.push({ name: '', username: '' });
        return newObj;
    });

    const { theme } = useTheme();
    const plusIcon = theme === 'dark' ? plusSignIconDark : plusSignIconLight;

    return (
        <div className={styles.root}>
            <div className={styles.main}>
                {guestList.map((_, i) => (
                    <GuestForm key={i} id={i} guestList={guestList} setGuestList={setGuestList} pageType={pagetype}/>
                ))}
            </div>
            <button onClick={() => addGuest()}>
                <img src={plusIcon} />
                <p>Добавить гостя</p>
            </button>
        </div>
    )
};

export default GuestList;
