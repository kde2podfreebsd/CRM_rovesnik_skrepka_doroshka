import React, { useRef, useState } from "react"
import SortByButton from "../sortByButton";
import styles from './styles.module.scss';
import { useAppDispatch } from "../../app/hooks/redux";
import { filterBySearchResult } from "../../entities/event/eventSlice";
import useDebounce from "../../app/hooks/useDebounce";
import { useTheme } from "../../shared/ui/themeContext/ThemeContext";

const EventSearchField = () => {
    const dispatch = useAppDispatch();
    const [isInputFocused, setIsInputFocused] = useState(false);
    const [inputValue, setInputValue] = useState('');
    const handleChange: React.ChangeEventHandler<HTMLInputElement> = (e) => setInputValue(e.target.value);
    useDebounce(() => {
        dispatch(filterBySearchResult(inputValue.toLowerCase()));
    }, [inputValue], 300);

    const { theme } = useTheme(); 
    const themeClass = theme === 'dark' ? styles.dark : styles.light;

    return (
        <div className={styles.root}>
            <input
                onFocus={() => setIsInputFocused(true)}
                onBlur={() => setIsInputFocused(false)}
                onChange={handleChange}
                type="text"
                className={`${styles.searchInput} ${themeClass}`}
                placeholder="Поиск событий"
            />
            <SortByButton isInputFocused={isInputFocused} iconType={isInputFocused ? 'searchIcon': 'showFiltersIcon'} />
        </div>
       
    )
};

export default EventSearchField;
