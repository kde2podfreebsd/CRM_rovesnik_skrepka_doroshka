import React from "react";
import { crossSignIconDark, crossSignIconLight } from "../../assets";
import { GuestInviteForm } from "../../types";
import styles from './styles.module.scss';
import { useTheme } from "../themeContext/ThemeContext";

type Props = {
    id: number,
    setGuestList: React.Dispatch<React.SetStateAction<GuestInviteForm[]>>,
    guestList: GuestInviteForm[],
};

const GuestForm = ({ id, guestList, setGuestList }: Props) => {
    const removeGuest = () => {
        setGuestList(prev => {
            let newObj = structuredClone(prev);
            newObj.splice(id, 1);
            return newObj;
        });
    };

    const handleChange = (trigger: 'name' | 'username', value: string) => {
        setGuestList(prev => {
            let newObj = structuredClone(prev);
            if (trigger === 'username') {
                newObj[id][trigger] = value.startsWith('@') ? value.slice(1) : value;
            } else {
                newObj[id][trigger] = value;
            }
            return newObj;
        });
    };

    const { theme } = useTheme();
    const crossIcon = theme === 'dark' ? crossSignIconDark : crossSignIconLight;
    const inputThemeClass = theme === 'dark' ? styles.inputDark : styles.inputLight;

    return (
        <div className='flex flex-col gap-2 justify-start w-full'>
            <div className={styles.guestInfo}>
                <h3 className='font-bold'>Гость №{id + 1}</h3>
                <button onClick={removeGuest} className={'w-6 h-6'}>
                    <img src={crossIcon} alt="Удалить гостя" />
                </button>
            </div>
            <div className='flex flex-col gap-2'>
                <input
                    className={`rounded-full ${theme === 'dark' ? 'bg-neutral-700 text-white' : 'bg-neutral-200 text-black'} ${inputThemeClass}`}
                    type="text"
                    value={guestList[id].name ?? ''}
                    placeholder='Имя фамилия'
                    onChange={e => handleChange('name', e.target.value)}
                />
                <input
                    type="text"
                    className={`rounded-full ${theme === 'dark' ? 'bg-neutral-700 text-white' : 'bg-neutral-200 text-black'} ${inputThemeClass}`}
                    value={'@' + guestList[id].username}
                    onChange={e => handleChange('username', e.target.value.slice(0, 32))}
                />
            </div>
        </div>
    );
};

export default GuestForm;
