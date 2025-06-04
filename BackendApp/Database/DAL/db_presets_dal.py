from BackendApp.Database.Models.transaction_model import Transaction
from BackendApp.Middleware.transaction_middleware import TX_TYPES
from BackendApp.Database.Models.bar_model import Bar
from BackendApp.Database.Models.client_model import Client
from BackendApp.Database.Models.client_log_model import ClientActionLog
from BackendApp.Database.Models.event_model import Event
from BackendApp.Middleware.event_middleware import EVENT_TYPE
from BackendApp.Database.Models.ticket_model import Ticket
from BackendApp.Database.Models.review_model import Review
from BackendApp.Database.Models.reservation_model import Reservation
from BackendApp.Database.Models.referrals_model import Referral
from BackendApp.Database.Models.table_model import Table

from BackendApp.IIKO.api import Client as ClientIIKO
from BackendApp.Database.session import async_session
from datetime import datetime, timedelta
from sqlalchemy import select
from typing import List
from dotenv import load_dotenv
import asyncio
import os

API_LOGIN = os.getenv("API_LOGIN")

class PresetN1:
    """
    Preset for finding Clients, who has spent over :param amount:, with specific :param bar_id:
    Args:
        bar_id: bar id
        amount: sum a client has spent in the bar with the bar_id
    Returns:
        list of suitable clients 
    """
    @staticmethod
    async def preset_enabled(bar_id=1, amount=500) -> list:
        async with async_session() as session:
            query = await session.execute(
                select(Client).join(Transaction, Client.chat_id == Transaction.client_chat_id).filter(
                    Transaction.bar_id == bar_id, Transaction.amount >= amount
                )
            )
            clients = query.scalars().all()
            return clients

class ActiveForOneDayFilter:

    @staticmethod
    async def preset_enabled(days=1) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            for client in clients:
                logs = await session.execute(select(ClientActionLog.created_at).where(ClientActionLog.client_chat_id == client.chat_id))
                logs = sorted(logs.scalars().all())
                now = datetime.now() + timedelta(hours=3)
                if (now - logs[-1] <= timedelta(days=days) and now > logs[-1]):
                    suitable.append(client)
            return suitable

class InactiveForOneDayFilter:

    @staticmethod
    async def preset_enabled(days=1) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            for client in clients:
                logs = await session.execute(select(ClientActionLog.created_at).where(ClientActionLog.client_chat_id == client.chat_id))
                logs = sorted(logs.scalars().all())
                now = datetime.now() + timedelta(hours=3)
                if (now - logs[-1] > timedelta(days=days) and now > logs[-1]):
                    suitable.append(client)
            return suitable
        
class HighSessionActivityFilter:

    @staticmethod
    async def preset_enabled(gap=1, sessions_amount=10) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            for client in clients:
                logs = await session.execute(select(ClientActionLog.created_at).where(ClientActionLog.client_chat_id == client.chat_id))
                logs = sorted(logs.scalars().all())

                for index in range(1, len(logs)):
                    session_cntr = 0
                    if (logs[index] - logs[index - 1] >= timedelta(hours=gap)):
                        session_cntr += 1

                    if (sessions_amount <= session_cntr):
                        suitable.append(client)

            return suitable

class LowSessionActivityFilter:

    @staticmethod
    async def preset_enabled(gap=1, sessions_amount=10) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            for client in clients:
                logs = await session.execute(select(ClientActionLog.created_at).where(ClientActionLog.client_chat_id == client.chat_id))
                logs = sorted(logs.scalars().all())

                for index in range(1, len(logs)):
                    session_cntr = 0
                    if (logs[index] - logs[index - 1] >= timedelta(hours=gap)):
                        session_cntr += 1

                    if (sessions_amount > session_cntr):
                        suitable.append(client)

            return suitable

class RovesnikPreferenceFilter:

    @staticmethod
    async def preset_enabled() -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            for client in clients:
                logs = await session.execute(select(ClientActionLog.action).where(ClientActionLog.client_chat_id == client.chat_id))
                logs = sorted(logs.scalars().all())

                rovesnik_menu_handler = "Rovesnik.Handlers.menu_handler.send_menu"
                skrepka_menu_handler = "Skrepka.Handlers.menu_handler.send_menu"
                doroshka_menu_handler = "Doroshka.Handlers.menu_handler.send_menu"
                r_freq = 0
                s_freq = 0
                d_freq = 0

                for log in logs:
                    if (rovesnik_menu_handler in log):
                        r_freq += 1
                    if (skrepka_menu_handler in log):
                        s_freq += 1
                    if (doroshka_menu_handler in log):
                        d_freq += 1
                
                if (r_freq > s_freq and r_freq > d_freq):
                    suitable.append(client)

            return suitable

