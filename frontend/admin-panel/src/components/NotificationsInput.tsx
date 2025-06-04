import { SetStateAction, useState } from 'react';
import { Input } from '@material-tailwind/react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import {IEvent} from "../api/EventService.ts";

interface TagsInputProps {
    setInputData: React.Dispatch<SetStateAction<IEvent[]>>;
    inputData?: IEvent;
}
const NotificationsInput = ({ setInputData, inputData }: TagsInputProps) => {
    const [notificationsArray, setNotificationsArray] = useState<string[]>(inputData?.notification_time || []);
    const [notification, setNotification] = useState<string>('');

    const handleRemoveTag = (index: number) => {
        setNotificationsArray((prevState) => prevState.filter((_, i) => i !== index));
    };

    const handleAddTag = () => {
        if (!notification) return;
        setNotificationsArray((prevState) => {
            const newTagsArray = [...prevState, notification];
            setInputData((prevState) => ({
                ...prevState,
                notification_time: newTagsArray,
            }));
            return newTagsArray;
        });
        setNotification('');
    };

    return (
        <div>
            <div className="flex flex-col gap-2">
                <div className="flex gap-4">
                    <Input
                        onChange={(e) => setNotification(e.target.value)}
                        type="text"
                        value={notification}
                        className="border border-neutral-300 rounded-md w-full p-1 text-white"
                        name="tags"
                        label="Уведомления в минутах"
                        placeholder=""
                        crossOrigin=""
                        color='white'
                    />
                    <button
                        onClick={() => handleAddTag()}
                        className="rounded-md px-4 hover:bg-neutral-100 hover:text-black active:bg-neutral-200 active:text-neutral-600 transition-all"
                    >
                        Add
                    </button>
                </div>

                <div className="flex gap-2 flex-wrap">
                    {notificationsArray.map((tag, i) => (
                        <div
                            className="bg-neutral-600 px-2 py-2 text-white font-bold flex justify-center gap-2 rounded-md"
                            key={i}
                        >
                            {tag}
                            <button onClick={() => handleRemoveTag(i)}>
                                <XMarkIcon
                                    className="text-white w-4 h-4
                                            hover:bg-neutral-800 rounded-md transition-all
                                            active:bg-neutral-300 active:text-black"
                                />
                            </button>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default NotificationsInput;
