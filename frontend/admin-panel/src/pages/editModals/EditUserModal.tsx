import React, { useEffect, useState } from 'react';
import { Button, Dialog, DialogHeader, DialogBody, DialogFooter, Input } from "@material-tailwind/react";
import UserService, {IUser} from "../../api/UserService.ts";

interface Props {
    isOpen: boolean;
    handleClose: () => void;
    editableUser: IUser | null;
    setEditableUser: React.Dispatch<React.SetStateAction<IUser | null>>;
    setUsers: React.Dispatch<React.SetStateAction<IUser[]>>;
}

const EditUserModal = ({ isOpen, handleClose, editableUser, setEditableUser, setUsers }: Props) => {
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [balance, setBalance] = useState(0);

    useEffect(() => {
        if (editableUser) {
            setFirstName(editableUser.first_name);
            setLastName(editableUser.last_name || '');
        }
    }, [editableUser]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        if (name === 'firstName') {
            setFirstName(value);
        } else if (name === 'lastName') {
            setLastName(value);
        } else if (name === 'balance') {
            setBalance(parseFloat(value));
        }
    };

    const handleSubmit = async () => {
        if (editableUser) {
            try {
                if (editableUser.first_name !== firstName) {
                    await UserService.updateFirstName(editableUser.chat_id, firstName);
                }
                if (editableUser.last_name !== lastName) {
                    await UserService.updateLastName(editableUser.chat_id, lastName);
                }
                if (editableUser.balance !== balance) {
                    await UserService.refillBalance(editableUser.chat_id, balance - editableUser.balance);
                }
                setEditableUser(null);
                setUsers(users => users.map(user => user.chat_id === editableUser.chat_id ? {...user, first_name: firstName, last_name: lastName, balance: balance} : user) );
                handleClose();
            } catch (error) {
                console.error(error);
            }
        }
    };

    return (
        <Dialog open={isOpen} className='bg-neutral-800' handler={ handleClose}>
            <DialogHeader className='text-white'>Изменить пользователя</DialogHeader>
            <DialogBody className='text-white flex flex-col gap-4'>
                <Input
                    label="Имя"
                    name="firstName"
                    value={firstName}
                    onChange={handleInputChange}
                    color='white'
                />
                <Input
                    label="Фамилия"
                    name="lastName"
                    value={lastName}
                    onChange={handleInputChange}
                    color='white'
                />
                <Input
                    label="Добавить баланс"
                    name="balance"
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

export default EditUserModal;