class SkrepkaPreferenceFilter:

    @staticmethod
    async def preset_enabled() -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            for client in clients:
                logs = await session.execute(select(ClientActionLog.action).where(ClientActionLog.client_chat_id == client.chat_id))
                logs = sorted(logs.scalars().all())

                rovesnik_menu_handler = "Rovesnik.Handlers.menu_handler.send_menu"
                skrepka_menu_handler = "Skrepka.Handlers.menu_handler.send_menu"
                doroshka_menu_handler = "Doroshka.Handlers.menu_handler.send_menu"
                r_freq = 0
                s_freq = 0
                d_freq = 0

                for log in logs:
                    if (rovesnik_menu_handler in log):
                        r_freq += 1
                    if (skrepka_menu_handler in log):
                        s_freq += 1
                    if (doroshka_menu_handler in log):
                        d_freq += 1
                
                if (s_freq > r_freq and s_freq > d_freq):
                    suitable.append(client)

            return suitable

class DoroshkaPreferenceFilter:

    @staticmethod
    async def preset_enabled() -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            for client in clients:
                logs = await session.execute(select(ClientActionLog.action).where(ClientActionLog.client_chat_id == client.chat_id))
                logs = sorted(logs.scalars().all())

                rovesnik_menu_handler = "Rovesnik.Handlers.menu_handler.send_menu"
                skrepka_menu_handler = "Skrepka.Handlers.menu_handler.send_menu"
                doroshka_menu_handler = "Doroshka.Handlers.menu_handler.send_menu"
                r_freq = 0
                s_freq = 0
                d_freq = 0

                for log in logs:
                    if (rovesnik_menu_handler in log):
                        r_freq += 1
                    if (skrepka_menu_handler in log):
                        s_freq += 1
                    if (doroshka_menu_handler in log):
                        d_freq += 1
                
                if (d_freq > s_freq and d_freq > r_freq):
                    suitable.append(client)

            return suitable

class TicketAmountGreaterFilter:

    @staticmethod
    async def preset_enabled(amount=5) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            for client in clients:
                tickets = await session.execute(select(Ticket).where(Ticket.client_chat_id == client.chat_id))
                tickets = tickets.scalars().all()

                if (len(tickets) >= amount):
                    suitable.append(client)

            return suitable

class TicketAmountLessFilter:

    @staticmethod
    async def preset_enabled(amount=5) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            for client in clients:
                tickets = await session.execute(select(Ticket).where(Ticket.client_chat_id == client.chat_id))
                tickets = tickets.scalars().all()

                if (len(tickets) < amount):
                    suitable.append(client)
                    
            return suitable

class FreeEventPreferenceFilter:

    @staticmethod
    async def preset_enabled() -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            for client in clients:
                tickets = await session.execute(select(Ticket.event_id).where(
                    Ticket.client_chat_id == client.chat_id,
                    Ticket.activation_status == True
                ))
                ids = tickets.scalars().all()

                free_cntr = 0
                deposit_cntr = 0
                event_cntr = 0    

                for id in ids:
                    event = await session.execute(select(Event).where(Event.id == id))
                    event = event.scalars().first()

                    if (event.event_type == EVENT_TYPE.FREE):
                        free_cntr += 1
                    if (event.event_type == EVENT_TYPE.DEPOSIT):
                        deposit_cntr += 1
                    if (event.event_type == EVENT_TYPE.EVENT):
                        event_cntr += 1
                
                if (free_cntr > deposit_cntr and free_cntr > event_cntr):
                    suitable.append(client)
                    
            return suitable

