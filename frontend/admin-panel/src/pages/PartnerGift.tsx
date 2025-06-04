import React, { useEffect, useState } from 'react';
import { Button, Card, Typography } from "@material-tailwind/react";
import { PencilIcon, TrashIcon, EyeIcon } from "@heroicons/react/24/outline";
import PartnerGiftService, {IPartnerGift} from "../api/PartnerGiftService.ts";
import {rowsColors} from "../shared/funcsNconsts.ts";
import UserService from "../api/UserService.ts";
import CreatePartnerGiftModal from "./createModals/CreatePartnerGiftModal.tsx";
import ButtonWithPopover from "../components/ButtonWithPopover.tsx";
import EditPartnerGiftModal from "./editModals/EditPartnerGftModal.tsx";

const PartnerGift = () => {
    const [gifts, setGifts] = useState<IPartnerGift[]>([]);
    const [isEdit, setIsEdit] = useState(false);
    const [editableGift, setEditableGift] = useState<IPartnerGift | null>(null);
    const [isCreating, setIsCreating] = useState(false);
    const [usersWithUsernames, setUsersWithUsernames] = useState<{ chat_id: number; username: string }[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const handleEdit = (id: number) => {
        setEditableGift(gifts.find((gift) => gift.id === id) || null);
        setIsEdit(true);
    }

    const handleShowGiftInfo = (id: number) => {
        setEditableGift(gifts.find((gift) => gift.id === id) || null);
        setIsGiftInfoOpen(true);
    }

    useEffect(() => {
        (async () => {
            setIsLoading(true)
            const res = await PartnerGiftService.getAll();
            if (Array.isArray(res.data.Message)) {
                setGifts(res.data.Message);
            }
            setIsLoading(false)
            const usernamesRes = await UserService.getAllUsernames()
            setUsersWithUsernames(usernamesRes.data.message)
        })();
    }, []);

    const TABLE_HEAD = ['', "Short Name", "Promotion Text", "Got Gift IDs"];

    if (isLoading) {
        return <div className='w-full min-h-screen h-full flex justify-center items-center'><div className={"loader"}></div></div>;
    }

    const handleDelete = async (id: number) => {
        try {
            await PartnerGiftService.delete(id)
            setGifts(gifts.filter((gift) => gift.id !== id))
        } catch (e) {
            throw new Error(e)
        }
    }

    return (
        <>
            <div className='p-2'>
                <div className='mb-2'>
                    <Button color='blue-gray' onClick={() => setIsCreating(true)}>Добавить подарок</Button>
                </div>
                {gifts.length > 0 ? (
                    <Card className="h-full w-full overflow-scroll">
                        <table className="w-full min-w-max table-auto text-left">
                            <thead>
                            <tr>
                                {TABLE_HEAD.map((head) => (
                                    <th key={head} className="border-b border-blue-gray-100 bg-neutral-800 p-4">
                                        <Typography
                                            variant="small"
                                            color="white"
                                            className="leading-none opacity-70 text-white font-bold text-xl"
                                        >
                                            {head}
                                        </Typography>
                                    </th>
                                ))}
                            </tr>
                            </thead>
                            <tbody>
                            {gifts && gifts.length > 0 && gifts.map((gift, index) => (
                                <tr key={index} className={`${index % 2 === 0 ? rowsColors.first : rowsColors.second}`}>
                                    <td className="p-4">
                                        <div className="flex gap-2">
                                            <Button color='blue-gray' onClick={() => handleEdit(gift.id)}>
                                                <PencilIcon className='w-5 h-5'/>
                                            </Button>
                                            <ButtonWithPopover
                                                color='blue-gray'
                                                onClick={() =>  handleDelete(gift.id)}
                                                popoverText='Вы уверены что хотите удалить подарок партнера?'
                                            >
                                                <TrashIcon className='w-5 h-5'/>
                                            </ButtonWithPopover>
                                        </div>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {gift.short_name}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {gift.promotion_text}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography
                                            className="text-blue-200 underline flex gap-2 flex-wrap max-w-80 font-normal">
                                            {usersWithUsernames.filter(user => gift.got_gift?.includes(user.chat_id)).map(user => user.username).map((username, index) =>
                                                <a key={index} href={`https://t.me/${username}`}
                                                   target='_blank'>@{username},</a>)}
                                        </Typography>
                                    </td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                    </Card>
                ) : (
                    <p className={'text-white font-normal text-xl'}>Пусто</p>
                )}
            </div>
            {isCreating && <CreatePartnerGiftModal handleClose={() => setIsCreating(false)} setPartnerGifts={setGifts}
                                                   isOpen={isCreating}/>}
            {isEdit && <EditPartnerGiftModal isOpen={isEdit} handleClose={ () => setIsEdit(false)} partnerGift={ editableGift} setPartnerGifts={ setGifts}    />}
        </>
    );
};

export default PartnerGift;
