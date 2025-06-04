import React, { useState, useEffect } from 'react';
import { Button, Dialog, DialogHeader, DialogBody, DialogFooter, Input, Textarea } from "@material-tailwind/react";
import MailingService, { IMailing } from "../../api/MailingService.ts";
import ImageService from "../../api/ImageService.ts";
import { eventImageServUrl, imageUrl } from "../../shared/funcsNconsts.ts";
import { TrashIcon } from "@heroicons/react/24/outline";
import { PlayIcon } from "@heroicons/react/24/solid";

interface Props {
    isOpen: boolean;
    handleClose: () => void;
    mailing: IMailing; // Передаем существующую рассылку для редактирования
    setMailings: React.Dispatch<React.SetStateAction<IMailing[]>>; // Обновите тип в зависимости от структуры данных рассылки
}

const EditMailingModal = ({ isOpen, handleClose, mailing, setMailings }: Props) => {
    const [mailingName, setMailingName] = useState('');
    const [newMailingName, setNewMailingName] = useState('');
    const [text, setText] = useState('');
    const [preset, setPreset] = useState('');
    const [photoFiles, setPhotoFiles] = useState<File[]>([]);
    const [videoFiles, setVideoFiles] = useState<File[]>([]);
    const [documentFiles, setDocumentFiles] = useState<File[]>([]);
    const [urlButtons, setUrlButtons] = useState<string[][]>([]);
    const [alpha, setAlpha] = useState(0);
    const [beta, setBeta] = useState(0);
    const [isVideoPlaying, setIsVideoPlaying] = useState(false);
    const [clickedVideoPath, setClickedVideoPath] = useState<string>('');
    const [newUrlButtons, setNewUrlButtons] = useState<{ url: string, button_text: string }[]>([]);

    useEffect(() => {
        if (mailing) {
            setMailingName(mailing.mailing_name);
            setNewMailingName(mailing.mailing_name);
            setText(mailing.text);
            setPreset(mailing.preset);
            setUrlButtons(mailing.url_buttons);
            setAlpha(mailing.alpha);
            setBeta(mailing.beta);
        }
    }, [mailing]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        switch (name) {
            case 'newMailingName':
                setNewMailingName(value);
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
        const newButtons = [...newUrlButtons];
        newButtons[index] = { ...newButtons[index], [name]: value };
        setNewUrlButtons(newButtons);
    };

    const handleAddUrlButton = () => {
        setNewUrlButtons([...newUrlButtons, { url: '', button_text: '' }]);
    };

    const handleRemoveUrlButton = (index: number) => {
        const newnewUrlButtons = newUrlButtons.filter((_, idx) => idx !== index);
        setNewUrlButtons(newnewUrlButtons);
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
                const res = await ImageService.uploadImage(formData, eventImageServUrl);
                return res.data.message;
            }));

            const documentPaths = await Promise.all(documentFiles.map(async (file) => {
                const formData = new FormData();
                formData.append('file', file);
                const res = await ImageService.uploadImage(formData, eventImageServUrl);
                return res.data.message;
            }));

            const updatedMailing = {
                mailing_name: mailingName,
                new_mailing_name: newMailingName,
                new_text: text,
                new_photo_name: photoPaths.join(','),
                new_video_name: videoPaths.join(','),
                new_document_name: documentPaths.join(','),
                new_url_button: newUrlButtons.length > 0 ? {...newUrlButtons} : null,
                new_preset: preset,
                alpha,
                beta
            };

            await MailingService.update(updatedMailing);
            setMailings( prevMailings => prevMailings.map(m => m.mailing_name === mailing.mailing_name ? { ...m, ...updatedMailing } : m) );
            // window.location.reload();
            handleClose();
        } catch (error) {
            console.error(error);
        }
    };

    const handleDeletePhoto = async (path: string) => {
        await MailingService.deletePhotoPath(mailing.mailing_name, path);
        setMailings(prevMailings => prevMailings.map(m => m.id === mailing.id ? { ...m, photo_paths: m.photo_paths.filter(p => p !== path) } : m));
    }

    const handleDeleteVideo = async (path: string) => {
        await MailingService.deleteVideoPath(mailing.mailing_name, path);
        setMailings(prevMailings => prevMailings.map(m => m.id === mailing.id ? { ...m, video_paths: m.video_paths.filter(p => p !== path) } : m));
    }

    const handleDeleteDocument = async (path: string) => {
        await MailingService.deleteDocumentPath(mailing.mailing_name, path);
        setMailings(prevMailings => prevMailings.map(m => m.id === mailing.id ? { ...m, document_paths: m.document_paths.filter(p => p !== path) } : m));
    }

    return (
        <>
            <Dialog open={isOpen} className='bg-neutral-800 h-auto max-h-full overflow-y-auto' handler={handleClose}>
                <DialogHeader className='text-white'>Редактировать рассылку</DialogHeader>
                <DialogBody className='text-white flex flex-col gap-4'>
                    <Input
                        label="Новое название"
                        name="newMailingName"
                        value={newMailingName}
                        onChange={handleInputChange}
                        color='white'
                    />
                    <Textarea
                        label="Новый текст"
                        name="text"
                        value={text}
                        onChange={handleInputChange}
                        className='text-white'
                    />
                    <Input
                        label="Новый пресет"
                        name="preset"
                        value={preset}
                        onChange={handleInputChange}
                        color='white'
                    />
                    <p className='font-bold'>Фото:</p>
                    <div className='flex flex-wrap gap-2'>
                        {mailing.photo_paths && mailing.photo_paths.length > 0 ? (
                            mailing.photo_paths?.map((path, index) => (
                                <div className='w-72 flex flex-col gap-2' key={index}>
                                    <img src={imageUrl + path} alt='loading...'
                                         className='w-72 h-40 rounded-lg object-contain'/>
                                    <Button color='red' onClick={() => handleDeletePhoto(path)}>
                                        Удалить фото
                                    </Button>
                                </div>
                            ))
                        ) : (
                            <p>Пусто</p>
                        )}
                    </div>
                    <Input
                        label="Добавить фото"
                        name="photoFiles"
                        type="file"
                        multiple
                        onChange={(e) => handleFilesChange(e, setPhotoFiles)}
                        color='white'
                    />
                    <p className='font-bold'>Видео:</p>
                    <div>
                        {mailing.video_paths && mailing.video_paths.length > 0 ? (
                            mailing.video_paths?.map((path, index) => (
                                <div className='flex items-center gap-2' key={index}>
                                    <p>{index + 1}. {path.slice(path.lastIndexOf('/') + 1)}</p>
                                    <Button color='red' onClick={() => handleDeleteVideo(path)} size='sm'>
                                        <TrashIcon className=' w-4 h-4'/>
                                    </Button>
                                    <Button color='blue-gray' size='sm' onClick={() => {
                                        setIsVideoPlaying(true)
                                        setClickedVideoPath(path)
                                    }}>
                                        <PlayIcon className='w-4 h-4'/>
                                    </Button>
                                </div>
                            ))
                        ) : (
                            <p>Пусто</p>
                        )}
                    </div>
                    <Input
                        label="Добавить видео"
                        name="videoFiles"
                        type="file"
                        multiple
                        onChange={(e) => handleFilesChange(e, setVideoFiles)}
                        color='white'
                    />
                    <p className='font-bold'>Документы:</p>
                    <div className='flex flex-col gap-1'>
                        {mailing.document_paths.map((path, index) => (
                            <div className='flex items-center gap-2' key={index}>
                                <p className='text-xl'>{index + 1}. {path.slice(path.lastIndexOf('/') + 1)}</p>
                                <Button color='red' onClick={() => handleDeleteDocument(path)} className='p-auto'
                                        size='sm'>
                                    <TrashIcon className='w-4 h-4'/>
                                </Button>
                            </div>
                        ))}
                    </div>
                    <Input
                        label="Добавить документы"
                        name="documentFiles"
                        type="file"
                        multiple
                        onChange={(e) => handleFilesChange(e, setDocumentFiles)}
                        color='white'
                    />
                    <div className="flex flex-col gap-4">
                        {urlButtons.map((button, index) => (
                            <div key={index} className="flex gap-2">
                                <Input label="URL" name="url" value={button[0]} disabled />
                                <Input label="Текст кнопки" name="button_text" value={button[1]} disabled />
                            </div>
                        ))}
                        {newUrlButtons.map((button, index) => (
                            <div key={index} className="flex gap-2">
                                <Input label="URL" name="url" value={button.url}
                                       onChange={(e) => handleUrlButtonChange(index, e)} color='white'/>
                                <Input label="Текст кнопки" name="button_text" value={button.button_text}
                                       onChange={(e) => handleUrlButtonChange(index, e)} color='white'/>
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
            {isVideoPlaying && clickedVideoPath && (
                <Dialog open={isVideoPlaying} handler={() => setIsVideoPlaying(false)} className='bg-neutral-600'>
                    <DialogHeader className='text-white'>Видео</DialogHeader>
                    <DialogBody className='text-white'>
                        <video className="h-full w-full rounded-lg" controls>
                            <source src={imageUrl + clickedVideoPath}/>
                            Ваш браузер не поддерживает HTML5 видео
                        </video>
                    </DialogBody>
                    <DialogFooter>
                        <Button color="red" onClick={() => setIsVideoPlaying(false)}>Закрыть</Button>
                    </DialogFooter>
                </Dialog>
            )}
        </>
    );
};

export default EditMailingModal;
