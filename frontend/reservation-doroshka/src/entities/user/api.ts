import { apiEndpoint } from "../../shared/constants"
import { TTicket, UID } from "../../shared/types"

type TFetchUserTickets = (uid?: UID) => Promise<TTicket[]> 
export const fetchUserTicketsByUID: TFetchUserTickets = (uid = 272324534) => {
    return fetch(`${apiEndpoint}/tickets/${uid}`, {
        method: 'GET',
    }).then(res => res.json());
}