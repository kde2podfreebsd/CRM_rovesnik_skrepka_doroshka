import asyncio
import json
import pprint
from dataclasses import asdict
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

import aiohttp
import dacite


base_url = "https://rovesnik-bot.ru"

async def main():
    
    data = {
            "event_id" : 9,
            "client_chat_id" : 406149877,
            "friends" : [
                {"name" : "name1", "username" : "username1"},
                {"name" : "name2", "username" : "username2"}
            ]
        }
    
    param_data = {
        "event_id" : 9,
        "client_chat_id" : 406149871,
    }
    
    json_data = {
        "friends" : [
                {"name" : "name1", "username" : "username1"},
                {"name" : "name2", "username" : "username2"}
            ]
    }
    
    session = aiohttp.ClientSession()
    
    print("Before request")
    
    hashc = '30e2effc349cf1f2cdfb0617192b1f91899b3d28f21f7b3c0651725bafa13e2e'
    ticket_id = 32
    
    data = {
        "hashcode": hashc
    }
    
    data = {
        "event_id" : 9,
        "desctiprion" : "new_description alkajsdl;fkaj;lskdjf"
    }

    try:
        async with session.patch(
            # f"{base_url}/purchase_ticket/", json=param_data
            f"{base_url}/api/event/update/", json=data
        ) as response:
            json_data = await response.json()
            response.raise_for_status()
            
            print(json_data)
            print("AFTER request")
            

    except (aiohttp.ClientError, ValueError) as err:
        pprint.pprint(json_data)
        
    
    if session:
        await session.close()

    
    
if __name__ == "__main__":
    asyncio.run(main())