import React, { useEffect, useState } from 'react';
import { Button, Card, Typography } from "@material-tailwind/react";
import { PencilIcon, TrashIcon, EyeIcon } from "@heroicons/react/24/outline";
import UserService, {IUser} from "../../api/UserService.ts";
import {rowsColors} from "../../shared/funcsNconsts.ts";
import EditUserModal from "../editModals/EditUserModal.tsx";
import LoyaltyInfoModal from "./LoyaltyInfoModal.tsx";
import promoCodes from "../PromoCodes.tsx";

const Users = () => {
    const [users, setUsers] = useState<IUser[]>([]);
    const [isCreate, setIsCreate] = useState(false);
    const [isEdit, setIsEdit] = useState(false);
    const [isLoyaltyInfoOpen, setIsLoyaltyInfoOpen] = useState(false);
    const [editableUser, setEditableUser] = useState<IUser | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleEdit = (chat_id: number) => {
        setEditableUser(users.find((user) => user.chat_id === chat_id) || null);
        setIsEdit(true);
    }

    const handleShowLoyaltyInfo = (chat_id: number) => {
        setEditableUser(users.find((user) => user.chat_id === chat_id) || null);
        setIsLoyaltyInfoOpen(true);
    }

    useEffect(() => {
        (async () => {
            setIsLoading(true)
            const res = await UserService.getAll();
            setUsers(res.data.message);
            setIsLoading(false)
        })();
    }, []);

    const TABLE_HEAD = ['', "Chat ID", "Username", "First Name", "Last Name", "Phone", "Spent Amount", "Referral Link", "Balance"];

    if (isLoading) {
        return <div className='w-full min-h-screen h-full flex justify-center items-center'><div className={"loader"}></div></div>;
    }

    return (
        <>
            <div className='p-2'>
                {users.length > 0 ? (
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
                            <tbody >
                            {users.map((user, index) => (
                                <tr key={index} className={`${index % 2 === 0 ? rowsColors.first : rowsColors.second}`}>
                                    <td className="p-4">
                                        <div className="flex gap-2">
                                            <Button color='blue-gray' onClick={() => handleEdit(user.chat_id)}>
                                                <PencilIcon className='w-5 h-5'/>
                                            </Button>
                                            <Button color='blue-gray' onClick={() => handleShowLoyaltyInfo(user.chat_id)}>
                                                <EyeIcon className='w-5 h-5'/>
                                            </Button>
                                        </div>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {user.chat_id}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {user.username}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {user.first_name}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {user.last_name}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {user.phone}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {user.spent_amount}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {user.referral_link}
                                        </Typography>
                                    </td>
                                    <td className="p-4">
                                        <Typography variant="small" color="white" className="font-normal">
                                            {user.balance}
                                        </Typography>
                                    </td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                    </Card>
                ) : (
                    <p className='w-full min-h-screen h-full flex justify-center items-center'>Пусто</p>
                )}
            </div>
            {isEdit && editableUser &&
                <EditUserModal setUsers={setUsers} editableUser={editableUser} setEditableUser={setEditableUser} isOpen={isEdit} handleClose={() => setIsEdit(false)} />}
            {isLoyaltyInfoOpen && editableUser && <LoyaltyInfoModal isOpen={isLoyaltyInfoOpen} handleClose={() => setIsLoyaltyInfoOpen(false)} qrCodePath={editableUser.qr_code_path} client={editableUser} />}
        </>
    );
};

export default Users;
