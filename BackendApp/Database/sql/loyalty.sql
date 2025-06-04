select
    l.cashback_percentage,
    l.discount_percentage,
    l."id",
    l.level_name,
    l.loyalty_id,
    l.required_money_spend
from
    loyalty l;

insert into loyalty (
    cashback_percentage,
    level_name,
    loyalty_id,
    required_money_spend,
    discount_percentage)
values (
    0,
    'loyalty_init_level',
    1,
    0.00,
    0)
;