import classNames from 'classnames';
import React, { FormEvent } from 'react';
import styles from './styles.module.scss';

type Props = {
    className?: string,
    text: React.ReactNode,
    type?: 'realBlue' |'blue' | 'white' | 'textRed' | 'widthBtn' | 'toBook' | 'whiteBtnToBuy' | 'checkAfisha' | 'whiteChangeReserve' | 'submitBtn' | 'submitReserve' | 'reserveTable' | 'changeReserve',
    onClick?: (e?: any) => void,
}
const Button = ({className, text, type, onClick = () => {}}: Props) => {
    const buttonClasses = classNames(className, styles.root, {
        [styles.realBlue]: type === 'realBlue',
        [styles.blue]: type === 'blue',
    });

    return (
        <div
            className={buttonClasses}
            onClick={onClick}
            onTouchStart={onClick}
        >
            {text}
        </div>
    );
};

export default Button;