class DepositEventPreferenceFilter:

    @staticmethod
    async def preset_enabled() -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            for client in clients:
                tickets = await session.execute(select(Ticket.event_id).where(
                    Ticket.client_chat_id == client.chat_id,
                    Ticket.activation_status == True
                ))
                ids = tickets.scalars().all()

                free_cntr = 0
                deposit_cntr = 0
                event_cntr = 0    

                for id in ids:
                    event = await session.execute(select(Event).where(Event.id == id))
                    event = event.scalars().first()

                    if (event.event_type == EVENT_TYPE.FREE):
                        free_cntr += 1
                    if (event.event_type == EVENT_TYPE.DEPOSIT):
                        deposit_cntr += 1
                    if (event.event_type == EVENT_TYPE.EVENT):
                        event_cntr += 1
                
                if (deposit_cntr > free_cntr and deposit_cntr > event_cntr):
                    suitable.append(client)
                    
            return suitable

class EventPreferenceFilter:

    @staticmethod
    async def preset_enabled() -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            for client in clients:
                tickets = await session.execute(select(Ticket.event_id).where(
                    Ticket.client_chat_id == client.chat_id,
                    Ticket.activation_status == True
                ))
                ids = tickets.scalars().all()

                free_cntr = 0
                deposit_cntr = 0
                event_cntr = 0    

                for id in ids:
                    event = await session.execute(select(Event).where(Event.id == id))
                    event = event.scalars().first()

                    if (event.event_type == EVENT_TYPE.FREE):
                        free_cntr += 1
                    if (event.event_type == EVENT_TYPE.DEPOSIT):
                        deposit_cntr += 1
                    if (event.event_type == EVENT_TYPE.EVENT):
                        event_cntr += 1
                
                if (event_cntr > deposit_cntr and event_cntr > free_cntr):
                    suitable.append(client)
                    
            return suitable

class ReviewAmountLessFilter:

    @staticmethod
    async def preset_enabled(amount=5) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            for client in clients:
                reviews = await session.execute(select(Review).where(Review.chat_id == client.chat_id))
                reviews = reviews.scalars().all()

                if (len(reviews) < amount):
                    suitable.append(client)
                    
            return suitable

class ReviewAmountGreaterFilter:

    @staticmethod
    async def preset_enabled(amount=5) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            for client in clients:
                reviews = await session.execute(select(Review).where(Review.chat_id == client.chat_id))
                reviews = reviews.scalars().all()

                if (len(reviews) >= amount):
                    suitable.append(client)
                    
            return suitable

class ReservationRovesnikFilter:

    @staticmethod
    async def preset_enabled(amount=5, bar_id=1) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            for client in clients:
                booked_table_uuids = await session.execute(select(Reservation.table_uuid).where(Reservation.client_chat_id == client.chat_id))
                booked_table_uuids = booked_table_uuids.scalars().all()
                reservations_cntr = 0

                for table_uuid in booked_table_uuids:
                    table = await session.execute(select(Table).where(Table.table_uuid == table_uuid))
                    table = table.scalars().first()
                    if (table.bar_id == bar_id):
                        reservations_cntr += 1

                if (reservations_cntr >= amount):
                    suitable.append(client)
                    
            return suitable

class ReservationSkrepkaFilter:

    @staticmethod
    async def preset_enabled(amount=5, bar_id=2) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            for client in clients:
                booked_table_uuids = await session.execute(select(Reservation.table_uuid).where(Reservation.client_chat_id == client.chat_id))
                booked_table_uuids = booked_table_uuids.scalars().all()
                reservations_cntr = 0

                for table_uuid in booked_table_uuids:
                    table = await session.execute(select(Table).where(Table.table_uuid == table_uuid))
                    table = table.scalars().first()
                    if (table.bar_id == bar_id):
                        reservations_cntr += 1

                if (reservations_cntr >= amount):
                    suitable.append(client)
                    
            return suitable

class ReservationDoroshkaFilter:

    @staticmethod
    async def preset_enabled(amount=5, bar_id=3) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            for client in clients:
                booked_table_uuids = await session.execute(select(Reservation.table_uuid).where(Reservation.client_chat_id == client.chat_id))
                booked_table_uuids = booked_table_uuids.scalars().all()
                reservations_cntr = 0

                for table_uuid in booked_table_uuids:
                    table = await session.execute(select(Table).where(Table.table_uuid == table_uuid))
                    table = table.scalars().first()
                    if (table.bar_id == bar_id):
                        reservations_cntr += 1

                if (reservations_cntr >= amount):
                    suitable.append(client)
                    
            return suitable

class IncreaseBalanceTransactionAmountFilter:

    @staticmethod
    async def preset_enabled(amount=5) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            for client in clients:
                txs = await session.execute(select(Transaction).where(Transaction.tx_type == TX_TYPES.INCREASE_BALANCE))
                txs = txs.scalars().all()

                if (len(txs) >= amount):
                    suitable.append(client)
                    
            return suitable

