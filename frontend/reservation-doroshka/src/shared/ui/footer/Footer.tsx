import React from 'react';
import styles from './styles.module.scss';
import { footerBarToResourcesMap, logoSizes } from '../../constants';
import { Link, useSearchParams } from 'react-router-dom';
import useGetBarData from '../../../app/hooks/useGetBarData';

const Footer = () => {
    const [searchParams] = useSearchParams();
    const [barId, logoSrc, address, footerLogo] = useGetBarData(searchParams);

    const resources = footerBarToResourcesMap.get(barId);
    const backgroundStyle = { backgroundColor: resources?.background };
    
    const { logoWidth, logoHeight } = logoSizes[barId];

    return (
        <div className={`${styles.root}`} style={backgroundStyle}>
            <div className={styles.container}>
                <div className={styles.footerLogo}>
                    <img src={footerLogo} alt='afishaFooter' width={logoWidth} height={logoHeight} />
                </div>
                <div className={styles.footerNav}>
                    <div className={styles.footerText}>
                        <Link to={'https://t.me/crm_head_test_bot'}>
                            <p>Головной тг-бот</p>
                        </Link>
                        <p>{address}</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Footer;