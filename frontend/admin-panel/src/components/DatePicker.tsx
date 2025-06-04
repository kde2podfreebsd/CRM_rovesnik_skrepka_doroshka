import React, { useEffect, useState } from "react";
import { format } from "date-fns";
import { DayPicker } from "react-day-picker";
import { ChevronRightIcon, ChevronLeftIcon } from "@heroicons/react/24/outline";
import { Input } from "@material-tailwind/react";
import { formatDate } from "../shared/funcsNconsts.ts";

interface DatePickerProps {
    setInputPCEndTime: React.Dispatch<React.SetStateAction<Date | undefined>>;
    inputPCEndTime?: Date
    text: string;
}

const DatePicker: React.FC<DatePickerProps> = ({ setInputPCEndTime, inputPCEndTime, text }) => {
    const [month, setMonth] = useState<Date>(inputPCEndTime || new Date());

    useEffect(() => {
        if (inputPCEndTime) {
            setMonth(inputPCEndTime);
        }
    }, [inputPCEndTime]);

    return (
        <div className="relative z-50">
            <h1 className="font-bold border-b-2 text-white">{text} {inputPCEndTime ? format(inputPCEndTime, 'dd.MM.yyyy').slice(0, 11) : ''}</h1>
            <DayPicker
                mode="single"
                selected={inputPCEndTime}
                onSelect={setInputPCEndTime}
                month={month}
                onMonthChange={setMonth}
                showOutsideDays
                className="border-0 mt-4 w-full"
                classNames={{
                    caption: "flex justify-between items-center py-2 mb-4",
                    caption_label: "text-sm font-medium text-gray-900 text-white",
                    nav: "flex items-center",
                    nav_button: "h-6 w-6 bg-transparent hover:bg-blue-gray-50 p-1 rounded-md transition-colors duration-300",
                    nav_button_previous: "ml-2",
                    nav_button_next: "mr-2",
                    table: "w-full border-collapse",
                    head_row: "flex font-medium text-gray-900 justify-between",
                    head_cell: "w-1/7 text-center font-normal text-sm text-white",
                    row: "flex w-full mt-2 justify-between",
                    cell: "text-gray-600 rounded-md h-9 w-9 text-center text-sm p-0 m-0.5 relative focus-within:relative focus-within:z-20",
                    day: "h-9 w-9 p-0 font-normal text-white",
                    day_range_end: "day-range-end",
                    day_today: "rounded-md text-yellow-500",
                    day_outside: "text-gray-500 opacity-50",
                    day_selected: "rounded-md bg-blue-600 text-white hover:bg-blue-600 hover:text-white focus:bg-blue-600 focus:text-white transition-colors duration-300",
                    day_disabled: "text-gray-500 opacity-50",
                    day_hidden: "invisible",
                }}
                components={{
                    IconLeft: ({ ...props }) => (
                        <ChevronLeftIcon {...props} className="h-4 w-4 stroke-2" />
                    ),
                    IconRight: ({ ...props }) => (
                        <ChevronRightIcon {...props} className="h-4 w-4 stroke-2" />
                    ),
                }}
            />
        </div>
    );
};

export default DatePicker;
