import React, { useState, useEffect } from 'react';
import { Button, Dialog, DialogHeader, DialogBody, DialogFooter, Input, Option, Select } from "@material-tailwind/react";
import PromotionsService, { IPromotion } from "../../api/PromotionsService";
import { promoCodeTypeParser, promocodeTypes } from "../../shared/funcsNconsts.ts";

interface Props {
    isOpen: boolean;
    handleClose: () => void;
    promotion: IPromotion; // Текущая акция для редактирования
    setPromotions: React.Dispatch<React.SetStateAction<IPromotion[]>>;
}

const EditPromotionModal = ({ isOpen, handleClose, promotion, setPromotions }: Props) => {
    const [channelLink, setChannelLink] = useState('');
    const [shortName, setShortName] = useState('');
    const [promotionText, setPromotionText] = useState('');
    const [promocodeType, setPromocodeType] = useState('');

    useEffect(() => {
        if (promotion) {
            setChannelLink(promotion.channel_link);
            setShortName(promotion.short_name);
            setPromotionText(promotion.promotion_text);
            setPromocodeType(promotion.promocode_type);
        }
    }, [promotion]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement> | React.ChangeEvent<HTMLSelectElement>) => {
        const { name, value } = e.target;
        if (name === 'channelLink') {
            setChannelLink(value);
        } else if (name === 'shortName') {
            setShortName(value);
        } else if (name === 'promotionText') {
            setPromotionText(value);
        } else if (name === 'promocodeType') {
            setPromocodeType(value);
        }
    };


    const handleSelectChange = (value) => {
        setPromocodeType(value);
    };

    const handleSubmit = async () => {
        try {
            const updatedPromotion: IPromotion = {
                ...promotion,
                channel_link: channelLink,
                short_name: shortName,
                promotion_text: promotionText,
                promocode_type: promocodeType,
            };

            await PromotionsService.update(updatedPromotion); // Обновляем акцию

            setPromotions(prevPromotions =>
                prevPromotions.map(p =>
                    p.short_name === promotion.short_name ? updatedPromotion : p
                )
            );

            handleClose();
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <Dialog open={isOpen} className='bg-neutral-800'>
            <DialogHeader className='text-white'>Редактировать акцию</DialogHeader>
            <DialogBody className='text-white flex flex-col gap-4'>
                <Input
                    label="Ссылка на канал"
                    name="channelLink"
                    value={channelLink}
                    onChange={handleInputChange}
                    color='white'
                />
                <Input
                    label="Короткое название"
                    name="shortName"
                    value={shortName}
                    onChange={handleInputChange}
                    color='white'
                />
                <Input
                    label="Текст акции"
                    name="promotionText"
                    value={promotionText}
                    onChange={handleInputChange}
                    color='white'
                />
                <Select
                    label="Тип промокода"
                    name="promocodeType"
                    value={promocodeType}
                    onChange={handleSelectChange}
                    className='text-white'
                >
                    {Object.values(promocodeTypes).map((type) => (
                        <Option key={type} value={type}>{promoCodeTypeParser(type)}</Option>
                    ))}
                </Select>
            </DialogBody>
            <DialogFooter>
                <Button color="red" variant={'text'} onClick={handleClose}>Отмена</Button>
                <Button color="green" variant={'filled'} onClick={handleSubmit}>Сохранить</Button>
            </DialogFooter>
        </Dialog>
    );
};

export default EditPromotionModal;
