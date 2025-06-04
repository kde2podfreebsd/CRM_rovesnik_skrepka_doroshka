import {
    barAddressMap,
    barFullNameMap,
    barIdToBarNameMap,
    footerBarToResourcesMap,
    headerBarToLogoMap
} from '../../shared/constants';
import { BarFullName, BarId, Theme } from '../../shared/types';
import { dorozhkaDarkHeaderLogo, dorozhkaLightHeaderLogo } from '../../shared/assets';
import { selectCurrentBarId } from '../../entities/bar/barSlice';
import { useAppDispatch, useAppSelector } from './redux';
import { useTheme } from '../../shared/ui/themeContext/ThemeContext';

export default function useGetBarData(searchParams: URLSearchParams):
    [barId: BarId, logoSrc: string, address: string, footerLogo: string] {
    const { theme } = useTheme();
    let barId = searchParams.get('barId') !== undefined ?
        (Number(searchParams.get('barId')) as BarId):
        useAppSelector(selectCurrentBarId);
    barId = barId ?? 1;
    const address = barAddressMap.get(barFullNameMap.get(barIdToBarNameMap.get(barId)!) ?? 'Ровесник');
    const footerLogo = footerBarToResourcesMap.get(barId);
    let logoSrc = headerBarToLogoMap.get(barId);

    if (barId === 3) {
        logoSrc = theme === 'dark' ? dorozhkaDarkHeaderLogo : dorozhkaLightHeaderLogo;
    }

    return [barId!, logoSrc!, address!, footerLogo!.logo!]
}