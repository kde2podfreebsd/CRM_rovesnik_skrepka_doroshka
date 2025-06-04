import React, { useEffect, useState } from 'react';
import { Button, Dialog, DialogBody, DialogFooter, DialogHeader, Input, Option, Select } from "@material-tailwind/react";
import TablesService, { ITable } from "../../api/TablesService.ts";
import DatePicker from "../../components/DatePicker.tsx";
import { formatDate } from "date-fns/format";
import ReservationService from "../../api/ReservationService.ts";
import { v4 as uuidv4 } from 'uuid';

const MergeTablesModal = ({ isMerge, setIsMerge, setFilteredReservations }: { isMerge: boolean, setIsMerge: React.Dispatch<React.SetStateAction<boolean>>, setFilteredReservations: React.Dispatch<React.SetStateAction<ITableReservation[]>> }) => {
    const [startDate, setStartDate] = useState<Date | undefined>(undefined);
    const [startTime, setStartTime] = useState<string>('');
    const [tables, setTables] = useState<ITable[]>([]);
    const [barId, setBarId] = useState<string>('');
    const [capacity, setCapacity] = useState<string>('');
    const [selectedTable1, setSelectedTable1] = useState<ITable | null>(null);
    const [selectedTable2, setSelectedTable2] = useState<ITable | null>(null);
    const [clientId, setClientId] = useState<number>(0);

    const handleEndTimeChange = (value: string) => {
        setStartTime(value);
    };

    const handleChangeBarId = (value: string) => {
        setBarId(value);
    };

    const handleFindTables = async () => {
        try {
            const startDateToSend = formatDate(startDate?.toISOString().toString(), 'yyyy-MM-dd');
            const timeString = startDateToSend + ' ' + startTime;

            const requests = [
                TablesService.getByTimeAndCapacity(timeString, 4),
                TablesService.getByTimeAndCapacity(timeString, 5),
                TablesService.getByTimeAndCapacity(timeString, 6),
                TablesService.getByTimeAndCapacity(timeString, 7),
                TablesService.getByTimeAndCapacity(timeString, 8)
            ];

            const responses = await Promise.all(requests);

            const validResponses = responses
                .filter(res => res.data.Status !== 'Failed')
                .map(res => res.data.Message);

            const allTables: ITable[] = [].concat(...validResponses);

            console.log(allTables);
            setTables(allTables);
        } catch (error) {
            console.error(error);
        }
    };

    const handleTableSelect1 = (table: ITable) => {
        if (selectedTable2?.table_uuid === table.table_uuid) {
            alert("Этот стол уже выбран во втором окне.");
        } else {
            setSelectedTable1(table);
        }
    };

    const handleTableSelect2 = (table: ITable) => {
        if (selectedTable1?.table_uuid === table.table_uuid) {
            alert("Этот стол уже выбран в первом окне.");
        } else {
            setSelectedTable2(table);
        }
    };

    const handleSubmit = async () => {
        const startDateToSend = formatDate(startDate?.toISOString().toString(), 'yyyy-MM-dd');
        const timeString = startDateToSend + ' ' + startTime;
        const uuid = uuidv4();

        try {
            const [firstReservation, secondReservation] = await Promise.all([
                ReservationService.create({
                    client_chat_id: clientId,
                    table_uuid: selectedTable1!.table_uuid!,
                    reservation_start: startDateToSend + ' ' + startTime + ':00.000',
                    order_uuid: uuid,
                    deposit: 0,
                }),
                ReservationService.create({
                    client_chat_id: clientId,
                    table_uuid: selectedTable2!.table_uuid!,
                    reservation_start: startDateToSend + ' ' + startTime + ':00.000',
                    order_uuid: uuid,
                    deposit: 0,
                })
            ]);

            console.log('[FIRST]', firstReservation.data);
            console.log('[SECOND]', secondReservation.data);
        } catch (error) {
            console.error(error);
        }
    };


    return (
        <>
            <Dialog open={isMerge} handler={setIsMerge} className='bg-neutral-800 overflow-y-auto max-h-full w-full'>
                <DialogHeader className='text-white'>Объединить столы</DialogHeader>
                <DialogBody divider className='flex gap-4 w-full flex-col'>
                    <div className='flex flex-col gap-4 w-full'>
                        <p className='text-white'>Выберите бар</p>
                        <Select onChange={handleChangeBarId} value={barId.toString()} className='text-white' dismiss={undefined}>
                            <Option value='1' defaultChecked={true}>Ровесник</Option>
                            {/*<Option value='2'>Скрепка</Option>*/}
                            {/*<Option value='3'>Дорожка</Option>*/}
                        </Select>
                        <Input color='white' label="Количество гостей" value={capacity}
                               onChange={e => setCapacity(e.target.value)} className='text-white' />
                        <Input color='white' label="ID пользователя" value={clientId}
                               onChange={e => setClientId(Number(e.target.value))} className='text-white' />
                        <DatePicker setInputPCEndTime={setStartDate} inputPCEndTime={startDate} text='Дата резервации: ' />
                        <Select
                            label="Время резервации"
                            value={startTime}
                            onChange={handleEndTimeChange}
                            className='text-white'
                            dismiss={undefined}
                        >
                            {[...Array(10 * 2)].map((_, i) => {
                                const hour = Math.floor(14 + i / 2);
                                const minute = (i % 2) * 30;
                                const hourString = hour.toString().padStart(2, '0');
                                const minuteString = minute.toString().padStart(2, '0');
                                return (
                                    <Option key={`${hourString}:${minuteString}`} value={`${hourString}:${minuteString}`}>
                                        {`${hourString}:${minuteString}`}
                                    </Option>
                                );
                            })}
                        </Select>
                        <Button color="blue-gray" onClick={handleFindTables} className="mr-1">
                            Поиск
                        </Button>
                    </div>
                    <div className='w-full flex gap-8'>
                        <div className='w-1/2 flex flex-col gap-2'>
                            <p className='text-white font-semibold'>Первый стол</p>
                            {tables.map(table => (
                                <div
                                    key={table.table_uuid}
                                    className={`rounded-lg text-white p-4 ${selectedTable1?.table_uuid === table.table_uuid ? 'bg-blue-400/50' : 'bg-neutral-600'} transition-all duration-300 `}
                                    onClick={() => handleTableSelect1(table)}
                                >
                                    <p>Стол №{table.table_id}</p>
                                    <p className='font-bold'>На {table.capacity} человек</p>
                                    <p>На {table.storey} этаже</p>
                                </div>
                            ))}
                        </div>
                        <div className='w-1/2 flex flex-col gap-2'>
                            <p className='text-white font-semibold'>Второй стол</p>
                            {tables.map(table => (
                                <div
                                    key={table.table_uuid}
                                    className={`rounded-lg text-white p-4 ${selectedTable2?.table_uuid === table.table_uuid ? 'bg-blue-400/50' : 'bg-neutral-600'} transition-all duration-300 `}
                                    onClick={() => handleTableSelect2(table)}
                                >
                                    <p>Стол №{table.table_id}</p>
                                    <p className='font-bold'>На {table.capacity} человек</p>
                                    <p>На {table.storey} этаже</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </DialogBody>
                <DialogFooter>
                    <Button variant="text" color="red" onClick={() => setIsMerge(false)} className="mr-1">
                        Отмена
                    </Button>
                    <Button color="green" onClick={handleSubmit}>
                        Сохранить
                    </Button>
                </DialogFooter>
                {tables.length > 0 && (
                    <div
                        className='fixed bottom-0 w-80 bg-neutral-500 text-white p-4 font-bold text-lg rounded-t-lg rounded-br-lg shadow-md'>
                        {selectedTable1 === null && selectedTable2 === null ? (
                            <p>Не выбраны</p>
                        ) : (
                            <>
                                <p>Выбраны
                                    столы: {selectedTable1 ? `№${selectedTable1.table_id}` : ''} {selectedTable2 ? `и №${selectedTable2.table_id}` : ''}</p>
                                <p>Мест
                                    всего: {(selectedTable1 ? selectedTable1.capacity : 0) + (selectedTable2 ? selectedTable2.capacity : 0)}</p>
                                <p>Этажи: {selectedTable1 && selectedTable2
                                    ? (selectedTable1.storey === selectedTable2.storey ? `Одинаковые ${selectedTable1.storey}` : `Разные ${selectedTable1.storey} и ${selectedTable2.storey}`)
                                    : ''}</p>
                            </>
                        )}
                    </div>
                )}
            </Dialog>
        </>
    );
};

export default MergeTablesModal;
