import React, { useState } from 'react';
import { Button, Dialog, DialogHeader, DialogBody, DialogFooter, Input, Textarea } from "@material-tailwind/react";
import MailingService, {IMailing} from "../../api/MailingService.ts";
import ImageService from "../../api/ImageService.ts";
import {eventImageServUrl} from "../../shared/funcsNconsts.ts";

interface Props {
    isOpen: boolean;
    handleClose: () => void;
    setMailings: React.Dispatch<React.SetStateAction<IMailing[]>>; // Обновите тип в зависимости от структуры данных рассылки
}

const CreateMailingModal = ({ isOpen, handleClose, setMailings }: Props) => {
    const [mailingName, setMailingName] = useState('');
    const [text, setText] = useState('');
    const [preset, setPreset] = useState('');
    const [photoFiles, setPhotoFiles] = useState<File[]>([]);
    const [videoFiles, setVideoFiles] = useState<File[]>([]);
    const [documentFiles, setDocumentFiles] = useState<File[]>([]);
    const [urlButtons, setUrlButtons] = useState([{ url: '', button_text: '' }]);
    const [alpha, setAlpha] = useState(0);
    const [beta, setBeta] = useState(0);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        switch (name) {
            case 'mailingName':
                setMailingName(value);
                break;
            case 'text':
                setText(value);
                break;
            case 'preset':
                setPreset(value);
                break;
            case 'alpha':
                setAlpha(Number(value));
                break;
            case 'beta':
                setBeta(Number(value));
                break;
            default:
                break;
        }
    };

    const handleFilesChange = (e: React.ChangeEvent<HTMLInputElement>, setFiles: React.Dispatch<React.SetStateAction<File[]>>) => {
        if (e.target.files) {
            setFiles(Array.from(e.target.files));
        }
    };

    const handleUrlButtonChange = (index: number, e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        const newUrlButtons = [...urlButtons];
        newUrlButtons[index] = { ...newUrlButtons[index], [name]: value };
        setUrlButtons(newUrlButtons);
    };

    const handleAddUrlButton = () => {
        setUrlButtons([...urlButtons, { url: '', button_text: '' }]);
    };

    const handleRemoveUrlButton = (index: number) => {
        const newUrlButtons = urlButtons.filter((_, idx) => idx !== index);
        setUrlButtons(newUrlButtons);
    };

    const handleSubmit = async () => {
        try {
            const photoPaths = await Promise.all(photoFiles.map(async (file) => {
                const formData = new FormData();
                formData.append('file', file);
                const res = await ImageService.uploadImage(formData, eventImageServUrl);
                return res.data.message;
            }));

            const videoPaths = await Promise.all(videoFiles.map(async (file) => {
                const formData = new FormData();
                formData.append('file', file);
                const res = await ImageService.uploadImage(formData, eventImageServUrl); // Assuming the same endpoint for video
                return res.data.message;
            }));

            const documentPaths = await Promise.all(documentFiles.map(async (file) => {
                const formData = new FormData();
                formData.append('file', file);
                const res = await ImageService.uploadImage(formData, eventImageServUrl);
                return res.data.message;
            }));

            const newMailing = {
                mailing_name: mailingName,
                text,
                preset,
                photo_paths: photoPaths,
                video_paths: videoPaths,
                document_paths: documentPaths,
                url_buttons: urlButtons,
                alpha,
                beta
            };

            await MailingService.create(newMailing);
            setMailings([...mailings, newMailing]);
            handleClose();
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <Dialog open={isOpen} className='bg-neutral-800' handler={handleClose}>
            <DialogHeader className='text-white'>Создать рассылку</DialogHeader>
            <DialogBody className='text-white flex flex-col gap-4'>
                <Input
                    label="Название"
                    name="mailingName"
                    value={mailingName}
                    onChange={handleInputChange}
                    color='white'
                />
                <Textarea
                    label="Текст"
                    name="text"
                    value={text}
                    onChange={handleInputChange}
                    className='text-white'
                />
                <Input
                    label="Пресет"
                    name="preset"
                    value={preset}
                    onChange={handleInputChange}
                    color='white'
                />
                <Input
                    label="Фото"
                    name="photoFiles"
                    type="file"
                    multiple
                    onChange={(e) => handleFilesChange(e, setPhotoFiles)}
                    color='white'
                />
                <Input
                    label="Видео"
                    name="videoFiles"
                    type="file"
                    multiple
                    onChange={(e) => handleFilesChange(e, setVideoFiles)}
                    color='white'
                />
                <Input
                    label="Документы"
                    name="documentFiles"
                    type="file"
                    multiple
                    onChange={(e) => handleFilesChange(e, setDocumentFiles)}
                    color='white'
                />
                <div className="flex flex-col gap-2">
                    {urlButtons.map((button, index) => (
                        <div key={index} className="flex gap-2">
                            <Input
                                label="URL"
                                name="url"
                                value={button.url}
                                onChange={(e) => handleUrlButtonChange(index, e)}
                                color='white'
                            />
                            <Input
                                label="Текст кнопки"
                                name="button_text"
                                value={button.button_text}
                                onChange={(e) => handleUrlButtonChange(index, e)}
                                color='white'
                            />
                            <Button color="red" onClick={() => handleRemoveUrlButton(index)}>Удалить</Button>
                        </div>
                    ))}
                    <Button color="blue-gray" onClick={handleAddUrlButton}>Добавить кнопку</Button>
                </div>
                <Input
                    label="Alpha"
                    name="alpha"
                    value={alpha}
                    type="number"
                    onChange={handleInputChange}
                    color='white'
                />
                <Input
                    label="Beta"
                    name="beta"
                    value={beta}
                    type="number"
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

export default CreateMailingModal;