class IncreaseBalanceSumFilter:

    @staticmethod
    async def preset_enabled(amount=5000) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            for client in clients:
                txs = await session.execute(select(Transaction.final_amount).where(Transaction.tx_type == TX_TYPES.INCREASE_BALANCE))
                total_sum = sum([int(sum) for sum in txs.scalars().all()])

                if (total_sum >= amount):
                    suitable.append(client)
                    
            return suitable

class ReduceBalanceTransactionAmountFilter:

    @staticmethod
    async def preset_enabled(amount=5) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            for client in clients:
                txs = await session.execute(select(Transaction).where(Transaction.tx_type == TX_TYPES.REDUCE_BALANCE))
                txs = txs.scalars().all()

                if (len(txs) >= amount):
                    suitable.append(client)
                    
            return suitable

class ReduceBalanceSumFilter:

    @staticmethod
    async def preset_enabled(amount=5000) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            for client in clients:
                txs = await session.execute(select(Transaction.final_amount).where(Transaction.tx_type == TX_TYPES.REDUCE_BALANCE))
                total_sum = sum([int(sum) for sum in txs.scalars().all()])

                if (total_sum >= amount):
                    suitable.append(client)
                    
            return suitable

class ProfileBalanceGreaterFilter:

    @staticmethod
    async def preset_enabled(amount=5000) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            client_iiko = await ClientIIKO.create(API_LOGIN, "Rovesnik")
            for client in clients:
                iiko_user = await client_iiko.get_customer_info(id=client.iiko_id)
                balance = iiko_user.walletBalances[0]["balance"]
                if (balance >= amount):
                    suitable.append(client)
                    
            return suitable

class ProfileBalanceLessFilter:

    @staticmethod
    async def preset_enabled(amount=5000) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            client_iiko = await ClientIIKO.create(API_LOGIN, "Rovesnik")
            for client in clients:
                iiko_user = await client_iiko.get_customer_info(id=client.iiko_id)
                balance = iiko_user.walletBalances[0]["balance"]
                if (balance < amount):
                    suitable.append(client)
                    
            return suitable

class IsReferralFilter:

    @staticmethod
    async def preset_enabled() -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            referrers = await session.execute(select(Referral))
            referrers = referrers.scalars().all()

            suitable = []
            for client in clients:
                for referrer in referrers:
                    if (referrer.referral_link == client.referral_link):
                        suitable.append(client)
                        break
                    
            return suitable

class ReferralAmountGreaterFilter:

    @staticmethod
    async def preset_enabled(amount=5) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            referrers = await session.execute(select(Referral))
            referrers = referrers.scalars().all()

            suitable = []
            for client in clients:
                ref_cntr = 0
                for referrer in referrers:
                    if (referrer.referral_link == client.referral_link):
                        ref_cntr += 1
                
                if (ref_cntr >= amount):
                    suitable.append(client)
                    
            return suitable

class ReferralAmountLessFilter:

    @staticmethod
    async def preset_enabled(amount=5) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            referrers = await session.execute(select(Referral))
            referrers = referrers.scalars().all()

            suitable = []
            for client in clients:
                ref_cntr = 0
                for referrer in referrers:
                    if (referrer.referral_link == client.referral_link):
                        ref_cntr += 1
                
                if (ref_cntr < amount):
                    suitable.append(client)
                    
            return suitable

class Level1Filter:

    @staticmethod
    async def preset_enabled() -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client).where(
                Client.spent_amount < 5000
            ))
            clients = clients.scalars().all()
                    
            return clients

class Level2Filter:

    @staticmethod
    async def preset_enabled() -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client).where(
                Client.spent_amount >= 5000,
                Client.spent_amount < 15000
            ))
            clients = clients.scalars().all()
                    
            return clients

class Level3Filter:

    @staticmethod
    async def preset_enabled() -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client).where(
                Client.spent_amount >= 15000,
                Client.spent_amount < 50000
            ))
            clients = clients.scalars().all()
                    
            return clients

class Level4Filter:

    @staticmethod
    async def preset_enabled() -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client).where(
                Client.spent_amount >= 50000,
                Client.spent_amount < 100000
            ))
            clients = clients.scalars().all()
                    
            return clients

