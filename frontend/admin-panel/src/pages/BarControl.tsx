import React, {useEffect, useState} from 'react';
import {Button, Option, Select} from "@material-tailwind/react";
import TablesService, {ITable} from "../api/TablesService.ts";

const BarControl = () => {
    const [barId, setBarId] = useState(1);
    const [tables, setTables] = useState<ITable[]>([]);
    const [floors, setFloors] = useState<number[]>([]);

    const handleChangeBarId = (value: string) => {
        setBarId(Number(value));
        setFloors(Number(value) === 1 ? [1,2,3] : [1])
    }

    useEffect(() => {
        (async () => {
            const tablesRes = await TablesService.getAll()
            const findMaxFloor = Math.max(...tablesRes.data.Message.map(table => table.storey))
            setFloors( Array.from({length: findMaxFloor}, (_, i) => i + 1))
            setTables(tablesRes.data.Message)
        })()
    }, []);

    const handleReserveFloor = async (barId: number, floor: number) => {
        await TablesService.changeStatus(floor, barId)
        setTables(prev => prev.map(table => table.bar_id === barId && table.storey === floor ? {...table, reserved: !table.reserved} : table))
    }

    const handleBlockTable = async (table_uuid: string) => {
        await TablesService.update({...tables.find(table => table.table_uuid === table_uuid), reserved: !tables.find(table => table.table_uuid === table_uuid).reserved})
        setTables( prev => prev.map(table => table.table_uuid === table_uuid ? {...table, reserved: !table.reserved} : table))
    }

    return (
        <div className='p-4 text-white'>
            <h1 className='text-xl font-bold mb-1'>Выберите бар</h1>
            <div className='w-60'>
                <Select onChange={handleChangeBarId} value={barId.toString()} className='text-white text-xl'>
                    <Option value='1'>Ровесник</Option>
                    <Option value='2'>Скрепка</Option>
                    <Option value='3'>Дорожка</Option>
                </Select>
            </div>
            <div className='flex flex-col gap-4'>
                {tables.length > 0 ? floors.map((floor) => (
                    <div className='flex flex-col gap-2'>
                        <p className='text-xl font-bold'>Этаж {floor}</p>
                        <Button color={tables.filter(table => table.bar_id === barId && table.storey === floor).every(table => table.reserved) ? 'green' : 'red'} onClick={() => handleReserveFloor(barId, floor)}>
                            {tables.filter(table => table.bar_id === barId && table.storey === floor).every(table => table.reserved) ? 'Изменить статус всего этажа' : 'Изменить статус всего этажа'}
                        </Button>
                        <div className='flex flex-wrap gap-2'>
                            {tables
                                .filter(table => table.bar_id === barId && table.storey === floor)
                                .map(table => (
                                    <div className=' bg-neutral-700 w-40 h-24 p-2 rounded-lg flex justify-center flex-col items-center'>
                                        <p className='font-normal'>Стол № {table.table_id}</p>
                                        <p className={`font-bold ${table.reserved ? 'text-red-500' : 'text-green-500'}`}>{table.reserved ? 'Заблокирован' : 'Доступен'}</p>
                                        <Button size='sm' variant='text' color='white' onClick={() => handleBlockTable(table.table_uuid)}>
                                            {table.reserved ? 'Разблокировать' : 'Заблокировать'}
                                        </Button>
                                    </div>
                                ))}
                        </div>
                    </div>
                )) : (
                    <p className='text-white text-xl font-normal'>Столов нет в базе данных</p>
                )}
            </div>
        </div>
    );
};

export default BarControl;