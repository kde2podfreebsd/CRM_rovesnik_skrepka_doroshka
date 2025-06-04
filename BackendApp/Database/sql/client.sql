insert into client (
    "id",
    chat_id,
    first_name,
    last_name,
    loyalty_id,
    username)
values (
    :id,
    :chat_id,
    :first_name,
    :last_name,
    :loyalty_id,
    :username)
;

select
    c.chat_id,
    c.first_name,
    c."id",
    c.last_name,
    c.loyalty_id,
    c.username
from
    client c;