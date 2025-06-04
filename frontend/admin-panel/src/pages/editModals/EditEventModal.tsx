import React, { useState, useEffect } from 'react';
import {
    Button,
    Dialog,
    DialogHeader,
    DialogBody,
    DialogFooter,
    Input,
    Select,
    Option, Avatar,
} from "@material-tailwind/react";
import EventService, { IEvent } from "../../api/EventService.ts";
import DatePicker from "../../components/DatePicker.tsx";
import {barIdParser, imageUrl} from "../../shared/funcsNconsts.ts";
import {formatDate} from "date-fns/format";
import ArtistService, {IArtist} from "../../api/Artists.ts";
import ImageService from "../../api/ImageService.ts";
import NotificationsInput from "../../components/NotificationsInput.tsx";


interface EditEventModalProps {
    isOpen: boolean;
    handleClose: () => void;
    editableEvent: IEvent;
    setEditableEvent: (event: IEvent) => void;
    setEvents: React.Dispatch<React.SetStateAction<IEvent[]>>
}

const EditEventModal: React.FC<EditEventModalProps> = ({ isOpen, handleClose, editableEvent, setEditableEvent, setEvents }) => {
    const [startDate, setStartDate] = useState<Date | null>(null);
    const [endDate, setEndDate] = useState<Date | null>(null);
    const [startTime, setStartTime] = useState<string>('');
    const [endTime, setEndTime] = useState<string>('');
    const [artists, setArtists] = useState<IArtist[]>([]);
    const [imageFile, setImageFile] = useState<File | null>(null);
    const [reletionShips, setRelationships] = useState<any[]>([]);

    useEffect(() => {
        const fetchArtists = async () => {
            try {
                const res = await EventService.getArtists(editableEvent.event_id);
                setRelationships(res.data)
                console.log(res.data)
                const artistPromises = res.data.map((artist) => ArtistService.getById(artist.artist_id));
                const artistResponses = await Promise.all(artistPromises);
                const artistData = artistResponses.map(response => response.data);
                setArtists(artistData);
            } catch (error) {
                console.error("Error fetching artists:", error);
            }
        };
        fetchArtists();
    }, [ editableEvent.event_id ]);

    useEffect(() => {
        if (editableEvent.dateandtime) {
            setStartDate(new Date(editableEvent.dateandtime));
        }
        if (editableEvent.end_datetime) {
            setEndDate(new Date(editableEvent.end_datetime));
        }
        if (editableEvent.dateandtime) {
            const eventTime = new Date(editableEvent.dateandtime);
            const hours = eventTime.getHours().toString().padStart(2, '0');
            const minutes = eventTime.getMinutes().toString().padStart(2, '0');
            setStartTime(`${hours}:${minutes}`);
        }
        if (editableEvent.end_datetime) {
            const eventEndTime = new Date(editableEvent.end_datetime);
            const hours = eventEndTime.getHours().toString().padStart(2, '0');
            const minutes = eventEndTime.getMinutes().toString().padStart(2, '0');
            setEndTime(`${hours}:${minutes}`);
        }
    }, [editableEvent.dateandtime, editableEvent.end_datetime]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        setEditableEvent({ ...editableEvent, [e.target.name]: e.target.value });
    };

    const handleStartTimeChange = (value: string) => {
        setStartTime(value);
    };

    const handleEndTimeChange = (value: string) => {
        setEndTime(value);
    };

    const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setImageFile(e.target.files[0]);
        }
    };

    useEffect(() => {
        if (editableEvent.dateandtime) {
            setStartDate(new Date(editableEvent.dateandtime));
        }
        if (editableEvent.end_datetime) {
            setEndDate(new Date(editableEvent.end_datetime));
        }
    }, [editableEvent.dateandtime, editableEvent.end_datetime]);

    const handleSubmit = async () => {
        const startDateToSend = formatDate(startDate?.toISOString().toString(), 'yyyy-MM-dd');
        const endDateToSend = formatDate(endDate?.toISOString().toString(), 'yyyy-MM-dd');

        if (imageFile) {
            const imageData = new FormData();
            imageData.append('file', imageFile);
             const response = await ImageService.uploadImage(imageData, '/events');
            const dataToSend = {
                ...editableEvent,
                dateandtime: startDateToSend + ' ' + startTime + ':00.000',
                end_datetime: endDateToSend + ' ' + endTime + ':00.000',
                img_path: response.data.message
            };
            const res = await EventService.update(dataToSend);
            console.log(res)
            setEvents(prev => [...prev, dataToSend]);
        } else {
            const dataToSend = {
                ...editableEvent,
                dateandtime: startDateToSend + ' ' + startTime + ':00.000',
                end_datetime: endDateToSend + ' ' + endTime + ':00.000',
            };
            await EventService.update(dataToSend);
        }
        window.location.reload();
        handleClose();
    };

    const handleDeleteArtist = async (artistId: number) => {
        const relationshipId = reletionShips.find((relationship) => relationship.artist_id === artistId).relationship_id;
        await ArtistService.deleteRelationship(relationshipId)
        setArtists( artists.filter((artist) => artist.artist_id !== artistId));
    };

    return (
        <Dialog open={isOpen} handler={handleClose} className='bg-neutral-800 overflow-y-scroll max-h-screen h-full'>
            <DialogHeader className='text-white'>Редактировать ивент</DialogHeader>
            <DialogBody className='text-white flex flex-col gap-4'>
                <h1 className='font-semibold'>Бар: {barIdParser(editableEvent.bar_id)}</h1>
                <Input
                    label="Название ивента"
                    name="short_name"
                    value={editableEvent.short_name}
                    onChange={handleInputChange}
                    color='white'
                />
                <Input
                    label="Описание"
                    name="description"
                    value={editableEvent.description}
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
                    value={editableEvent.place}
                    onChange={handleInputChange}
                    color='white'
                />
                <div>
                    <Select
                        label="Тип ивента"
                        name="event_type"
                        value={editableEvent.event_type}
                        onChange={handleInputChange}
                        dismiss={undefined}
                    >
                        <Option value="free">Бесплатный</Option>
                        <Option value="deposit">Депозитный</Option>
                        <Option value="event">Событие</Option>
                    </Select>
                </div>
                <Input
                    label="Цена"
                    name="price"
                    value={editableEvent.price.toString()}
                    onChange={handleInputChange}
                    color='white'
                />
                <Input
                    type='number'
                    label="Ограничение по возрасту"
                    name="age_restriction"
                    value={editableEvent.age_restriction.toString()}
                    onChange={handleInputChange}
                    color='white'
                />
                <DatePicker setInputPCEndTime={setStartDate} inputPCEndTime={startDate} label="Дата и время начала"
                            text='Дата начала: '/>
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
                <DatePicker setInputPCEndTime={setEndDate} inputPCEndTime={endDate} label="Дата и время окончания"
                            text='Дата конца: '/>
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
                <p>За сколько минут нужно уведоменить пользователей:</p>
                <NotificationsInput setInputData={setEditableEvent} inputData={editableEvent}/>
                <h1 className='font-bold text-xl text-white'>Артисты: </h1>
                <div className='flex overflow-x-auto'>
                    {artists.length > 0 ? (
                        artists.map((artist) => (
                            <div key={artist.id}
                                 className='bg-neutral-500 rounded-lg shadow-md flex flex-col gap-2 justify-center items-center w-60 px-4 py-2'>
                                <Avatar src={imageUrl + artist.img_path} alt={artist.name} className='w-24 h-24'/>
                                <p className='font-bold text-lg'>{artist.name}</p>
                                <p className=' text-sm max-w-56'>{artist.description}</p>
                                <Button color='red' onClick={() => handleDeleteArtist(artist.artist_id)}>
                                    Удалить артиста с события
                                </Button>
                            </div>
                        ))
                    ) : (
                        <p>Список пуст</p>
                    )}
                </div>
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

export default EditEventModal;
