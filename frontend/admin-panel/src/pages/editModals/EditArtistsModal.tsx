import React, { useEffect, useState } from 'react';
import {Button, Dialog, DialogHeader, DialogBody, DialogFooter, Input, Select, Option} from "@material-tailwind/react";
import ArtistService, { IArtist } from "../../api/Artists.ts";
import ImageService from "../../api/ImageService.ts";
import {eventImageServUrl, imageUrl} from "../../shared/funcsNconsts.ts";
import EventService, {IEvent} from "../../api/EventService.ts";

interface Props {
    isOpen: boolean;
    handleClose: () => void;
    editableArtist: IArtist | null;
    setEditableArtist: React.Dispatch<React.SetStateAction<IArtist | null>>;
    setArtists: React.Dispatch<React.SetStateAction<IArtist[]>>;
}

const EditArtistModal = ({ isOpen, handleClose, editableArtist, setEditableArtist, setArtists }: Props) => {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [image, setImage] = useState<File | null>(null);
    const [events, setEvents] = useState([]);
    const [barId, setBarId] = useState(1);

    useEffect(() => {
        if (editableArtist) {
            setName(editableArtist.name);
            setDescription(editableArtist.description || '');
        }
    }, [editableArtist]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        if (name === 'name') {
            setName(value);
        } else if (name === 'description') {
            setDescription(value);
        }
    };

    const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setImage(e.target.files[0]);
        }
    };

    const handleSubmit = async () => {
        if (editableArtist) {
            try {
                if (image) {
                    const formData = new FormData();
                    formData.append('file', image);
                    const res = await ImageService.uploadImage(formData, eventImageServUrl);
                    setEditableArtist({ ...editableArtist, img_path: res.data });
                    await ArtistService.update({
                        artist_id: editableArtist.artist_id,
                        name: name,
                        description: description,
                        img_path: res.data.message,
                    }
                    );
                } else {
                    await ArtistService.update({
                        artist_id: editableArtist.artist_id,
                        name: name,
                        description: description,
                    });
                }

                setEditableArtist(null);
                setArtists(artists => artists.map(artist => artist.artist_id === editableArtist.artist_id ? { ...artist, name, description } : artist));
                window.location.reload();
                handleClose();
            } catch (error) {
                console.error(error);
            }
        }
    };

    useEffect(() => {
        return () => {
            setEvents([]);
        }
    }, []);

    const handleEvents = async () => {
        try {
            const res = await EventService.getBarEvents(barId)
            setEvents(res.data);
        } catch (error) {
            console.error(error);
        }
    };

    useEffect(() => {
        (async () => {
            const res = await EventService.getBarEvents(barId)
            setEvents(res.data);
        })()
    }, [barId])

    const handleChangeBarId = (value) => {
        setBarId(value);
    }

    const addArtistToEvent = async (event_id: number) => {
        try {
            await ArtistService.addToEvent({
                event_id: event_id,
                artist_id: editableArtist!.artist_id
        });
        } catch (error) {
            console.error(error);
        }
    }

    return (
        <div>
            <Dialog open={isOpen} className='bg-neutral-800 overflow-y-scroll h-auto max-h-full'>
                <DialogHeader className='text-white'>Изменить артиста</DialogHeader>
                <DialogBody className='text-white flex flex-col gap-4'>
                    <Input
                        label="Имя"
                        name="name"
                        value={name}
                        onChange={handleInputChange}
                        color='white'
                    />
                    <Input
                        label="Описание"
                        name="description"
                        value={description}
                        onChange={handleInputChange}
                        color='white'
                    />
                    <Input
                        label="Картинка"
                        name="image"
                        type="file"
                        onChange={handleImageChange}
                        color='white'
                    />
                    <Button color='blue-gray' onClick={handleEvents} className='text-white'>
                        Добавить в событие
                    </Button>
                    {events.length > 0 && events && (
                        <div>
                            <Select onChange={handleChangeBarId} value={barId.toString()} className='text-white'>
                                <Option value='1' defaultChecked={true}>Ровесник</Option>
                                <Option value='2'>Скрепка</Option>
                                <Option value='3'>Дорожка</Option>
                            </Select>
                            <div className='flex flex-col gap-2'>
                                {events.map((event: IEvent) => (
                                    <div className='bg-neutral-600 flex flex-col'>
                                        <div key={event.event_id} className='flex gap-2 bg-neutral-600 p-4 items-center'>
                                            <img src={imageUrl + event.img_path} alt={event.short_name}
                                                 className='w-40 h-20 rounded-md'/>
                                            <div className='flex flex-col gap-1'>
                                                <p className='font-bold text-lg'>{event.short_name}</p>
                                                <p className='truncate w-80'>{event.description}</p>
                                                <p>Тип: {event.event_type}</p>
                                            </div>
                                        </div>
                                        <Button color='blue-gray' onClick={() => addArtistToEvent(event.event_id)}>
                                            Добавить
                                        </Button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </DialogBody>

                <DialogFooter>
                    <Button color="red" variant={'text'} onClick={handleClose}>Отмена</Button>
                    <Button color="green" variant={'filled'} onClick={handleSubmit}>Сохранить</Button>
                </DialogFooter>
            </Dialog>
        </div>
    );
};

export default EditArtistModal;
