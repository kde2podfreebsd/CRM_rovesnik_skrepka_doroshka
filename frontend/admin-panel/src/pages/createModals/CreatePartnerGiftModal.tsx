import React, { useState } from 'react';
import { Button, Dialog, DialogHeader, DialogBody, DialogFooter, Input } from "@material-tailwind/react";
import PartnerGiftService from "../../api/PartnerGiftService.ts";

export interface IPartnerGift {
    short_name: string;
    promotion_text: string;
}

interface Props {
    isOpen: boolean;
    handleClose: () => void;
    setPartnerGifts: React.Dispatch<React.SetStateAction<IPartnerGift[]>>;
}

const CreatePartnerGiftModal = ({ isOpen, handleClose, setPartnerGifts }: Props) => {
    const [shortName, setShortName] = useState('');
    const [promotionText, setPromotionText] = useState('');

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
            const newPartnerGift: IPartnerGift = {
                short_name: shortName,
                promotion_text: promotionText,
            };

            await PartnerGiftService.create(newPartnerGift);

            setPartnerGifts(prevGifts => [...prevGifts, newPartnerGift]);

            handleClose();
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <Dialog open={isOpen} className='bg-neutral-800'>
            <DialogHeader className='text-white'>Добавить подарок от партнера</DialogHeader>
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

export default CreatePartnerGiftModal;