class Level5Filter:

    @staticmethod
    async def preset_enabled() -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client).where(
                Client.spent_amount >= 100000,
                Client.spent_amount < 250000
            ))
            clients = clients.scalars().all()
                    
            return clients

class Level6Filter:

    @staticmethod
    async def preset_enabled() -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client).where(Client.spent_amount >= 250000))
            clients = clients.scalars().all()
                    
            return clients

class RegistrationDateFilter:

    @staticmethod
    async def preset_enabled(start_date=datetime(2024, 5, 25, 0, 0, 0)) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()
            suitable = []

            for client in clients:
                logs = await session.execute(select(ClientActionLog.created_at).where(ClientActionLog.client_chat_id == client.chat_id))
                registration_date = sorted(logs.scalars().all())[-1]
                if (registration_date >= start_date):
                    suitable.append(client)

class MorningFilter:

    @staticmethod
    async def preset_enabled(gap=1) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()
            suitable = []

            for client in clients:
                logs = await session.execute(select(ClientActionLog.created_at).where(ClientActionLog.client_chat_id == client.chat_id))
                logs = logs.scalars().all()

                morning_sessions = 0
                morning_logs = []
                afternoon_sessions = 0
                afternoon_logs = []
                evening_sessions = 0
                evening_logs = []
                night_sessions = 0
                night_logs = []

                for log in logs:
                    if (
                        log >= datetime(log.year, log.month, log.day, 6, 0, 0) and 
                        log <= datetime(log.year, log.month, log.day, 12, 0, 0)
                    ):
                        morning_logs.append(log)
                morning_logs = sorted(morning_logs)

                for index in range(1, len(morning_logs)):
                    if (morning_logs[index] - morning_logs[index - 1] >= timedelta(hours=gap)):
                        morning_sessions += 1

                for log in logs:
                    if (
                        log >= datetime(log.year, log.month, log.day, 12, 0, 0) and 
                        log <= datetime(log.year, log.month, log.day, 18, 0, 0)
                    ):
                        afternoon_logs.append(log)
                afternoon_logs = sorted(afternoon_logs)

                for index in range(1, len(afternoon_logs)):
                    if (afternoon_logs[index] - afternoon_logs[index - 1] >= timedelta(hours=gap)):
                        afternoon_sessions += 1
                
                for log in logs:
                    if (
                        log >= datetime(log.year, log.month, log.day, 18, 0, 0) and 
                        log <= datetime(log.year, log.month, log.day, 22, 0, 0)
                    ):
                        evening_logs.append(log)
                evening_logs = sorted(evening_logs)

                for index in range(1, len(evening_logs)):
                    if (evening_logs[index] - evening_logs[index - 1] >= timedelta(hours=gap)):
                        evening_sessions += 1

                for log in logs:

                    the_following_day = None
                    one_day = timedelta(days=1)
                    if ((log + one_day).month != log.month):
                        the_following_day = datetime(log.year, log.month + 1, 1, 6, 0, 0)
                    else:
                        the_following_day = datetime(log.year, log.month, log.day + 1, 6, 0, 0)

                    if (
                        log >= datetime(log.year, log.month, log.day, 22, 0, 0) and 
                        log <= the_following_day
                    ):
                        night_logs.append(log)
                night_logs = sorted(night_logs)

                for index in range(1, len(night_logs)):
                    if (night_logs[index] - night_logs[index - 1] >= timedelta(hours=gap)):
                        night_sessions += 1
                
                if (
                    morning_sessions >= afternoon_sessions and 
                    morning_sessions >= evening_sessions and
                    morning_sessions >= night_sessions
                ):
                    suitable.append(client)

        return suitable

