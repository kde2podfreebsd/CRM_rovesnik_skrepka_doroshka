## Скорее всего я разберуюсь, как сделать одну программу лояльности для всех заведений, 
так что синхронизационный слой не пригодится. 

## обычные методы. 

Главный класс: 
```.py
from BackendApp.IIKO.core import CoreClient
```

Создание клиента:
```.py
client = await CoreCustomer.create(api_login, "Ровесник") Выбор заведения скорее всего потом отойдет.
```

Создание клиента:
```.py
await client.full_create_customer()
```

Пополнить баланс:
```.py
await client.refill_customer_balance(customer_id, user_wallet, 100)
```

Найти user_wallet:
```.py
await client.get_customer_info(id или телефон)
```

Снять деньги с баланса:
```.py
await client.withdraw_balance(customer_id, user_wallet, 40)
```
