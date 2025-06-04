import { apiEndpoint } from "../../shared/constants"
import { AcquiringTransaction, BarId, CreateTransactionApiResponse, EventId, TEvent, TIncreaseLoaltyApiResponse, TInitPaymentResponse, UID } from "../../shared/types";
import { fetchEventDataById } from "../event/api";

type TInitPayment = (transaction: AcquiringTransaction) => Promise<TInitPaymentResponse>;
export const initPayment: TInitPayment = (transaction) => {
    return fetch(`${apiEndpoint}/acquiring/init_tx`, {
        headers: {
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify(transaction),
    }).then(res => res.json());
}

type TIncreaseLoaltyByCost = (chatid: UID, amount: number) => Promise<TIncreaseLoaltyApiResponse>
export const increaseLoaltyByCost: TIncreaseLoaltyByCost = (chatid, amount) => {
    return fetch(`${apiEndpoint}/acquiring/handle_spent_money`, {
        headers: {
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({
            spent_amount: amount,
            chat_id: chatid,
        }),
    }).then(res => res.json());
}

type TIncreaseLoyaltyByEventCost = (chatid: UID, eventId: EventId) => Promise<TIncreaseLoaltyApiResponse>
export const increaseLoyaltyByEventCost: TIncreaseLoyaltyByEventCost = async (uid, eventId) => {
    return increaseLoaltyByCost(uid, (await fetchEventDataById(eventId)).price);
}

export const refillUserBalance: TIncreaseLoaltyByCost = (chatid, amount) => {
    return fetch(`${apiEndpoint}/client/refill_balance`, {
        headers: {
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({
            chat_id: chatid,
            amount,
        }),
    }).then(res => res.json());
}

export const increaseBalanceByEventCost: TIncreaseLoyaltyByEventCost = async (uid, eventId) => {
    return refillUserBalance(uid, (await fetchEventDataById(eventId)).price)
}

type TCreateTransaction = (uid: UID, barId: BarId, amount: number, type: 'reduce_balance' | 'increase_balance') =>
    Promise<CreateTransactionApiResponse>
export const createTransaction: TCreateTransaction = (uid, barId, amount, type) => {
    return fetch(`${apiEndpoint}/transaction/create`, {
        headers: {
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({
            bar_id: barId,
            amount,
            final_amount: amount,
            tx_type: type,
            client_chat_id: uid,
        }),
    }).then(res => res.json());
}