class AfternoonFilter:

    @staticmethod
    async def preset_enabled(gap=1) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()
            suitable = []

            for client in clients:
                logs = await session.execute(select(ClientActionLog.created_at).where(ClientActionLog.client_chat_id == client.chat_id))
                logs = logs.scalars().all()

                morning_sessions = 0
                morning_logs = []
                afternoon_sessions = 0
                afternoon_logs = []
                evening_sessions = 0
                evening_logs = []
                night_sessions = 0
                night_logs = []

                for log in logs:
                    if (
                        log >= datetime(log.year, log.month, log.day, 6, 0, 0) and 
                        log <= datetime(log.year, log.month, log.day, 12, 0, 0)
                    ):
                        morning_logs.append(log)
                morning_logs = sorted(morning_logs)

                for index in range(1, len(morning_logs)):
                    if (morning_logs[index] - morning_logs[index - 1] >= timedelta(hours=gap)):
                        morning_sessions += 1

                for log in logs:
                    if (
                        log >= datetime(log.year, log.month, log.day, 12, 0, 0) and 
                        log <= datetime(log.year, log.month, log.day, 18, 0, 0)
                    ):
                        afternoon_logs.append(log)
                afternoon_logs = sorted(afternoon_logs)

                for index in range(1, len(afternoon_logs)):
                    if (afternoon_logs[index] - afternoon_logs[index - 1] >= timedelta(hours=gap)):
                        afternoon_sessions += 1
                
                for log in logs:
                    if (
                        log >= datetime(log.year, log.month, log.day, 18, 0, 0) and 
                        log <= datetime(log.year, log.month, log.day, 22, 0, 0)
                    ):
                        evening_logs.append(log)
                evening_logs = sorted(evening_logs)

                for index in range(1, len(evening_logs)):
                    if (evening_logs[index] - evening_logs[index - 1] >= timedelta(hours=gap)):
                        evening_sessions += 1

                for log in logs:

                    the_following_day = None
                    one_day = timedelta(days=1)
                    if ((log + one_day).month != log.month):
                        the_following_day = datetime(log.year, log.month + 1, 1, 6, 0, 0)
                    else:
                        the_following_day = datetime(log.year, log.month, log.day + 1, 6, 0, 0)

                    if (
                        log >= datetime(log.year, log.month, log.day, 22, 0, 0) and 
                        log <= the_following_day
                    ):
                        night_logs.append(log)
                night_logs = sorted(night_logs)

                for index in range(1, len(night_logs)):
                    if (night_logs[index] - night_logs[index - 1] >= timedelta(hours=gap)):
                        night_sessions += 1
                
                if (
                    afternoon_sessions >= morning_sessions and 
                    afternoon_sessions >= evening_sessions and
                    afternoon_sessions >= night_sessions
                ):
                    suitable.append(client)
                    
        return suitable
     
class EveningFilter:

    @staticmethod
    async def preset_enabled(gap=1) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()
            suitable = []

            for client in clients:
                logs = await session.execute(select(ClientActionLog.created_at).where(ClientActionLog.client_chat_id == client.chat_id))
                logs = logs.scalars().all()

                morning_sessions = 0
                morning_logs = []
                afternoon_sessions = 0
                afternoon_logs = []
                evening_sessions = 0
                evening_logs = []
                night_sessions = 0
                night_logs = []

                for log in logs:
                    if (
                        log >= datetime(log.year, log.month, log.day, 6, 0, 0) and 
                        log <= datetime(log.year, log.month, log.day, 12, 0, 0)
                    ):
                        morning_logs.append(log)
                morning_logs = sorted(morning_logs)

                for index in range(1, len(morning_logs)):
                    if (morning_logs[index] - morning_logs[index - 1] >= timedelta(hours=gap)):
                        morning_sessions += 1

                for log in logs:
                    if (
                        log >= datetime(log.year, log.month, log.day, 12, 0, 0) and 
                        log <= datetime(log.year, log.month, log.day, 18, 0, 0)
                    ):
                        afternoon_logs.append(log)
                afternoon_logs = sorted(afternoon_logs)

                for index in range(1, len(afternoon_logs)):
                    if (afternoon_logs[index] - afternoon_logs[index - 1] >= timedelta(hours=gap)):
                        afternoon_sessions += 1
                
                for log in logs:
                    if (
                        log >= datetime(log.year, log.month, log.day, 18, 0, 0) and 
                        log <= datetime(log.year, log.month, log.day, 22, 0, 0)
                    ):
                        evening_logs.append(log)
                evening_logs = sorted(evening_logs)

                for index in range(1, len(evening_logs)):
                    if (evening_logs[index] - evening_logs[index - 1] >= timedelta(hours=gap)):
                        evening_sessions += 1

                for log in logs:

                    the_following_day = None
                    one_day = timedelta(days=1)
                    if ((log + one_day).month != log.month):
                        the_following_day = datetime(log.year, log.month + 1, 1, 6, 0, 0)
                    else:
                        the_following_day = datetime(log.year, log.month, log.day + 1, 6, 0, 0)

                    if (
                        log >= datetime(log.year, log.month, log.day, 22, 0, 0) and 
                        log <= the_following_day
                    ):
                        night_logs.append(log)
                night_logs = sorted(night_logs)

                for index in range(1, len(night_logs)):
                    if (night_logs[index] - night_logs[index - 1] >= timedelta(hours=gap)):
                        night_sessions += 1
                
                if (
                    evening_sessions >= morning_sessions and 
                    evening_sessions >= afternoon_sessions and
                    evening_sessions >= night_sessions
                ):
                    suitable.append(client)
                    
        return suitable     

