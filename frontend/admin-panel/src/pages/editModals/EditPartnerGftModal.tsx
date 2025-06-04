import React, { useState, useEffect } from 'react';
import { Button, Dialog, DialogHeader, DialogBody, DialogFooter, Input } from "@material-tailwind/react";
import PartnerGiftService, {IPartnerGift} from "../../api/PartnerGiftService.ts";

interface Props {
    isOpen: boolean;
    handleClose: () => void;
    partnerGift: IPartnerGift; // Текущий подарок для редактирования
    setPartnerGifts: React.Dispatch<React.SetStateAction<IPartnerGift[]>>;
}

const EditPartnerGiftModal = ({ isOpen, handleClose, partnerGift, setPartnerGifts }: Props) => {
    const [shortName, setShortName] = useState('');
    const [promotionText, setPromotionText] = useState('');

    useEffect(() => {
        if (partnerGift) {
            setShortName(partnerGift.short_name);
            setPromotionText(partnerGift.promotion_text);
        }
    }, [partnerGift]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        if (name === 'shortName') {
            setShortName(value);
        } else if (name === 'promotionText') {
            setPromotionText(value);
        }
    };

    const handleSubmit = async () => {
        try {
            const updatedPartnerGift: IPartnerGift = {
                short_name: shortName,
                promotion_text: promotionText,
                id: partnerGift.id,
            };

            await PartnerGiftService.update({
                partner_gift_id: partnerGift.id,
                short_name: shortName,
                promotion_text: promotionText,
            });

            setPartnerGifts(prevGifts =>
                prevGifts.map(gift =>
                    gift.short_name === partnerGift.short_name ? updatedPartnerGift : gift
                )
            );

            handleClose();
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <Dialog open={isOpen} className='bg-neutral-800'>
            <DialogHeader className='text-white'>Редактировать подарок от партнера</DialogHeader>
            <DialogBody className='text-white flex flex-col gap-4'>
                <Input
                    label="Краткое название"
                    name="shortName"
                    value={shortName}
                    onChange={handleInputChange}
                    color='white'
                />
                <Input
                    label="Текст промоакции"
                    name="promotionText"
                    value={promotionText}
                    onChange={handleInputChange}
                    color='white'
                />
            </DialogBody>
            <DialogFooter>
                <Button color="red" variant={'text'} onClick={handleClose}>Отмена</Button>
                <Button color="green" variant={'filled'} onClick={handleSubmit}>Сохранить</Button>
            </DialogFooter>
        </Dialog>
    );
};

export default EditPartnerGiftModal;
