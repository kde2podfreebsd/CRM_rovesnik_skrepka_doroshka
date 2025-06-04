import React from 'react';
import {Button, Dialog, DialogBody, DialogFooter, DialogHeader, Input, Option, Select} from "@material-tailwind/react";
import DatePicker from "../../components/DatePicker.tsx";
import TablesService, {ITable} from "../../api/TablesService.ts";
import {formatDate} from "date-fns/format";
import ReservationService from "../../api/ReservationService.ts";
import { v4 as uuidv4 } from 'uuid';


const CreateReservation = ({ isOpen, handleClose, setReservations }: { isOpen: boolean, handleClose: () => void, setReservations: React.Dispatch<React.SetStateAction<any>>}) => {
    const [barId, setBarId] = React.useState<number>(1);
    const [capacity, setCapacity] = React.useState<string>('');
    const [clientId, setClientId] = React.useState<number>(0);
    const [startDate, setStartDate] = React.useState<Date | undefined>(undefined);
    const [startTime, setStartTime] = React.useState<string>('');
    const [tables, setTables] = React.useState<ITable[]>([]);

    const handleEndTimeChange = (value: string) => {
        setStartTime(value);
    };

    const handleChangeBarId = (value: string) => {
        setBarId(Number(value));
    };

    const sendReq = async (capacity) => {
        return await TablesService.getByTimeAndCapacity(
            formatDate(startDate?.toISOString().toString(), 'yyyy-MM-dd') + ' ' + startTime,
            Number(capacity)
        );
    };

    const handleFindTables = async (prop) => {
        if (prop === 9) {
            return;
        }

        const res = await sendReq(prop);

        if (res.data.Status === 'Failed') {
            setCapacity(prevState => (Number(prevState) + 1).toString());
            await handleFindTables(Number(capacity) + 1);
        } else {
            setTables(res.data.Message);
        }
    };

    const handleBook = async (tableuuid) => {
        await ReservationService.create({
            client_chat_id: clientId,
            table_uuid: tableuuid,
            reservation_start: formatDate(startDate?.toISOString().toString(), 'yyyy-MM-dd') + ' ' + startTime + ':00.000',
            deposit: 0,
            order_uuid: uuidv4()
        })
    }

    const handleInputChange = (value) => {
        setCapacity(value);
    }

    return (
       <Dialog open={isOpen} onClose={handleClose} className='bg-neutral-800 overflow-y-auto max-h-full w-full' >
           <DialogHeader className='text-white'>Создание резервации</DialogHeader>
           <DialogBody className='flex flex-col gap-4'>
               <p className='text-white'>Выберите бар</p>
               <Select onChange={handleChangeBarId} value={barId.toString()} className='text-white' dismiss={undefined}>
                   <Option value='1' defaultChecked={true}>Ровесник</Option>
                   {/*<Option value='2'>Скрепка</Option>*/}
                   {/*<Option value='3'>Дорожка</Option>*/}
               </Select>
               <Select onChange={handleInputChange} value={capacity} className='text-white' label='Кол-во мест'>
                   {[2,4,5,8].map( i => <Option key={i} value={i.toString()}>{i}</Option>)}
               </Select>
               <Input color='white' label="ID пользователя" value={clientId}
                      onChange={e => setClientId(Number(e.target.value))} className='text-white'/>
               <DatePicker setInputPCEndTime={setStartDate} inputPCEndTime={startDate} text='Дата резервации: '/>
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
               <Button color="blue-gray" onClick={() => handleFindTables(capacity)} className="mr-1">
                   Поиск
               </Button>
               <div className='flex flex-col gap-2'>
                   {tables.length > 0 && tables.map( table => (
                       <div
                           key={table.table_uuid}
                           className={`rounded-lg text-white p-4 bg-neutral-600 w-full`}
                       >
                           <p>Стол №{table.table_id}</p>
                           <p className='font-bold'>На {table.capacity} человек</p>
                           <p>На {table.storey} этаже</p>
                           <Button onClick={() => handleBook(table.table_uuid)}>
                               Забронировать
                           </Button>
                       </div>
                   ))}
               </div>
           </DialogBody>
           <DialogFooter>
               <Button variant="text" color="red" onClick={ handleClose} className="mr-1">
                   Отмена
               </Button>
           </DialogFooter>
       </Dialog>
    );
};

export default CreateReservation;