class NightFilter:

    @staticmethod
    async def preset_enabled(gap=1) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()
            suitable = []

            for client in clients:
                logs = await session.execute(select(ClientActionLog.created_at).where(ClientActionLog.client_chat_id == client.chat_id))
                logs = logs.scalars().all()

                morning_sessions = 0
                morning_logs = []
                afternoon_sessions = 0
                afternoon_logs = []
                evening_sessions = 0
                evening_logs = []
                night_sessions = 0
                night_logs = []

                for log in logs:
                    if (
                        log >= datetime(log.year, log.month, log.day, 6, 0, 0) and 
                        log <= datetime(log.year, log.month, log.day, 12, 0, 0)
                    ):
                        morning_logs.append(log)
                morning_logs = sorted(morning_logs)

                for index in range(1, len(morning_logs)):
                    if (morning_logs[index] - morning_logs[index - 1] >= timedelta(hours=gap)):
                        morning_sessions += 1

                for log in logs:
                    if (
                        log >= datetime(log.year, log.month, log.day, 12, 0, 0) and 
                        log <= datetime(log.year, log.month, log.day, 18, 0, 0)
                    ):
                        afternoon_logs.append(log)
                afternoon_logs = sorted(afternoon_logs)

                for index in range(1, len(afternoon_logs)):
                    if (afternoon_logs[index] - afternoon_logs[index - 1] >= timedelta(hours=gap)):
                        afternoon_sessions += 1
                
                for log in logs:
                    if (
                        log >= datetime(log.year, log.month, log.day, 18, 0, 0) and 
                        log <= datetime(log.year, log.month, log.day, 22, 0, 0)
                    ):
                        evening_logs.append(log)
                evening_logs = sorted(evening_logs)

                for index in range(1, len(evening_logs)):
                    if (evening_logs[index] - evening_logs[index - 1] >= timedelta(hours=gap)):
                        evening_sessions += 1

                for log in logs:

                    the_following_day = None
                    one_day = timedelta(days=1)
                    if ((log + one_day).month != log.month):
                        the_following_day = datetime(log.year, log.month + 1, 1, 6, 0, 0)
                    else:
                        the_following_day = datetime(log.year, log.month, log.day + 1, 6, 0, 0)

                    if (
                        log >= datetime(log.year, log.month, log.day, 22, 0, 0) and 
                        log <= the_following_day
                    ):
                        night_logs.append(log)
                night_logs = sorted(night_logs)

                for index in range(1, len(night_logs)):
                    if (night_logs[index] - night_logs[index - 1] >= timedelta(hours=gap)):
                        night_sessions += 1
                
                if (
                    night_sessions >= morning_sessions and 
                    night_sessions >= evening_sessions and
                    night_sessions >= afternoon_sessions
                ):
                    suitable.append(client)
                    
        return suitable    

