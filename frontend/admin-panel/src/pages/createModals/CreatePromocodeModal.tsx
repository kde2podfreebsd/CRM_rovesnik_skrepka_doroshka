import React, { useState, useEffect, SetStateAction } from 'react';
import {
    Button,
    Dialog,
    DialogHeader,
    DialogBody,
    DialogFooter,
    Input,
    Option,
    Select,
} from "@material-tailwind/react";
import PromocodeService, { IPromocode } from "../../api/PromocodeService.ts";
import { formatDateToSend, promoCodeTypeParser, promocodeTypes, randomNum } from "../../shared/funcsNconsts.ts";
import DatePicker from "../../components/DatePicker.tsx";
import UserService from "../../api/UserService.ts";
import {InformationCircleIcon} from "@heroicons/react/24/outline";

interface props {
    isOpen: boolean
    setIsOpen: (open: boolean) => void
    setPromocodes: React.Dispatch<SetStateAction<IPromocode[]>>
    promocodes: IPromocode[]
}

const CreatePromocodeModal = ({ isOpen, setIsOpen, setPromocodes, promocodes }: props) => {
    const [newPromocode, setNewPromocode] = useState<IPromocode>({
        client_chat_id: 0,
        number: randomNum(),
        name: '',
        description: '',
        operational_info: '',
        type: 'ONE_TIME_FREE_MENU_ITEM',
        end_time: '',
        is_activated: false
    });
    const [promocodeDate, setPromocodeDate] = useState<Date | null>(null);
    const [username, setUsername] = useState('');
    const [usersList, setUsersList] = useState<{ chat_id: number, username: string }[]>([]);
    const [isSearching, setIsSearching] = useState(false);
    const [foundUsers, setFoundUsers] = useState<{ chat_id: number, username: string }[]>([]);

    const findUsers = (username: string) => {
        return usersList.filter(user => user.username.includes(username))
    }

    useEffect(() => {
        if (!isOpen) {
            setNewPromocode({
                client_chat_id: 0,
                number: randomNum(),
                name: '',
                description: '',
                operational_info: '',
                type: 'ONE_TIME_FREE_MENU_ITEM',
                end_time: '',
                is_activated: false
            });
        }
        (async () => {
            const res = await UserService.getAllUsernames()
            setUsersList(res.data.message)
        })()
    }, [isOpen]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        setNewPromocode({ ...newPromocode, [e.target.name]: e.target.value });
    };

    const handleSelectChange = (value) => {
        setNewPromocode({ ...newPromocode, type: value });
    };

    const handleSubmit = async () => {
        try {
            const updatedPromocode = {
                ...newPromocode,
                end_time: formatDateToSend(promocodeDate!),
                client_chat_id: username === '0' ? 0 : usersList.find(user => user.username === username)?.chat_id || 0
            };
            await PromocodeService.create(updatedPromocode);
            setPromocodes([...promocodes, updatedPromocode]);
            setIsOpen(false);
            console.log(updatedPromocode);
        } catch (e) {
            throw new Error(e);
        }
    };

    const handleInput = (value: string) => {
        setUsername(value);
        setIsSearching(true)
        setFoundUsers(findUsers(value))
    }


    return (
        <Dialog open={isOpen} handler={() => setIsOpen(false)} className='bg-neutral-800 overflow-y-auto h-full'>
            <DialogHeader className='text-white'>Создать промокод</DialogHeader>
            <DialogBody className='text-white flex flex-col gap-4'>
                <Input
                    label="Имя промокода"
                    name="name"
                    value={newPromocode.name}
                    onChange={handleInputChange}
                    color='white'
                />
                <Input
                    label="Описание"
                    name="description"
                    value={newPromocode.description}
                    onChange={handleInputChange}
                    color='white'
                />
                <Input
                    label="Информация для персонала"
                    name="operational_info"
                    value={newPromocode.operational_info}
                    onChange={handleInputChange}
                    color='white'
                />
                <Select
                    label="Тип промокода"
                    name="type"
                    value={newPromocode.type}
                    onChange={handleSelectChange}
                    className='text-white'
                >
                    {promocodeTypes.map((type) => (
                        <Option key={type} value={type}>{promoCodeTypeParser(type)}</Option>
                    ))}
                </Select>
                <p className='text-white flex gap-2 items-center'><InformationCircleIcon  className='w-8 h-8'/>Выберите юзера которому присвоить проокод, или впишите 0 чтобы не назначать промокод никому</p>
                <Input
                    label="Юзернейм пользователя"
                    name="username"
                    value={username}
                    onChange={e => handleInput(e.target.value)}
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
                                        setNewPromocode({ ...newPromocode, client_chat_id: user.chat_id })
                                    }}
                                >
                                    {user.username}
                                </div>
                            ))
                        ) : (
                            <p className='font-normal p-2'>Пользователь не найден</p>
                        )}
                    </div>
                )}
                <Input label='Number' name='number' value={newPromocode.number} onChange={handleInputChange} color='white' type='number'/>
                <DatePicker setInputPCEndTime={setPromocodeDate} inputPCEndTime={promocodeDate} />
            </DialogBody>
            <DialogFooter>
                <Button variant="text" color="red" onClick={() => setIsOpen(false)} className="mr-1">
                    Отмена
                </Button>
                <Button color="green" onClick={handleSubmit}>
                    Создать
                </Button>
            </DialogFooter>
        </Dialog>
    );
};

export default CreatePromocodeModal;
