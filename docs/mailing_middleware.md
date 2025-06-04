# Mailing

```../Middleware/mailing_middleware.py```: содержит класс MailingMiddleware, содержащий методы обертки над методами ```mailing_dal.py``` и библиотеки ```pytelegrambotapi``` для отправки сообщений

**send_msg(chat_id: int | str, mailing: Mailing)** - метод для отправки Mailing пользователю с ```chat_id``` фотографий, видео, документов,текстовых сообщений. Их отправка происходит в следующем порядке: группа фотографий и видео, текст и группа документов 

---

❗️ **.send_media_group** из ```pytelegrambotapi```, не смотря на утверждение в документации, что работает только с группами, состоящими из
от 2 до 10 types.InputMedia, может работать и с одним.

❗️ types.InputMediaPhoto и types.InputMediaVideo нельзя отправлять вместе с types.InputMediaDocument, поэтому сначала отправляются фотографии и видео, чистится массив ```input_media``` с types.InputMedia, отправляется текст и затем документы

---

**launch_mailing_alpha(mailing: Mailing)** - метод над методом ```send_msg``` для его использования над фиксированной выборкой клиентов и проведения альфа-тестирования

**launch_mailing_beta(mailing: Mailing)** - метод над методом ```send_msg``` для его использования над фиксированной выборкой клиентов и проведения бета-тестирования

**create_full_mailing(mailing_name, text, photo_paths, video_paths, document_paths, url_buttons, preset)** - метод для создания объекта ```Mailing``` в таблице со всеми заполненными полями

**update_mailing(mailing_name, new_mailing_name, new_text, new_photo_paths, new_video_paths, new_document_paths, new_url_button, new_preset)** - метод для обновления всех полей объекта ```Mailing```

**create_mailing(mailing_name: str, text: str, preset: str)** - метод для создания объекта ```Mailing``` в таблице только с обязательными полями

**get_mailing(mailing_name: str)** - метод для получения объекта ```Mailing``` с именем ```mailing_name``` из таблицы

**get_all_mailings()** - метод для получения всех объектов ```Mailing``` из таблицы

**delete_mailing(mailing_name: str)** - метод для удаления объекта ```Mailing``` с ```mailing_name``` из таблицы

**get_mailing_stats(mailing_name: str)** - метод для получения полей объекта ```Mailing``` с ```mailing_name```, касающихся А-В тестирования

```../DAL/db_presets_dal.py```: содержит классы PresetN *(number of preset)* для получения выборки из SQL таблиц для рассылки в ```launch_mailing```

```../Models/mailing_model.py```: содержит модель Mailing

* mailing_name - имя рассылки
* photo_paths - массив путей к фототграфия рассылки, которые находятся по пути ```../static/photo```
* video_paths - массив путей к видео рассылки, которые находятся по пути ```../static/video```
* document_paths - массив путей к документам рассылки, которые находятся по пути ```../static/document```
* text - текст сообщения 
* url_buttons - массив с уникальными парами ключ-значение, где ключ - url, значение - текст кнопки

Поля для A-B тестирования:

* alpha - процент выборки для альфа-тестирования
* alpha_sent - количество сообщений, которые были отправлены по выборке alpha
* alpha_delivered - количество сообщений, которые были отправлены по выборке alpha и были доставлены 
* beta - процент выборки для бета-тестирования
* beta_sent - количество сообщений, которые были отправлены по выборке beta
* beta_delivered - количество сообщений, которые были отправлены по выборке beta и были доставлены 

```../DAL/mailing_dal.py```: методы для взаимодействия с моделью Mailing