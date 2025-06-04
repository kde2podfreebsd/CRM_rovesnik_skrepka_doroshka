select
    f.answer,
    f."id",
    f.short_name
from
    faq f;

insert into faq (
    "id",
    answer,
    short_name)
values (
    "ответ на вопрос номер 1 о чем то рассказывается",
    "вопрос номер 1")
;

