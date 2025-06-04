import React, { useState } from 'react';
import {
    Button,
    Dialog,
    DialogHeader,
    DialogBody,
    DialogFooter,
    Input,
    Select,
    Option,
} from "@material-tailwind/react";
import EventService, { IEvent } from "../../api/EventService.ts";
import ImageService from "../../api/ImageService.ts";
import DatePicker from "../../components/DatePicker.tsx";
import { barIdParser } from "../../shared/funcsNconsts.ts";
import { api_url } from "../../api";
import {formatDate} from "date-fns/format";
import NotificationsInput from "../../components/NotificationsInput.tsx";

interface CreateEventModalProps {
    isOpen: boolean;
    handleClose: () => void;
    setEvents: React.Dispatch<React.SetStateAction<IEvent[]>>;
    barId: number;
}

const CreateEventModal: React.FC<CreateEventModalProps> = ({ isOpen, handleClose, setEvents, barId }) => {
    const [formData, setFormData] = useState<IEvent>({
        short_name: '',
        description: '',
        img_path: '',
        event_datetime: '',
        end_datetime: '',
        bar_id: barId,
        place: '',
        age_restriction: 0,
        event_type: '',
        price: 0,
        notification_time: [],
    });
    const [imageFile, setImageFile] = useState<File | null>(null);
    const [startTime, setStartTime] = useState<string>('');
    const [endTime, setEndTime] = useState<string>('');
    const [startDate, setStartDate] = useState<Date | null>(null);
    const [endDate, setEndDate] = useState<Date | null>(null);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSelectChange = (value: string) => {
        setFormData({ ...formData, event_type: value });
    };

    const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setImageFile(e.target.files[0]);
        }
    };

    const handleStartTimeChange = (value: string) => {
        setStartTime(value);
    };

    const handleEndTimeChange = (value: string) => {
        setEndTime(value);
    };

    const handleSubmit = async () => {
        console.log('click')
        const startDateToSend = formatDate( startDate?.toISOString().toString(), 'yyyy-MM-dd');
        const endDateToSend = formatDate( endDate?.toISOString().toString(), 'yyyy-MM-dd');
        if (imageFile) {
            const imageData = new FormData();
            imageData.append('file', imageFile);
            const response = await ImageService.uploadImage( imageData, '/events' );
            console.log('[IMAGE]',response)
            const dataToSend = {
                ...formData,
                event_datetime: startDateToSend + ' ' + startTime + ':00.000',
                end_datetime: endDateToSend + ' ' + endTime + ':00.000',
                img_path: response.data.message,
                notification_time: formData.notification_time
            }
            await EventService.create(dataToSend);
            setEvents(prev => [...prev, dataToSend]);

        }
        handleClose();
    };

    return (
        <Dialog open={isOpen} handler={handleClose} className='bg-neutral-800 overflow-y-scroll max-h-screen h-full'>
            <DialogHeader className='text-white'>Создать ивент</DialogHeader>
            <DialogBody className='text-white flex flex-col gap-4'>
                <h1 className='font-semibold'>Бар: {barIdParser(barId)}</h1>
                <Input
                    label="Название ивента"
                    name="short_name"
                    value={formData.short_name}
                    onChange={handleInputChange}
                    color='white'
                />
                <Input
                    label="Описание"
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    color='white'
                />
                <Input
                    label="Изображение"
                    type="file"
                    name="img_path"
                    onChange={handleImageChange}
                    color='white'
                />
                <Input
                    label="Место проведения"
                    name="place"
                    value={formData.place}
                    onChange={handleInputChange}
                    color='white'
                />
                <div>
                    <Select
                        label="Тип ивента"
                        value={formData.event_type}
                        onChange={handleSelectChange}
                    >
                        <Option value="free">Бесплатный</Option>
                        <Option value="deposit">Депозитный</Option>
                        <Option value="event">Событие</Option>
                    </Select>
                </div>
                <Input
                    label="Цена"
                    name="price"
                    value={formData.price.toString()}
                    onChange={handleInputChange}
                    color='white'
                />
                <Input
                    type='number'
                    label="Ограничение по возрасту"
                    name="age_restriction"
                    value={formData.age_restriction.toString()}
                    onChange={handleInputChange}
                    color='white'
                />
                <DatePicker setInputPCEndTime={setStartDate} inputPCEndTime={startDate} text='Дата начала: '/>
                <Select
                    label="Время начала"
                    value={startTime}
                    onChange={handleStartTimeChange}
                    className='text-white'
                    dismiss={undefined}
                >
                    {[...Array(10 * 2)].map((_, i) => {
                        const hour = Math.floor(14 + i / 2);
                        const minute = (i % 2) * 30;
                        const hourString = hour.toString().padStart(2, '0');
                        const minuteString = minute.toString().padStart(2, '0');
                        return (
                            <Option key={`${hourString}:${minuteString}`} value={`${hourString}:${minuteString}`}>
                                {`${hourString}:${minuteString}`}
                            </Option>
                        );
                    })}
                </Select>
                <DatePicker setInputPCEndTime={setEndDate} inputPCEndTime={endDate} text='Дата конца: '/>
                <Select
                    label="Время окончания"
                    value={endTime}
                    onChange={handleEndTimeChange}
                    className='text-white'
                    dismiss={undefined}
                >
                    {[...Array(10 * 2)].map((_, i) => {
                        const hour = Math.floor(14 + i / 2);
                        const minute = (i % 2) * 30;
                        const hourString = hour.toString().padStart(2, '0');
                        const minuteString = minute.toString().padStart(2, '0');
                        return (
                            <Option key={`${hourString}:${minuteString}`} value={`${hourString}:${minuteString}`}>
                                {`${hourString}:${minuteString}`}
                            </Option>
                        );
                    })}
                </Select>
                <p>За сколько минут нужно уведомить пользователей:</p>
                <NotificationsInput setInputData={setFormData} inputData={formData} />
            </DialogBody>
            <DialogFooter>
                <Button variant="text" color="red" onClick={handleClose} className="mr-1">
                    Отмена
                </Button>
                <Button color="green" onClick={handleSubmit}>
                    Создать
                </Button>
            </DialogFooter>
        </Dialog>
    );
};

export default CreateEventModal;
