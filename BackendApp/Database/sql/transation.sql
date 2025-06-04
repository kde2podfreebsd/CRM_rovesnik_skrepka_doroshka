select
    t.amount,
    t.bar_id,
    t.client_chat_id,
    t.final_amount,
    t."id"
from
    "transaction" t;

insert into "transaction" (
    "id",
    amount,
    bar_id,
    client_chat_id,
    final_amount)
values (
    :id,
    :amount,
    :bar_id,
    :client_chat_id,
    :final_amount)
;

