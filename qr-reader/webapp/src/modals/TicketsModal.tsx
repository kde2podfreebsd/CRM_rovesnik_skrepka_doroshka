import { useQrCodeContext } from "../QrReader.tsx";
import { useEffect, useState } from "react";
import { api_url } from "../App.tsx";
import ITicket from "../ types/ITicket.ts";
import IEvent from "../ types/IEvent.ts";
import axios from "axios";
import './loader.css'
import IUser from "../ types/IUser.ts";
import GoBackToScanButton from "../components/GoBackToScanButton.tsx";
import {useNavigate} from "react-router-dom";

const isDev = false

const TicketsModal = () => {
    const navigate = useNavigate();
    const { qrCodeData } = useQrCodeContext();
    const hashCodeToSend = isDev ? "202744f409f166cc61c973438d766ce5e38afabbce9cfb44133be35c77b285e5" : qrCodeData;

    const [ticket, setTicket] = useState<ITicket | null>(null);
    const [event, setEvent] = useState<IEvent | null>(null);
    const [isActivated, setIsActivated] = useState(ticket?.activation_status);
    const [userData, setUserData] = useState<IUser | null>(null);

    useEffect(() => {
        const fetchTicketAndEvent = async () => {
            try {
                const ticketRes = await axios.get(api_url + "/ticket/hash/" + hashCodeToSend);
                setTicket(ticketRes.data.message);
                console.log(ticketRes.data);
                setIsActivated(ticketRes.data.message.activation_status);
                
                const userRes = await axios.get(api_url + "/client/" + ticketRes.data.message.client_chat_id);
                setUserData(userRes.data);

                const eventRes = await axios.get(api_url + "/event/" + ticketRes.data.message.event_id);
                setEvent(eventRes.data);
                console.log();
                
            } catch (error) {
                console.error("Error fetching data:", error);
            }
        };

        fetchTicketAndEvent();
    }, []);

    if (!ticket || !event) {
        return <div className="w-full h-screen justify-center items-center flex"><div className='loader'></div></div>;
    }


    const handleActivate = async () => {
        setIsActivated(false)
        if (!isActivated) {
            try {
                const activateRes = await axios.patch(`${api_url}/ticket/activate?hashcode=${hashCodeToSend}`);
                console.log(activateRes.data);
                
                setIsActivated(true);
            } catch (error) {
                console.error("Error fetching data:", error);
            } finally {
                navigate('/')
            }

        }
    }

    return (
        <div className="flex justify-center items-center flex-col gap-8 pb-8">
            <div className="bg-opacity-80 p-8 rounded-lg flex flex-col justify-start items-start w-full bg-white gap-2">
                <p className='font-bold text-2xl'>Билет номер {ticket.id}</p>
                <p className='font-semibold text-xl'>{userData?.first_name} {userData?.last_name}</p>
                <div className='w-full'><div className='w-11/12 bg-neutral-200 h-[1px]'></div></div>
                <p className='text-xl'><span className='font-bold'>Друзья:</span> { ticket.friends! ? null :  <span>Пусто</span>}</p>
                {ticket.friends?.map((friend, index) => (
                    <p key={index} className='text-lg font-semibold ml-4'>{friend.name}</p>
                ))}
                <div className='flex flex-col gap-2 w-ful'>
                    <button onClick={() => handleActivate()}
                            className={`bg-blue-500 ${isActivated ? '' : 'hover:bg-blue-700'} text-white font-bold py-2 px-4 rounded ${isActivated ? 'opacity-50' : ''}`}>
                        {isActivated ? 'Активирован' : 'Активировать'}
                    </button>
                    <GoBackToScanButton/>
                </div>
            </div>
            <div className="bg-white rounded-lg overflow-hidden shadow-lg w-4/5">
                <img
                    src={event.img_path}
                    alt=""
                    className="object-cover w-full h-2/3 rounded-t-md"
                />
                <div className="p-4">
                <h2 className="text-xl font-semibold mb-2">{event.short_name}</h2>
                    <p className="text-md ">{event.description}</p>
                    <p className="text-md"><span className='font-semibold'>Возрастное ограничение:</span> {event.age_restriction}+</p>
                    <p className="text-md"><span className='font-semibold'>Дата:</span> {event.datetime}</p>
                    <p className="text-md"><span className='font-semibold'>где:</span> {event.place}</p>
                </div>
            </div>
        </div>
    );
};

export default TicketsModal;
