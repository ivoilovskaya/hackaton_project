# Marketing Data Model

Этот документ описывает структуру данных для MVP маркетинговой аналитики. Правила расчёта метрик и атрибуции вынесены в [measurement.md](measurement.md).

## Основной принцип

Для каждого ключевого события должно быть понятно:

```text
кто → что сделал → когда → откуда пришёл → к какой рекламной активности относится
```

## Сущности и таблицы

| Таблица | Что хранит | Основной источник |
|---|---|---|
| `dim_channel` | канал привлечения: Telegram, VK, YouTube, partner и т. п. | админ / импорт |
| `dim_campaign` | рекламная кампания и период её проведения | админ |
| `dim_placement` | конкретное размещение: канал, кампания, публикация, стоимость, валюта, тип поста, tracking token | админ / `/newlink` |
| `dim_creative` | креатив или рекламный материал | админ |
| `dim_course` | курс или продукт | справочник продукта |
| `dim_user` | внутренний пользователь, дата первого появления, первый известный источник | бот / backend |
| `fact_touch` | рекламное касание: пользователь, placement, creative, время | бот / redirect |
| `fact_bot_event` | действия внутри бота: bot_start, просмотр направления, курса, пакета | бот |
| `fact_lead` | заявка: пользователь, интерес, время, менеджер, статус | бот / менеджер |
| `fact_order` | заказ/оплата: пользователь, сумма, время, статус, возврат, связь с lead | менеджер / импорт |
| `fact_order_item` | состав заказа: один или несколько курсов/продуктов | вместе с заказом |
| `fact_attribution` | результат атрибуции: модель, purchase/order, placement, вес, attributed revenue, время расчёта | расчёт при отчёте |

## Ключевые поля

### dim_placement

Минимально:

```text
placement_id
campaign_id
channel_id
creative_id / post_id
tracking_token
publication_time
cost
currency
post_type
discount
```

`tracking_token` уникален для рекламного размещения или пары placement/creative.

### dim_user

Минимально:

```text
user_id
telegram_id_hash
username_hash        # опционально
first_seen_at
first_tracking_token
student_id           # только если связь подтверждена
```

Telegram username не используется как стабильный идентификатор: он может измениться. Внутри системы нужен собственный `user_id`.

### fact_touch

```text
touch_id
user_id
placement_id
creative_id
touch_time
tracking_token
```

### fact_bot_event

```text
event_id
user_id
event_type
course_id
event_time
metadata
```

Примеры `event_type`: `bot_start`, `course_view`, `package_view`, `lead_started`.

### fact_lead

```text
lead_id
user_id
student_id
lead_time
interest
self_reported_source
manager_id
status
```

Ответ пользователя «откуда узнал» хранится как отдельный self-reported сигнал и не подменяет техническую атрибуцию.

### fact_order

```text
order_id
purchase_id
user_id
student_id
lead_id
purchase_time
amount
refunded_amount
status
payment_provider
```

### fact_order_item

```text
order_id
course_id
quantity
item_amount
```

Отдельная таблица нужна, чтобы корректно хранить пакеты с несколькими курсами.

### fact_attribution

```text
attribution_id
order_id / purchase_id
placement_id
model
window_days
weight
attributed_revenue
calculated_at
```

Результаты разных моделей не перезаписывают друг друга.

## Связи

```text
dim_channel
    ↓
dim_campaign
    ↓
dim_placement ─── dim_creative
    ↓
fact_touch
    ↓
dim_user
    ↓
fact_lead
    ↓
fact_order
    ↓
fact_order_item ─── dim_course

fact_order + fact_touch
        ↓
fact_attribution
```

## Правила качества данных

- первичные ключи уникальны;
- внешние ключи ссылаются на существующие записи;
- неизвестные значения не заменяются нулём;
- деньги хранятся в копейках или Decimal;
- время хранится с часовым поясом;
- персональные идентификаторы не публикуются в открытом репозитории;
- synthetic/mock данные маркируются отдельно от реальных.
