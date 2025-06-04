import {Button, Dialog, DialogBody, DialogFooter, DialogHeader, Input} from "@material-tailwind/react";
import MailingService, {IMailing} from "../../api/MailingService.ts";
import {useEffect, useState} from "react";
import UserService from "../../api/UserService.ts";

interface props {
    isOpen: boolean;
    handleClose: () => void;
    mailing: IMailing;
}

const SendMaling = ({ isOpen, handleClose, mailing }: props) => {
    const [username, setUsername] = useState('');
    const [usersList, setUsersList] = useState<{chat_id: number, username: string}[]>([]);
    const [isSearching, setIsSearching] = useState(false);
    const [foundUsers, setFoundUsers] = useState<{chat_id: number, username: string}[]>([]);
    const [isSending, setIsSending] = useState(false);

    const findUsers = (username: string) => {
       return usersList.filter(user => user.username.includes(username))
    }

    useEffect(() => {
        (async () => {
           const res = await UserService.getAllUsernames()
           setUsersList(res.data.message)
            console.log(res.data)
        })()
    }, []);

    const handleSubmit = async () => {
        if (username) {
            await MailingService.sendMailingToUser(parseInt(usersList.find(user => user.username === username)?.chat_id, 10), mailing.mailing_name)
        }
    }

    const handleInput = (value: string) => {
        setUsername(value);
        setIsSearching(true)
        setFoundUsers(findUsers(value))
        console.log(findUsers(value))
    }

    const handleSendBeta = async () => {
        setIsSending( true)
        await MailingService.launchBeta(mailing.mailing_name)
        setIsSending(false)
        handleClose()
    }

    const handleSendAlpha = async () => {
        setIsSending( true)
        await MailingService.launchAlpha(mailing.mailing_name)
        setIsSending(false)
        handleClose()
    }

    return (
        <Dialog open={isOpen} className='bg-neutral-800' handler={ handleClose}>
            <DialogHeader className='text-white'>Отправить рассылку пользователю</DialogHeader>
            <DialogBody className='text-white flex flex-col gap-4'>
                <div className='w-full'>
                    <Input
                        label="Юзернейм пользователя"
                        name="firstName"
                        value={username}
                        onChange={e => handleInput(e.target.value)}
                        // onBlur={() => setIsSearching(false)}
                        color='white'
                        className={`${isSearching ? '!rounded-b-none' : ''}`}
                    />
                    {isSearching && username.length > 0 && (
                        <div className='bg-neutral-600 h-28 rounded-b-lg w-full overflow-y-auto'>
                            {foundUsers.length > 0 ? (
                                foundUsers.map(user => (
                                    <div
                                        key={user.chat_id}
                                        className='cursor-pointer hover:bg-neutral-500 p-2 transition-all'
                                        onClick={() => {
                                            setUsername(user.username)
                                            setIsSearching(false)
                                        }}
                                    >
                                        {user.username}
                                    </div>
                                ))
                            ) : (
                                <p className='font-normal p-2'>Пользователь не найден</p>
                            )}
                        </div>
                    )}
                </div>
                <h1 className='text-xl text-white font-bold'>Отправить рассылку на группу</h1>
                <div className='w-full flex gap-2'>
                    <Button color='blue-gray' onClick={handleSendAlpha}>
                        Отправить по альфе
                    </Button>
                    <Button color='blue-gray' onClick={handleSendBeta}>
                        Отправить по бете
                    </Button>
                </div>
                {isSending && (
                    <div>
                        <div className='animate-spin rounded-full h-10 w-10 border-b-2 border-white'></div>
                        <p className='animate-pulse'>Отправка...</p>
                    </div>
                )}
            </DialogBody>
            <DialogFooter>
                <Button color="red" variant={'text'} onClick={handleClose}>Отмена</Button>
                <Button color="green" variant={'filled'} onClick={handleSubmit}>Отправить</Button>
            </DialogFooter>
        </Dialog>
    );
};

export default SendMaling;