import React, { useState } from 'react';
import { Button, Dialog, DialogHeader, DialogBody, DialogFooter, Input } from "@material-tailwind/react";
import ArtistService, { IArtist } from "../../api/Artists.ts";
import ImageService from "../../api/ImageService.ts";
import { eventImageServUrl } from "../../shared/funcsNconsts.ts";

interface Props {
    isOpen: boolean;
    handleClose: () => void;
    setArtists: React.Dispatch<React.SetStateAction<IArtist[]>>;
}

const CreateArtistModal = ({ isOpen, handleClose, setArtists }: Props) => {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [image, setImage] = useState<File | null>(null);

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
        try {
            let img_path = '';

            if (image) {
                const formData = new FormData();
                formData.append('file', image);
                const res = await ImageService.uploadImage(formData, '/events/');
                img_path = res.data.message;
                console.log(img_path)
            }

            const newArtist = {
                name,
                description,
                img_path,
            };

            await ArtistService.create(newArtist);
            // @ts-ignore
            setArtists(prevArtists => [...prevArtists, newArtist]);
            handleClose();
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <Dialog open={isOpen} className='bg-neutral-800' handler={ handleClose}>
            <DialogHeader className='text-white'>Добавить артиста</DialogHeader>
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
            </DialogBody>
            <DialogFooter>
                <Button color="red" variant={'text'} onClick={handleClose}>Отмена</Button>
                <Button color="green" variant={'filled'} onClick={handleSubmit}>Сохранить</Button>
            </DialogFooter>
        </Dialog>
    );
};

export default CreateArtistModal;
