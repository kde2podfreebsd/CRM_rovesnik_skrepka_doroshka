import { useAppSelector } from "../../app/hooks/redux";
import { afishaURL, apiEndpoint, pageDomain, terminalId } from "../../shared/constants"
import { BarId, EventId, GuestInviteForm, TEvent, TPurchaseFreeTicketResponse, TPurchaseTicketResponse, TTicket, UID } from "../../shared/types"
import { createTransaction, increaseLoaltyByCost, initPayment } from "../acquiring/api";
import { selectEventById, selectEvents } from "../event/eventSlice";
import { fetchUserTicketsByUID } from "../user/api";

type TPurchaseFreeTickets = (eventId: EventId, uid: UID, friends?: GuestInviteForm[]) => Promise<TPurchaseFreeTicketResponse>;
export const purchaseFreeTickets: TPurchaseFreeTickets = (eventId, uid, friends) => {
    const validFriends = friends && friends.length > 0 && friends[0].name !== 'Ваше имя' ? friends : [];
    return fetch(`${apiEndpoint}/ticket/purchase_free`, {
        headers: {
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({
            event_id: eventId,
            client_chat_id: uid,
            friends: validFriends.length > 0 ? validFriends : null
        })
    }).then(res => res.json());
}


type TPurchaseTicket = (uid: UID, shouldBuyWithBonuses: boolean, eventData: TEvent) => Promise<TPurchaseTicketResponse>;
export const purchaseTicket: TPurchaseTicket = async (uid, shouldBuyWithBonuses, eventData) => {
    const {bar_id, event_id, price, event_type, short_name} = eventData;

    if (shouldBuyWithBonuses) {
        return fetch(`${apiEndpoint}/ticket/purchase_by_bonus_points`, {
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST',
            body: JSON.stringify({
                client_chat_id: uid,
                bar_id,
                event_id,
                amount: price,
            })
        }).then(res => res.json());
    }

    const paymentResponseData = await initPayment({
        TerminalKey: terminalId,
        Amount: price * 100,
        DATA: {},
        Description: `Покупка билета на мероприятие ${short_name}`,
        OrderId: Number(`${uid}${event_id}${(''+Date.now()).slice(0, 10) + (Math.random() * 100)}`),
        SuccessURL: `${afishaURL}?successEventId=${event_id}&barId=${bar_id}&amount=${price}&eventType=${event_type}`,
        FailURL: `${afishaURL}?failEventId=${event_id}&barId=${bar_id}&eventType=${event_type}`
    });

    return paymentResponseData
}

type TAddNewTicketForUser = (eventId: number, uid: UID) => Promise<TPurchaseTicketResponse>;
export const addNewTicketForUser: TAddNewTicketForUser = (eventId, uid) => {
    return fetch(`${apiEndpoint}/ticket/purchase`, {
        headers: {
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({
            event_id: eventId,
            client_chat_id: uid,
        })
    }).then(res => res.json());
}

type TUpdateTicket = (eventId: EventId, uid: UID, friends?: GuestInviteForm[]) => Promise<TPurchaseTicketResponse>;
export const updateTicket: TUpdateTicket = async (eventId, uid, friends) => {
    const id = (await fetchUserTicketsByUID(uid)).filter(({event_id}) => event_id === eventId)[0].id;

    return fetch(`${apiEndpoint}/ticket/update`, {
        headers: {
            'Content-Type': 'application/json'
        },
        method: 'PATCH',
        body: JSON.stringify({
            id,
            event_id: eventId,
            client_chat_id: uid,
            ...(friends && {friends})
        })
    }).then(res => res.json());
}

type TFetchTicketById = (ticketId: number) => Promise<any>;
export const fetchTicketById: TFetchTicketById = (ticketId) => {
    return fetch(`${apiEndpoint}/ticket_by_id/${ticketId}`, {
        method: 'GET',
    }).then(res => res.json());
}

type TFetchQrImg = (path: string) => Promise<any>
export const fetchQrImg: TFetchQrImg = (path) => {
    return fetch(`${apiEndpoint}/file/download/?path_to_file=${path}`).then(res => res.blob());
}