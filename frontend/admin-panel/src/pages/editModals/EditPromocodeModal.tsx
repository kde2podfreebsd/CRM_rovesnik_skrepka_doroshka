import React, {useEffect, useState} from 'react';
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
import PromocodeService, { IPromocode, PromocodeType } from "../../api/PromocodeService.ts";
import { promoCodeTypeParser } from "../../shared/funcsNconsts.ts";
import DatePicker from "../../components/DatePicker.tsx";

interface props {
    isOpen: boolean
    handleClose: () => void
    editablePromocode: IPromocode
    setEditablePromocode: (promocode: IPromocode) => void
}

const promocodeTypes: PromocodeType[] = [
    'ONE_TIME_FREE_MENU_ITEM',
    'DISCOUNT_ON_ACCOUNT',
    'DISCOUNT_ON_DISH',
    'DISCOUNT_FOR_PAID_EVENT',
    'FREE_EVENT_TICKET',
    'REFILLING_BALANCE',
    'PARTY_WITHOUT_DEPOSIT',
    'GIFT_FROM_PARTNER',
    'CUSTOM'
];

const EditPromocodeModal = ({ isOpen, handleClose, editablePromocode, setEditablePromocode }: props) => {
    const [promocodeDate, setPromocodeDate] = useState<Date | null>(null);

    useEffect(() => {
        if (editablePromocode.end_time) {
            setPromocodeDate(new Date(editablePromocode.end_time));
        }
    }, [editablePromocode.end_time]);

    const handleInputChange = (e) => {
        setEditablePromocode({ ...editablePromocode, [e.target.name]: e.target.value });
    };

    const handleSubmit = async () => {
        await PromocodeService.update( {...editablePromocode});
        console.log(editablePromocode);
        handleClose();
    };

    const handleCancelPromocode = async () => {
        try {
            await PromocodeService.delete( editablePromocode.number);
        } catch (e) {
            throw new Error(e)
        }
        setEditablePromocode({ ...editablePromocode, client_chat_id: 0 });
    };

    return (
        <Dialog open={isOpen} handler={handleClose} className='bg-neutral-800'>
            <DialogHeader className='text-white'>Редактировать промокод</DialogHeader>
            <DialogBody className='text-white flex flex-col gap-4'>
                <div className='flex gap-2 items-center'>
                    <p>Client Id: {editablePromocode.client_chat_id}</p>
                    <Button onClick={handleCancelPromocode} color={'red'} variant='text'>Забрать</Button>
                </div>
                <Input
                    label="Имя промокода"
                    name="name"
                    value={editablePromocode.name}
                    onChange={handleInputChange}
                    color='white'
                />
                <Input
                    label="Описание"
                    name="description"
                    value={editablePromocode.description}
                    onChange={handleInputChange}
                    color='white'

                />
                <Input
                    label="Информация для персонала"
                    name="operational_info"
                    value={editablePromocode.operational_info}
                    onChange={handleInputChange}
                    color='white'

                />
                <Select
                    label="Тип промокода"
                    name="type"
                    value={editablePromocode.type}
                    onChange={handleInputChange}
                    className='text-white'
                >
                    {Object.values(promocodeTypes).map((type) => (
                        <Option key={type} value={type}>{promoCodeTypeParser(type)}</Option>
                    ))}
                </Select>
                {promocodeDate && <DatePicker setInputPCEndTime={setPromocodeDate} inputPCEndTime={promocodeDate} text='Дата: '/>}
            </DialogBody>
            <DialogFooter>
                <Button variant="text" color="red" onClick={handleClose} className="mr-1">
                    Отмена
                </Button>
                <Button color="green" onClick={handleSubmit}>
                    Сохранить
                </Button>
            </DialogFooter>
        </Dialog>
    );
};

export default EditPromocodeModal;