class RegularCustomerFilter:

    @staticmethod
    async def preset_enabled(gap=1, session_amount=10, spent_amount=10000) -> List:
        async with async_session() as session:
            clients = await session.execute(select(Client))
            clients = clients.scalars().all()

            suitable = []
            for client in clients:
                logs = await session.execute(select(ClientActionLog.created_at).where(ClientActionLog.client_chat_id == client.chat_id))
                logs = logs.scalars().all()

                one_month_activity = False
                two_month_activity = False
                three_month_activity = False
                four_month_activity = False
                five_month_activity = False
                six_month_activity = False
                session_cntr = 0

                for index in range(1, len(logs)):
                    if (logs[index] - logs[index - 1] >= timedelta(hours=gap)):
                        session_cntr += 1
                    now = datetime.now() + timedelta(hours=3)
                    if (now - logs[index] <= timedelta(days=30)):
                        one_month_activity = True
                    if (
                        timedelta(days=30) < now - logs[index] and
                        now - logs[index] <= timedelta(days=60)
                    ):
                        two_month_activity = True
                    if (
                        timedelta(days=60) < now - logs[index] and
                        now - logs[index] <= timedelta(days=90)
                    ):
                        three_month_activity = True
                    if (
                        timedelta(days=90) < now - logs[index] and
                        now - logs[index] <= timedelta(days=120)
                    ):
                        four_month_activity = True
                    if (
                        timedelta(days=120) < now - logs[index] and
                        now - logs[index] <= timedelta(days=150)
                    ):
                        five_month_activity = True
                    if (
                        timedelta(days=120) < now - logs[index] and
                        now - logs[index] <= timedelta(days=180)
                    ):
                        six_month_activity = True
                    
                    if (
                        one_month_activity and 
                        two_month_activity and 
                        three_month_activity and 
                        four_month_activity and 
                        five_month_activity and 
                        six_month_activity
                    ):
                        break
            
                has_spent_over_one_month = False
                has_spent_over_two_months = False
                has_spent_over_three_months = False
                has_spent_over_four_months = False
                has_spent_over_five_months = False
                has_spent_over_six_months = False

                txs = await session.execute(select(Transaction).where(
                    Transaction.client_chat_id == client.chat_id,
                    Transaction.tx_type == TX_TYPES.REDUCE_BALANCE,
                    now - Ticket.activation_time <= timedelta(days=180)
                ))
                txs = txs.scalars().all()

                for tx in txs:
                    now = datetime.now() + timedelta(hours=3)
                    if (now - tx.time_stamp <= timedelta(days=30)):
                        has_spent_over_one_month = True
                    if (
                        timedelta(days=30) < now - tx.time_stamp and
                        now - tx.time_stamp <= timedelta(days=60)
                    ):
                        has_spent_over_two_months = True
                    if (
                        timedelta(days=60) < now - tx.time_stamp and
                        now - tx.time_stamp <= timedelta(days=90)
                    ):
                        has_spent_over_three_months = True
                    if (
                        timedelta(days=90) < now - tx.time_stamp and
                        now - tx.time_stamp <= timedelta(days=120)
                    ):
                        has_spent_over_four_months = True
                    if (
                        timedelta(days=120) < now - tx.time_stamp and
                        now - tx.time_stamp <= timedelta(days=150)
                    ):
                        has_spent_over_five_months = True
                    if (
                        timedelta(days=150) < now - tx.time_stamp and
                        now - tx.time_stamp <= timedelta(days=180)
                    ):
                        has_spent_over_six_months = True

                    if (
                        has_spent_over_one_month and 
                        has_spent_over_two_months and
                        has_spent_over_three_months and
                        has_spent_over_four_months and
                        has_spent_over_five_months and 
                        has_spent_over_six_months
                    ):
                        break

                now = datetime.now() + timedelta(hours=3)     
                tickets = await session.execute(select(Ticket).where(
                    Ticket.client_chat_id == client.chat_id,
                    Ticket.activation_status == True,
                    now - Ticket.activation_time <= timedelta(days=180)
                ))
                tickets = tickets.scalars().all()

                reservations = await session.execute(select(Reservation).where(
                    Reservation.client_chat_id == client.chat_id,
                    now - Ticket.activation_time <= timedelta(days=180)
                ))
                reservations = reservations.scalars().all()

                session_criterion = (
                    (
                        one_month_activity and 
                        two_month_activity and 
                        three_month_activity and 
                        four_month_activity and 
                        five_month_activity and 
                        six_month_activity
                    ) or session_cntr >= session_amount
                )

                tx_criterion = (
                    (
                        has_spent_over_one_month and 
                        has_spent_over_two_months and 
                        has_spent_over_three_months and 
                        has_spent_over_four_months and 
                        has_spent_over_five_months and 
                        has_spent_over_six_months
                    ) or sum([int(tx.final_amount) for tx in txs]) >= spent_amount
                )

                if (session_criterion and tx_criterion and (len(reservations) >= 3 or len(tickets) >= 3)):
                    suitable.append(client)
                    
            return suitable


async def main():
    async with async_session() as session:
        clients = await ActiveForOneDayFilter.preset_enabled()
        for client in clients:
            print(f"Клиент: {client.chat_id}")
            print(f"Имя: {client.first_name} {client.last_name}")

if __name__ == "__main__":
    asyncio.run(main())