export default interface ITicket {
    id: number;
    client_chat_id: number;
    qr_path: string;
    activation_status: boolean;
    friends: IFriend[]
    hashcode: string;
    event_id: number;
}

interface IFriend {
    name: string
    username: string
}