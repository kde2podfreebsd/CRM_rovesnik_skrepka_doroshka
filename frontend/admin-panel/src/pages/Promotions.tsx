import React, { useEffect, useState } from 'react';
import {Button, Card, Typography} from '@material-tailwind/react';
import PromotionsService from "../api/PromotionsService.ts";
import {promoCodeTypeParser} from "../shared/funcsNconsts.ts";
import {PencilIcon, TrashIcon} from "@heroicons/react/24/outline";
import ButtonWithPopover from "../components/ButtonWithPopover.tsx";
import EditPromotionModal from "./editModals/EditPromotionModal.tsx";
import CreatePromotionModal from "./createModals/CreatePromotionModal.tsx";

interface IPromotion {
    id: number;
    channel_link: string;
    promotion_text: string;
    promocode_type: 'ONE_TIME_FREE_MENU_ITEM';
    short_name: string;
    sub_chat_id: string[];
}

const Promotions = () => {
    const [promotions, setPromotions] = useState<IPromotion[]>([]);
    const [isCreating, setIsCreating] = useState(false);
    const [isEditing, setIsEditing] = useState(false);
    const [editingPromotion, setEditingPromotion] = useState<IPromotion>();

    useEffect(() => {
        (async () => {
           const res = await PromotionsService.getAll()
           setPromotions(res.data)
        })()
    }, []);

    const TABLE_HEAD = ['', "ID", "Channel Link", "Promotion Text", "Promocode Type", "Short Name", "Sub Chat ID"];

    const handleEdit = (promotion: IPromotion) => {
        setEditingPromotion(promotion);
        setIsEditing(true);
    }

    const handleDelete = async (id: number) => {
        try {
            await PromotionsService.delete(id)
            setPromotions(promotions.filter((promotion) => promotion.id !== id))
        } catch (e) {
            throw new Error(e)
        }
    }

    return (
        <>
            <div className="p-2">
                <div className='mb-2'>
                    <Button color='blue-gray' onClick={() => setIsCreating(true)}>Добавить канал</Button>
                </div>
                {promotions.length > 0 ? (
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
                            {promotions.map((promotion, index) => (

                                <tr key={index} className={`even:bg-neutral-600 odd:bg-neutral-500`}>
                                    <td className="p-4">
                                        <div className="flex gap-2">
                                            <Button color='blue-gray' onClick={() => handleEdit( promotion)}>
                                                <PencilIcon className='w-5 h-5'/>
                                            </Button>
                                            <ButtonWithPopover
                                                color='blue-gray'
                                                onClick={() => handleDelete( promotion.id)}
                                                popoverText='Вы уверены что хотите удалить подарок партнера?'
                                            >
                                                <TrashIcon className='w-5 h-5'/>
                                            </ButtonWithPopover>
                                        </div>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {promotion.id}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <a className="font-normal text-blue-200 underline"
                                           href={'https://' + promotion.channel_link} target="_blank">
                                            {promotion.channel_link}
                                        </a>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal max-w-xs truncate">
                                            {promotion.promotion_text}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {promoCodeTypeParser(promotion.promocode_type)}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {promotion.short_name}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {promotion.sub_chat_id?.join(', ')}
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
            {isEditing && <EditPromotionModal isOpen={ isEditing} handleClose={ () => setIsEditing(false)} promotion={ editingPromotion} setPromotions={ setPromotions} />}
            {isCreating && <CreatePromotionModal isOpen={ isCreating} handleClose={ () => setIsCreating(false)} setPromotions={ setPromotions} />}
        </>
    );
};

export default Promotions;
