import React, { useEffect, useState } from 'react';
import { Button, Card, Typography } from "@material-tailwind/react";
import {PencilIcon, TrashIcon, PaperAirplaneIcon} from "@heroicons/react/24/outline";
import CreateMailingModal from "../createModals/CreateMailingModal.tsx";
import MailingService, {IMailing} from "../../api/MailingService.ts";
import {imageUrl, rowsColors} from "../../shared/funcsNconsts.ts";
import ButtonWithPopover from "../../components/ButtonWithPopover.tsx";
import SendMaling from "./SendMaling.tsx";
import EditMailingModal from "../editModals/EditMailingModal.tsx";
import './../loader/loader.css'

const Smm = () => {
    const [isCreate, setIsCreate] = useState(false);
    const [mailings, setMailings] = useState<IMailing[]>([]);
    const [isSending, setIsSending] = useState(false);
    const [clickedMailing, setClickedMailing] = useState<IMailing>();
    const [isEditing, setIsEditing] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        (async () => {
            setIsLoading(true)
            const res = await MailingService.getAll();
            if (Array.isArray(res.data.message)){
                setMailings(res.data.message);
            }
            setIsLoading(false)
        })();
    }, []);

    const TABLE_HEAD = [
        '',
        "Название",
        "Текст",
        "Пресет",
        "Фотографии",
        "Видео",
        "Документы",
        "URL Кнопки",
        "% Alpha",
        "Alpha отправлено",
        "Alpha доставлено",
        "% Beta",
        "Beta отправлено",
        "Beta доставлено"
    ];

    const handleDeleteMailing = async (name: string) => {
        await MailingService.delete(name);
        setMailings(mailings.filter((mailing) => mailing.mailing_name !== name));
    }

    if (isLoading) {
        return <div className="w-full h-screen justify-center items-center flex"><div className='loader'></div></div>
    }

    return (
        <>
            <div className='p-4'>
                <Button color='blue-gray' onClick={() => setIsCreate(true)}>
                    Создать рассылку
                </Button>
                <div className='mt-4'>
                    <h1 className='text-white text-xl font-bold'>Рассылки</h1>
                </div>
            </div>
            <div className='p-2'>
                {mailings.length > 0 ? (
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
                            {mailings.map((mailing, index) => (
                                <tr key={index} className={`${index % 2 === 0 ? rowsColors.first : rowsColors.second}`}>
                                    <td className="p-4">
                                        <div className="flex gap-2">
                                            <Button color='blue-gray'
                                                    onClick={() =>{
                                                        setIsEditing(true)
                                                        setClickedMailing(mailing)
                                                    }}><PencilIcon
                                                className=' w-5 h-5'/>
                                            </Button>
                                            <ButtonWithPopover
                                                color='blue-gray'
                                                onClick={() => handleDeleteMailing(mailing.mailing_name)}
                                                popoverText='Вы уверены что хотите удалить рассылку?'
                                            >
                                                <TrashIcon className='w-5 h-5'/>
                                            </ButtonWithPopover>
                                            <Button color='blue-gray' onClick={() => {
                                                setIsSending(true)
                                                setClickedMailing(mailing)
                                            }}>
                                                <PaperAirplaneIcon  className=' w-5 h-5'/>
                                            </Button>
                                        </div>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {mailing.mailing_name}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {mailing.text}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {mailing.preset}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <div className='flex gap-4'>
                                            {mailing.photo_paths?.map((path, idx) => (
                                                <img src={imageUrl + path} alt='Загрузка...' key={idx} className=' w-24 h-12'/>
                                            ))}
                                        </div>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {mailing.video_paths?.length} шт.
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {mailing.document_paths?.length} шт.
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {mailing.url_buttons.map((btn, idx) => (
                                                <div key={idx}>
                                                    <p>{btn[0]}</p>
                                                </div>
                                            ))}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {mailing.alpha}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {mailing.alpha_sent}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {mailing.alpha_delivered}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {mailing.beta}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {mailing.beta_sent}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {mailing.beta_delivered}
                                        </Typography>
                                    </td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                    </Card>
                ) : (
                    <p className=' text-white font-normal text-xl'>Нет рассылок</p>
                )}
            </div>
            {isCreate && <CreateMailingModal isOpen={isCreate} handleClose={() => setIsCreate(false)}
                                             setMailings={setMailings}/>}
            {isSending && clickedMailing && <SendMaling isOpen={ isSending} handleClose={ () => setIsSending(false)} mailing={ clickedMailing}  />}
            {isEditing && clickedMailing && <EditMailingModal isOpen={isEditing} handleClose={() => setIsEditing(false)} mailing={clickedMailing} setMailings={ setMailings}/>}
        </>
    );
};

export default Smm;
