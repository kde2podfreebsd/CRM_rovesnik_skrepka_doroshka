import {useQrCodeContext} from "../../QrReader.tsx";
import { useEffect, useState } from "react";
import axios from "axios";
import { api_url } from "../../App.tsx";
import IPromoCode from "../../ types/IPromoCode.ts";
import IUser from "../../ types/IUser.ts";
import DatePicker from "../DatePicker.tsx";
import {Select, Option} from "@material-tailwind/react"
import '../loader.css'
import BalanceInputs from "./BalanceInputs.tsx";
import {format} from "date-fns";
import GoBackToScanButton from "../../components/GoBackToScanButton.tsx";
import {dateParser, promoCodeTypeParser} from "../PromoCodeModal.tsx";

const isDev = false

const UserProfileModal = () => {

    const { qrCodeData } = useQrCodeContext();


    const [userData, setUserData] = useState<IUser | null>(null)
    const [promoCodes, setPromoCodes] = useState<IPromoCode[] | null>(null)
    const [userBalance, setUserBalance] = useState<number>(0)

    const userReqData = isDev ? '272324534' : qrCodeData

    const handlePromoCodeClick = async () => {
        try {
            const promoCodesRes = await axios.post(api_url + "/promocodes/get_user_promocodes/" + userData?.chat_id);
            setPromoCodes(promoCodesRes.data);
        } catch (error) {
            console.error("Error fetching data:", error);
        } finally {
            setIsPromoCodeClicked(true);
        }
    }

    useEffect(() => {
        ( async () => {
            if (userReqData.length <= 7) {
                try {
                    const userRes = await axios.get(api_url + "/client/get_client_by_iiko_card/" + userReqData);
                    setUserData(userRes.data);
                    setUserBalance(userRes.data.balance);
                } catch (error) {
                    console.error("Error fetching data:", error);
                }
            } else {
                try {
                    const userRes = await axios.get(api_url + "/client/" + userReqData);
                    setUserBalance(userRes.data.balance);
                    setUserData(userRes.data);
                } catch (error) {
                    console.error("Error fetching data:", error);
                }
            }
        })()   
    }, [])

    const [isPromoCodeClicked, setIsPromoCodeClicked] = useState(false);
    const [isBalanceClicked, setIsBalanceClicked] = useState(false);
    const [isAddPromoCodeClicked, setIsAddPromoCodeClicked] = useState(false);

    const [inputPCName, setInputPCName] = useState('');

      const [inputPCOptions, setInputPCOptions] = useState<string | undefined>('');
      const [inputPCOperationalInfo, setInputPCOperationalInfo] = useState('');
      const [inputPCDescription, setInputPCDescription] = useState('');
      const [inputPCEndTime, setInputPCEndTime] = useState<Date | undefined>();

      const handleAddPromoCode = async () => {
        const dataToSend = {
            client_chat_id: userData?.chat_id,
            type: inputPCOptions,
            name: inputPCName,
            operational_info: inputPCOperationalInfo,
            description: inputPCDescription,
            number: parseInt((Math.random() * 100000).toFixed(0)),
            end_time: formatDate(inputPCEndTime!),
            is_activated: false
        }
        try {
            await axios.post(api_url + "/promocodes/create", dataToSend);
            setIsAddPromoCodeClicked(false);
        } catch (error) {
            console.error("Error adding promo code:", error);
        }
      }

    if (!userData) {
        return <div className="w-full h-screen justify-center items-center flex"><div className='loader'></div></div>;
    }

    const formatDate = (date: Date) => {
        return format(date, "yyyy-MM-dd HH:mm:ss.SSS");
    };


    return (
        <div className='flex flex-col items-center justify-center gap-4 pb-8'>
            <div className="flex flex-col gap-2 justify-start w-full p-4">
                <p className="text-2xl font-bold">{userData?.username}</p>
                <p className='font-bold text-xl'>{userData?.first_name} {userData?.last_name}</p>
                <p className='font-bold text-xl'>Баланс: {userBalance}</p>
                <p className='font-bold text-xl'>Уровень лояльности: {userData?.loyalty_info[0].level}</p>
                <p className='font-bold text-xl'>Кэшбэк: {userData?.loyalty_info[0].cashback}%</p>
            </div>

            <div className='w-full flex justify-center'><div className='bg-neutral-500 h-[1px] w-4/5 opacity-45'></div></div>

            <div className="w-full">
                {
                    isPromoCodeClicked ? (
                        <div className="px-8 py-4 shadow-md rounded-md w-full flex flex-col gap-4">
                            {
                                promoCodes ? (
                                    promoCodes.map((promoCode) => (
                                        <div className="flex justify-between w-full gap-2">
                                            <div>
                                                <p className="text-lg font-bold">{promoCode.name}</p>
                                                <p className="text-md">Тип: {promoCodeTypeParser(promoCode.type)}</p>
                                                <p className='font-thin'>{promoCode.description}</p>
                                                <p className='border-separate border-b pb-2'>До {dateParser(promoCode.end_time)}</p>
                                            </div>
                                        </div>
                                    ))
                                ) : (
                                    <p>Промокодов нет</p>
                                )
                            }
                        </div>
                    ) : (
                        <button onClick={() => handlePromoCodeClick()} className='m-4 bg-blue-500 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded'>
                            Просмотреть промокоды
                        </button>
                    )

                }
            </div>
            <div className='w-full'>
                {
                    isBalanceClicked ? (
                        <BalanceInputs userBalance={userBalance} setUserBalance={setUserBalance} chat_id={userData.chat_id} setIsBalanceClicked={setIsBalanceClicked}/>
                    ) : (
                        <button onClick={() => setIsBalanceClicked(true)} className='m-4 bg-blue-500 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded'>
                            Изменить баланс
                        </button>
                    )
                }
            </div>

            <div className="w-full">
                {
                    !isAddPromoCodeClicked ? (
                        <button onClick={() => setIsAddPromoCodeClicked(true)} className='m-4 bg-blue-500 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded'>
                            Добавить промокод
                        </button>
                    ) : (
                        <div className="p-4 flex flex-col gap-4 justify-start items-start">
                            <input type="text" className='p-2' value={inputPCName}
                                   onChange={e => setInputPCName(e.target.value)} placeholder="Название промокода"/>


                            <Select className="" placeholder={undefined} onPointerEnterCapture={undefined}
                                    onPointerLeaveCapture={undefined} value={inputPCOptions}
                                    onChange={(value) => setInputPCOptions(value)}>
                                <Option value='ONE_TIME_FREE_MENU_ITEM'>Одно бесплатное блюдо</Option>
                                <Option value="DISCOUNT_ON_ACCOUNT">Скидка на счет</Option>
                                <Option value="DISCOUNT_ON_DISH">Скидка на блюдо</Option>
                                <Option value="DISCOUNT_FOR_PAID_EVENT">Скидка на оплаченное мероприятие</Option>
                                <Option value="FREE_EVENT_TICKET">Бесплатный билет на мероприятие</Option>
                                <Option value="REFILLING_BALANCE">Пополнение баланса</Option>
                                <Option value="PARTY_WITHOUT_DEPOSIT">Вечеринка без депозита</Option>
                                <Option value="GIFT_FROM_PARTNER">Подарок от партнера</Option>
                                <Option value="CUSTOM">Пользовательский</Option>
                            </Select>

                            <input type="text" className='p-2' value={inputPCOperationalInfo}
                                   onChange={e => setInputPCOperationalInfo(e.target.value)}
                                   placeholder="Информация для персонала"/>
                            <input type="text" className='p-2' value={inputPCDescription}
                                   onChange={e => setInputPCDescription(e.target.value)} placeholder="Описание"/>
                            <DatePicker setInputPCEndTime={setInputPCEndTime} inputPCEndTime={inputPCEndTime}/>
                            <div className='flex gap-4'>
                                <button className=" bg-blue-500 text-white font-bold py-2 px-4 rounded active:scale-90 transition-all"
                                        onClick={() => handleAddPromoCode()}>
                                    Добавить
                                </button>
                                <button className=" bg-red-500 text-white font-bold py-2 px-4 rounded active:scale-90 transition-all"
                                        onClick={() => setIsAddPromoCodeClicked( false)}>
                                    Отменить
                                </button>
                            </div>
                        </div>
                    )

                }
            </div>
            <GoBackToScanButton/>
        </div>
    );
};

export default UserProfileModal;
