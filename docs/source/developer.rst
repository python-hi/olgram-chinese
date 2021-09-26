Для разработчиков
=================

Сборка и запуск
---------------
Вы можете развернуть Olgram на своём сервере. Вам потребуется собственный VPS или любой хост со статическим адресом
или доменом.

1. Создайте файл .env и заполните его по образцу `example.env <https://github.com/civsocit/olgram/blob/main/example.env>`_
Вам нужно заполнить переменные:

* ``BOT_TOKEN`` - токен нового бота, получить у `@botfather <https://t.me/botfather>`_
* ``POSTGRES_PASSWORD`` - любой случайный пароль
* ``WEBHOOK_HOST`` - IP адрес или доменное имя сервера, на котором запускается проект

2. Рядом с файлом .env сохраните файл
`docker-compose.yaml <https://github.com/civsocit/olgram/blob/main/docker-compose.yaml>`_ и соберите его:

.. code-block:: console

    (bash) $ sudo docker-compose up -d

Готово, ваш собственный Olgram запущен!

Дополнительно
-------------

В docker-compose.yaml приведена минимальная конфигурация. Для использования в серьёзных проектах мы советуем:

* Приобрести домен и настроить его на свой хост
* Наладить реверс-прокси и автоматическое обновление сертификатов - например, с помощью `Traefik <https://github.com/traefik/traefik>`_
* Скрыть IP сервера с помощью `Cloudflire <https://www.cloudflare.com>`_, чтобы пользователи ботов не могли найти IP адрес хоста по Webhook бота.

Пример более сложной конфигурации есть в файле `docker-compose-full.yaml <https://github.com/civsocit/olgram/blob/main/docker-compose-full.yaml>`_
