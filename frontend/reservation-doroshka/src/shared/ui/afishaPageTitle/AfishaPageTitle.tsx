import React from "react"
import styles from './styles.module.scss';

type Props = {
    text: string,
}
const AfishaPageTitle = ({text}: Props) => {

    return (
        <div className={styles.title}>
            <p>{text} Афиша&nbsp;мероприятий</p>
        </div>
    )
};

export default AfishaPageTitle;
