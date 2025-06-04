import React, { useState } from 'react';
import { Button, Dialog, DialogHeader, DialogBody, DialogFooter, Input, Option, Select } from "@material-tailwind/react";
import PromotionsService, { IPromotion } from "../../api/PromotionsService";
import { promoCodeTypeParser, promocodeTypes } from "../../shared/funcsNconsts.ts";

interface Props {
    isOpen: boolean;
    handleClose: () => void;
    setPromotions: React.Dispatch<React.SetStateAction<IPromotion[]>>;
}

const CreatePromotionModal = ({ isOpen, handleClose, setPromotions }: Props) => {
    const [channelLink, setChannelLink] = useState('');
    const [shortName, setShortName] = useState('');
    const [promotionText, setPromotionText] = useState('');
    const [promocodeType, setPromocodeType] = useState('');

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement> | React.ChangeEvent<HTMLSelectElement>) => {
        const { name, value } = e.target;
        switch (name) {
            case 'channelLink':
                setChannelLink(value);
                break;
            case 'shortName':
                setShortName(value);
                break;
            case 'promotionText':
                setPromotionText(value);
                break;
            case 'promocodeType':
                setPromocodeType(value);
                break;
            default:
                break;
        }
    };

    const handleSelectChange = (value: string) => {
        setPromocodeType(value);
    };

    const handleSubmit = async () => {
        try {
            const newPromotion: IPromotion = {
                channel_link: channelLink,
                short_name: shortName,
                promotion_text: promotionText,
                promocode_type: promocodeType,
            };

            await PromotionsService.create(newPromotion); // Создаем новую акцию

            setPromotions((prevPromotions) => [...prevPromotions, newPromotion]);

            handleClose();
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <Dialog open={isOpen} className='bg-neutral-800'>
            <DialogHeader className='text-white'>Добавить акцию</DialogHeader>
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

export default CreatePromotionModal;
