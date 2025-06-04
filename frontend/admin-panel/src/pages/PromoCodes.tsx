import React, { useEffect, useState } from 'react';
import PromocodeService, { IPromocode } from "../api/PromocodeService.ts";
import {Button, Card, Dialog, Typography} from "@material-tailwind/react";
import {bgAdd, formatDate, promoCodeTypeParser, rowsColors} from "../shared/funcsNconsts.ts";
import './loader/loader.css'
import {PencilIcon, TrashIcon} from "@heroicons/react/24/outline";
import ButtonWithPopover from "../components/ButtonWithPopover.tsx";
import EditPromocodeModal from "./editModals/EditPromocodeModal.tsx";
import CreatePromocodeModal from "./createModals/CreatePromocodeModal.tsx";

const PromoCodes = () => {
    const [promoCodes, setPromoCodes] = useState<IPromocode[]>([]);
    const [isEditing, setIsEditing] = useState(false)
    const [editablePromocode, setEditablePromocode] = useState<IPromocode>()
    const [isCreate, setIsCreate] = useState(false)
    const [usernames, setUsernames] = useState<string[]>([])
    const [isLoading, setIsLoading] = useState(false)

    useEffect(() => {
        (async () => {
            setIsLoading(true)
            const res = await PromocodeService.getAll()
            setPromoCodes(res.data)
            setIsLoading(false)
            console.log(res.data)
        })()
    }, []);

    const TABLE_HEAD = ["", "ID пользователя", "Тип", "Имя", "Информация для персонала", "Описание", "Действителен до"];

    const handleActivatePromocode = async (number: number) => {
        await PromocodeService.activate(number)
        setPromoCodes( promoCodes.map((promoCode) => {
            if (promoCode.number === number) {
                return {
                    ...promoCode,
                    is_activated: true
                }
            }
            return promoCode
        }))
    }

    const handleEditPromocode = (number: number) => {
        setEditablePromocode([])
        setEditablePromocode( promoCodes.find((promoCode) => promoCode.number === number))
        setIsEditing(true)
        console.log('clicked', number)
    }

    const handleDeletePromocode = async (number: number) => {
        try {
            await PromocodeService.delete(number)
            setPromoCodes( promoCodes.filter((promoCode) => promoCode.number !== number))
        } catch (e) {
            throw new Error(e)
        }
    }

    if (isLoading) {
        return <div className="w-full h-screen justify-center items-center flex"><div className='loader'></div></div>
    }

    return (
        <>
            <div className='p-2'>
                <div className='mb-2'>
                    <Button color='blue-gray' onClick={() => setIsCreate(true)}>Добавить промокод</Button>
                </div>
                {promoCodes.length > 0 ? (
                    <Card className="h-full w-full overflow-scroll">
                        <table className="w-full min-w-max table-auto text-left">
                            <thead>
                            <tr>
                                {TABLE_HEAD.map((head) => (
                                    <th key={head} className="border-b border-blue-gray-100 bg-neutral-700 p-4">
                                        <Typography
                                            variant="small"
                                            color="blue-gray"
                                            className="leading-none opacity-70 text-white font-bold text-xl"
                                        >
                                            {head}
                                        </Typography>
                                    </th>
                                ))}
                            </tr>
                            </thead>
                            <tbody>
                            {promoCodes.map((promoCode, index) => (
                                <tr key={index} className={`${index % 2 === 0 ? rowsColors.first : rowsColors.second}`}>
                                    <td className="p-4">
                                        <div className="flex gap-2">
                                            <Button color='blue-gray' onClick={() => handleEditPromocode(promoCode.number)}><PencilIcon
                                                className=' w-5 h-5'/></Button>
                                            <ButtonWithPopover
                                                color='blue-gray'
                                                onClick={() => handleDeletePromocode(promoCode.number)}
                                                popoverText='Вы уверены что хотите удалить промокод?'
                                            >
                                                <TrashIcon className='w-5 h-5'/>
                                            </ButtonWithPopover>
                                            <Typography variant="small" color="white"
                                                        className="flex items-center font-normal gap-2">
                                                <Button onClick={() => handleActivatePromocode(promoCode.number)} disabled={ promoCode.is_activated} color={ promoCode.is_activated ? 'red' : 'green'}>{promoCode.is_activated ? 'Активирован' : 'Активировать'}</Button>
                                            </Typography>
                                        </div>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {promoCode.client_chat_id}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {promoCodeTypeParser((promoCode.type))}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {promoCode.name}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {promoCode.operational_info}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {promoCode.description}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {formatDate(promoCode.end_time)}
                                        </Typography>
                                    </td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                    </Card>
                ) : (
                    <p className='text-white text-xl font-normal'>Пусто</p>
                )}
            </div>
            {editablePromocode &&
                <EditPromocodeModal
                    isOpen={isEditing}
                    handleClose={() => setIsEditing(false)}
                    editablePromocode={editablePromocode}
                    setEditablePromocode={setEditablePromocode}
                />
            }
            {isCreate && <CreatePromocodeModal isOpen={isCreate} promocodes={promoCodes} setPromocodes={setPromoCodes} setIsOpen={setIsCreate}/>}
        </>
    );
};

export default PromoCodes;
