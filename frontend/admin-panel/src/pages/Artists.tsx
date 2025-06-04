import React, { useEffect, useState } from 'react';
import { Card, Typography, Avatar, Button } from "@material-tailwind/react";
import {bgAdd, imageUrl, rowsColors} from "../shared/funcsNconsts.ts";
import ArtistService, { IArtist } from "../api/Artists.ts";
import { PencilIcon, TrashIcon } from "@heroicons/react/24/outline";
import ButtonWithPopover from "../components/ButtonWithPopover.tsx";
import EditArtistModal from "./editModals/EditArtistsModal.tsx";
import CreateArtistModal from "./createModals/CreateArtistModal.tsx";

const Artists = () => {
    const [artists, setArtists] = useState<IArtist[]>([]);
    const [isEditing, setIsEditing] = useState(false);
    const [editableArtist, setEditableArtist] = useState<IArtist>();
    const [isCreate, setIsCreate] = useState(false);

    useEffect(() => {
        (async () => {
            const res = await ArtistService.getAll();
            setArtists(res.data);
        })();
    }, []);

    const handleEditArtist = (id: number) => {
        setEditableArtist(artists.find((artist) => artist.artist_id === id));
        setIsEditing(true);
    };

    const handleDeleteArtist = async (id: number) => {
        try {
            await ArtistService.delete(id);
            setArtists(artists.filter((artist) => artist.artist_id !== id));
        } catch (e) {
            throw new Error(e);
        }
    };

    const TABLE_HEAD = ["", "ID", "Имя", "Описание", "Медиа"];

    return (
        <>
            <div className='p-2'>
                <div className='mb-2'>
                    <Button color='blue-gray' onClick={() => setIsCreate(true)}>Добавить артиста</Button>
                </div>
                {artists.length > 0 ? (
                    <Card className="h-full w-full overflow-scroll">
                        <table className="w-full min-w-max table-auto text-left">
                            <thead>
                            <tr>
                                {TABLE_HEAD.map((head) => (
                                    <th key={head} className="border-b border-blue-gray-100 bg-neutral-700 p-4">
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
                            {artists.map((artist, index) => (
                                <tr key={index} className={`${index % 2 === 0 ? rowsColors.first : rowsColors.second}`}>
                                    <td className="p-4">
                                        <div className="flex gap-2">
                                            <Button color='blue-gray' onClick={() => handleEditArtist(artist.artist_id)}>
                                                <PencilIcon className=' w-5 h-5'/>
                                            </Button>
                                            <ButtonWithPopover
                                                color='blue-gray'
                                                onClick={() => handleDeleteArtist(artist.artist_id)}
                                                popoverText='Вы уверены что хотите удалить артиста?'
                                            >
                                                <TrashIcon className='w-5 h-5'/>
                                            </ButtonWithPopover>
                                        </div>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {artist.artist_id}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {artist.name}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal max-w-xs truncate">
                                            {artist.description}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Avatar src={imageUrl + artist.img_path} className='w-24 h-24' variant="circular"/>
                                    </td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                    </Card>
                ) : (
                    <p className='text-white text-xl font-normal'>Пусто</p>
                )}
            </div>
            {editableArtist &&
                <EditArtistModal
                    isOpen={isEditing}
                    handleClose={() => setIsEditing(false)}
                    editableArtist={editableArtist}
                    setEditableArtist={setEditableArtist}
                />
            }
            {isEditing&& <EditArtistModal isOpen={isEditing} artists={artists} setArtists={setArtists} setIsOpen={setIsEditing} editableArtist={editableArtist} setEditableArtist={setEditableArtist} handleClose={() => setIsEditing(false)}/>}
            {isCreate && <CreateArtistModal isOpen={isCreate} artists={artists} setArtists={setArtists} setIsOpen={setIsCreate}  handleClose={() => setIsCreate(false)}/>}
        </>
    );
};

export default Artists;
