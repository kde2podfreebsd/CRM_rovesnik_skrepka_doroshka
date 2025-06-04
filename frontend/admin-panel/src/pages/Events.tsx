import { useEffect, useState } from 'react';
import EventService, { IEvent } from "../api/EventService.ts";
import {Button, Card, Option, Select, Typography} from "@material-tailwind/react";
import {barIdParser, bgAdd, formatDate, imageUrl, rowsColors} from "../shared/funcsNconsts.ts";
import {PencilIcon, TrashIcon} from "@heroicons/react/24/outline";
import ButtonWithPopover from "../components/ButtonWithPopover.tsx";
import EditEventModal from "./editModals/EditEventModal.tsx";
import CreateEventModal from "./createModals/CreateEventModal.tsx";

const Events = () => {
    const [barId, setBarId] = useState(1)
    const [events, setEvents] = useState<IEvent[]>([]);
    const [isCreate, setIsCreate] = useState(false)
    const [isEdit, setIsEdit] = useState(false)
    const [editableEvent, setEditableEvent] = useState<IEvent>()

    const TABLE_HEAD = ['', "ID события", "Название", "Описание", "Медиа", "Время начала", "Время конца", "Бар", "Адрес", "Возрастное ограничение", "Тип события", "Цена", "Уведомления"];

    const handleEdit = (id: number) => {
        setEditableEvent(events.find((event) => event.event_id === id))
        setIsEdit(true)
    }

    const handleDelete = async (id: number) => {
        try {
            await EventService.delete(id)
            setEvents( events.filter((event) => event.event_id !== id))
        } catch (e) {
            throw new Error(e)
        }
    }

    const handleChangeBarId = async (selectedBarId) => {
        setBarId(selectedBarId);
        const res = await EventService.getBarEvents(selectedBarId)
        setEvents(res.data)
    };

    useEffect(() => {
        (async () => {
            const res = await EventService.getBarEvents(barId)
            setEvents(res.data)
            console.log(res.data)
        })()
    }, []);

    return (
        <>
            <div className='p-2'>
                <div>
                    <div className='flex items-center gap-2 mb-2'>
                        <p className='text-cl text-white font-bold'>Бар: </p>
                        <div className='w-60'>
                            <Select onChange={handleChangeBarId} label='Бар' value={barId.toString()} className='text-white'
                                    dismiss={undefined}>
                                <Option value='1'>Ровесник</Option>
                                <Option value='2'>Скрепка</Option>
                                <Option value='3'>Дорожка</Option>
                            </Select>
                        </div>
                        <Button color='blue-gray' onClick={() => setIsCreate(true)}>Добавить</Button>
                    </div>
                </div>
                {events.length > 0 ? (
                    <Card className="h-full w-full overflow-scroll">
                        <table className="w-full min-w-max table-auto text-left">
                            <thead>
                            <tr>
                                {TABLE_HEAD.map((head) => (
                                    <th key={head} className="border-b border-blue-gray-100 bg-neutral-800 p-4">
                                        <Typography
                                            variant="small"
                                            color="blue-gray"
                                            className="leading-none opacity-70 text-white font-bold text-xl"
                                        >
                                            {head}
                                        </Typography>
                                    </th>
                                ))}
                            </tr>
                            </thead>
                            <tbody>
                            {events.map((event, index) => (
                                <tr key={index} className={`${index % 2 === 0 ? rowsColors.first : rowsColors.second}`}>
                                    <td className="p-4">
                                        <div className="flex gap-2">
                                            <Button color='blue-gray'
                                                    onClick={() => handleEdit(event.event_id)}><PencilIcon
                                                className=' w-5 h-5'/></Button>
                                            <ButtonWithPopover
                                                color='blue-gray'
                                                onClick={() => handleDelete(event.event_id)}
                                                popoverText='Вы уверены что хотите удалить событие?'
                                            >
                                                <TrashIcon className='w-5 h-5'/>
                                            </ButtonWithPopover>
                                        </div>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {event.event_id}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {event.short_name}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal max-w-xs truncate">
                                            {event.description}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <div className='w-40 h-20 flex justify-center items-center'>
                                            <img src={imageUrl + event.img_path} alt="" className='w-40 h-20 object-cover'/>
                                        </div>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {formatDate(event.dateandtime)}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {formatDate(event.end_datetime)}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {barIdParser(event.bar_id)}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {event.place}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {event.age_restriction}+
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {event.event_type}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {event.price}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {event.notification_time && event.notification_time.join(', ')}
                                        </Typography>
                                    </td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                    </Card>
                ) : (
                    <p className='text-white p-4'>Пусто</p>
                )}
            </div>
            {isEdit && editableEvent && <EditEventModal setEvents={setEvents} editableEvent={editableEvent} setEditableEvent={setEditableEvent} isOpen={isEdit} handleClose={() => setIsEdit(false)}/>}
            {isCreate && <CreateEventModal setEvents={setEvents} isOpen={isCreate}
                                           handleClose={() => setIsCreate(false)} barId={barId}/>}
        </>

    );

};

export default Events;
