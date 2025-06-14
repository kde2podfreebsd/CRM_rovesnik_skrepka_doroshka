import React, {useEffect} from "react";
import styles from './styles.module.scss';
import { useTheme } from "../themeContext/ThemeContext";

type Props = {
    activeTab: string,
    setActiveTab: React.Dispatch<React.SetStateAction<string>>,
    tabs: string[],
}
const TabsSwitch = ({activeTab, setActiveTab, tabs}: Props) => {
    const { theme } = useTheme();
    const buttonClassName = theme === 'dark' ? styles.buttonDark : styles.buttonLight;

    useEffect(() => {
        console.log(activeTab)
    }, [ activeTab ])

    return (
        <div className={`${styles.btnTypeChange} ${buttonClassName}`}>
            {tabs.map((tabName, i) => (
                <button
                    key={tabName + i}
                    className={`${tabName === activeTab ? styles.active : ''}`}
                    onClick={() => setActiveTab(tabName)}
                >
                    {tabName}
                </button>
            ))}
        </div>
    )
};

export default TabsSwitch;
