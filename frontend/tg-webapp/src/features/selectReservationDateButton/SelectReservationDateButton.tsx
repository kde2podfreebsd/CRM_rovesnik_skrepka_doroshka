import React, { useState } from "react"
import Button from "../../shared/ui/button";
import Drawer from "@mui/material/Drawer";
import { DateCalendar, LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import styles from './styles.module.scss';
import { triangle } from "../../shared/assets";

const SelectReservationDateButton = () => {
    const [isOpen, setIsOpen] = useState(false);
    const toggleDrawer = () => setIsOpen(prev => !prev);
    const selectDateRange = (val: string) => {
    }

    return (
        <div>
            <Button onClick={toggleDrawer} className={styles.timeBtn} text={<>Дата и время <img src={triangle} alt="Triangle" /></>} />
            <Drawer
                anchor='bottom'
                open={isOpen}
                onClose={toggleDrawer}
                PaperProps={{
                    style: {
                        borderRadius: isOpen ? '20px 20px 0 0' : '20px',
                    },
                }}
            >
                <LocalizationProvider dateAdapter={AdapterDayjs}>
                    <DateCalendar onChange={selectDateRange} />
                </LocalizationProvider>
            </Drawer>
        </div>
    )
};

export default SelectReservationDateButton;
