# Telegram Bot Architecture

Этот документ описывает роль Telegram-бота в MVP и передачу рекламного источника. Правила атрибуции и метрик находятся в [measurement.md](measurement.md), структура таблиц — в [data_model.md](data_model.md).

## Роли

### Клиент

Переходит по ссылке из рекламы, запускает бота, смотрит направления/курсы и оставляет заявку.

Фиксируем:

- рекламный источник;
- `bot_start` / touch;
- просмотры курсов или пакетов;
- lead;
- подтверждённую покупку после связывания с заказом.

### Менеджер

Получает заявку, работает с клиентом и связывает продажу с заказом.

Для demo менеджер может отмечать оплату вручную. В production предпочтителен импорт или интеграция с платёжной/CRM-системой.

### Админ / маркетолог

Создаёт рекламные размещения и смотрит маркетинговый отчёт.

Предлагаемые команды MVP:

```text
/newlink   создать размещение и tracking link
/report    маркетинговый отчёт
/status    состояние данных/импорта
```

Интерфейс может быть кнопочным:

```text
📢 Создать размещение
🔗 Мои размещения
📈 Отчёт
💰 ROMI
📥 Загрузить продажи
```

## Передача рекламного источника

Для каждого placement создаётся уникальный `tracking_token`.

Для Telegram MVP можно использовать deep link:

```text
https://t.me/<bot_username>?start=<tracking_token>
```

Поток:

```text
реклама
  ↓
уникальная ссылка
  ↓
Telegram /start <tracking_token>
  ↓
бот находит placement
  ↓
создаёт user при первом входе
  ↓
фиксирует fact_touch / bot_start
  ↓
пользователь смотрит курсы
  ↓
оставляет lead
  ↓
оплата / импорт заказа
  ↓
связывание заказа с user/student_id
  ↓
атрибуция и отчёт
```

Токен не должен содержать персональные данные.

## Создание размещения

Через `/newlink` админ вводит минимум:

```text
channel
campaign
publication_time
cost
currency
post_type
creative/post
```

Система создаёт:

```text
placement_id
tracking_token
deep link
```

## Отчёт

Пример логики `/report`:

```text
MARKETING REPORT

Период: 01.09 — 10.09

Revenue
Marketing cost
Attributed revenue
ROAS / ROMI

TOP PLACEMENTS
1. Channel / Placement A
2. Channel / Placement B
3. Channel / Placement C

Attribution model:
Last Touch / Linear
```

Отчёт может агрегироваться по channels, campaigns, placements, creatives и courses.

## Оплата и идентификация

Надёжная связь должна строиться через идентификатор, присутствующий в системе продаж и в маркетинговом контуре: например `order_id`, `student_id` или подтверждённое соответствие пользователя.

Username Telegram сам по себе не является надёжным ключом.

Ручная кнопка «оплачено» допустима как demo/MVP-заглушка, но должна быть явно помечена как такая.

## Секреты

Нельзя коммитить:

- Telegram bot token;
- Telegram session files;
- API keys;
- персональные данные.

Локальные секреты хранятся через `.env`; файл уже исключён через `.gitignore`.
