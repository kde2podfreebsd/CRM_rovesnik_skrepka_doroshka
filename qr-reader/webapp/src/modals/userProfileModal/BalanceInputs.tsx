import React, {useState} from 'react';
import {MinusIcon, PlusIcon} from "@heroicons/react/16/solid";
import {Input} from "@material-tailwind/react";
import axios from "axios";
import {api_url} from "../../App.tsx";

interface props {
    userBalance: number;
    setUserBalance: React.Dispatch<React.SetStateAction<number>>;
    chat_id: number;
    setIsBalanceClicked: React.Dispatch<React.SetStateAction<boolean>>;
}

const BalanceInputs = ({ userBalance, setUserBalance, chat_id, setIsBalanceClicked }: props) => {
    const [balanceChangeValue, setBalanceChangeValue] = useState<number>(50)

    const handleChangeBalance = async (value: number, action: 'increase' | 'decrease') => {
        setUserBalance(userBalance + (action === 'increase' ? value : -value))
        const res = await axios.post(api_url + "/client/refill_balance", {
            chat_id: chat_id,
            amount: action === 'increase' ? value : -value
        })
        console.log(res)
    }

    return (
        <div className='flex flex-col w-full items-start justify-start gap-2 m-4'>
            <div className='flex justify-center items-center gap-8'>
                <button className='bg-blue-500 hover:bg-indigo-700 text-white font-bold rounded p-2 text-2xl flex items-start justify-center
                                active:scale-90 transition-all'
                        onClick={() => handleChangeBalance(balanceChangeValue, 'decrease')}>
                    <MinusIcon className='w-6 h-6'/>
                </button>
                <p className='font-bold text-2xl'>{userBalance}</p>
                <button className='bg-blue-500 hover:bg-indigo-700 text-white font-bold rounded p-2 text-2xl flex items-start justify-center
                                active:scale-90 transition-all'
                        onClick={() => handleChangeBalance(balanceChangeValue, 'increase')}>
                    <PlusIcon className='w-6 h-6'/>
                </button>
            </div>
            <div className='flex justify-center items-center'>
                <Input type="number" name="" id="" onPointerEnterCapture={undefined}
                       onPointerLeaveCapture={undefined} crossOrigin={undefined}
                       onChange={e => setBalanceChangeValue(parseInt(e.target.value))} value={balanceChangeValue}/>
                <button onClick={() => setIsBalanceClicked(false)}
                        className='m-4 bg-blue-500 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded transition-all active:scale-90'>
                    Готово
                </button>
            </div>
        </div>
    );
};

export default BalanceInputs;