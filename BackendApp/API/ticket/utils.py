from BackendApp.API.ticket.schemas import TicketInfo, Friend
import json

def get_ticket_purchasing_info(status: bool):
    if status:
        return {"message": "Ticket purchased successfully"}
    else:
        return {"message": "Ticket already purchased for this user"}
    
def parse_ticket_into_format(ticket):
    friends = None
    
    if ticket.friends is not None:
        friends = [Friend(
            **friend
        ) for friend in json.loads(ticket.friends)]

    return TicketInfo(
        id=ticket.id,
        client_chat_id=ticket.client_chat_id,
        qr_path=ticket.qr_path,
        activation_status=ticket.activation_status,
        hashcode=ticket.hashcode,
        friends=friends,
        event_id=ticket.event_id,
    )
    
def parse_tickets_into_format(tickets):
    return [parse_ticket_into_format(ticket)
            for ticket in tickets]
    

def get_activate_ticket_description():
    return """Если билет уже активирован, то всё-равно вернётся Ticket activated successfully.
Если же такого билета не существует, то будет Ticket actiavtion failed."""