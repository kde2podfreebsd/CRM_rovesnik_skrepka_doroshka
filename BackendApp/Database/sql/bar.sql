select
    b.bar_id,
    b.bar_name,
    b."id"
from
    bar b;

insert into bar (
    "id",
    bar_id,
    bar_name)
values (
    :id,
    :bar_id,
    :bar_name)
;

