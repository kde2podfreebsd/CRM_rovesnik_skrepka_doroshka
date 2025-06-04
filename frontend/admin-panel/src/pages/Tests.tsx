import React, { useEffect, useState } from 'react';
import {Button, Card, Typography} from '@material-tailwind/react';
import TestsService from "../api/Tests.ts";
import {promoCodeTypeParser} from "../shared/funcsNconsts.ts";
import CreateTestModal from "./createModals/CreateTestModal.tsx";
import {PencilIcon, TrashIcon} from "@heroicons/react/24/outline";
import ButtonWithPopover from "../components/ButtonWithPopover.tsx";
import EditTestModal from "./editModals/EditTestModal.tsx";

interface ITest {
    name: string;
    correct_cnt: number;
    total_cnt: number;
    description: string;
    test_id: number;
    promocode_type: 'ONE_TIME_FREE_MENU_ITEM';
}

const Tests = () => {
    const [tests, setTests] = useState<ITest[]>([]);
    const [isCreate, setIsCreate] = useState(false);
    const [isEdit, setIsEdit] = useState(false);
    const [editableTest, setEditableTest] = useState<ITest>();

    useEffect(() => {
        (async () => {
           const res = await TestsService.getAll()
           setTests(res.data)
        })()
    }, []);

    const TABLE_HEAD = ['', 'Название', 'Кол-во правильных ответов', 'Кол-во вопросов', 'Описание', 'Процент добавки', 'ID', 'Тип промокода'];

    const handleDeleteTest = async (number: number) => {
        try {
            await TestsService.delete(number)
            setTests( tests.filter((test) => test.test_id !== number))
        } catch (e) {
            throw new Error(e)
        }
    }

    const handleEditTest = (id: number) => {
        setEditableTest(tests.find((test) => test.test_id === id))
        setIsEdit(true)
    }

    return (
        <div className="p-2">
            <div className='mb-2'>
                <Button color='blue-gray' onClick={() => setIsCreate(true)}>Добавить тест</Button>
            </div>
            {tests.length > 0 ? (
                <Card className="h-full w-full overflow-scroll">
                    <table className="w-full min-w-max table-auto text-left">
                        <thead>
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
                        </thead>
                        <tbody>
                        {tests.map((test, index) => (
                            <tr key={index} className={`even:bg-neutral-600 odd:bg-neutral-500`}>
                                <td className=' p-4 flex gap-2'>
                                    <Button color='blue-gray' onClick={() => handleEditTest(test.test_id)}><PencilIcon
                                        className=' w-5 h-5'/></Button>
                                    <ButtonWithPopover
                                        color='blue-gray'
                                        onClick={() => handleDeleteTest(test.test_id)}
                                        popoverText='Вы уверены что хотите удалить промокод?'
                                    >
                                        <TrashIcon className='w-5 h-5'/>
                                    </ButtonWithPopover>
                                </td>
                                <td className="p-4">
                                    <Typography variant="small" color="white" className="font-normal">
                                        {test.name}
                                    </Typography>
                                </td>
                                <td className="p-4">
                                    <Typography variant="small" color="white" className="font-normal">
                                        {test.correct_cnt}
                                    </Typography>
                                </td>
                                <td className="p-4">
                                    <Typography variant="small" color="white" className="font-normal">
                                        {test.total_cnt}
                                    </Typography>
                                </td>
                                <td className="p-4">
                                    <Typography variant="small" color="white" className="font-normal max-w-xs truncate">
                                        {test.description}
                                    </Typography>
                                </td>
                                <td className="p-4">
                                    <Typography variant="small" color="white" className="font-normal">
                                        {test.test_id}
                                    </Typography>
                                </td>
                                <td className="p-4">
                                    <Typography variant="small" color="white" className="font-normal">
                                        {promoCodeTypeParser(test.promocode_type)}
                                    </Typography>
                                </td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                </Card>
            ) : (
                <p className='text-white text-xl font-normal'>Пусто</p>
            )}
            {isCreate && <CreateTestModal tests={tests} setTests={setTests} setIsOpen={setIsCreate} isOpen={isCreate} />}
            {isEdit && <EditTestModal editableTest={editableTest} setTests={setTests} setIsOpen={setIsEdit} isOpen={isEdit} />}
        </div>
    );
};

export default Tests;
