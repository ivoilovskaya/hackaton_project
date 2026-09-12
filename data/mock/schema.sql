-- ============================================================
-- schema.sql
-- Схема базы данных bot_data.db
-- dim_ — справочники (кто и что существует)
-- fact_ — факты (что произошло)
-- is_synthetic = 1 — строка создана демо-генератором, а не реальными данными
-- ============================================================

PRAGMA foreign_keys = ON;

-- ============================================================
-- 1. dim_placement — размещение рекламы
--    Заполняет админ через /newlink
-- ============================================================
CREATE TABLE IF NOT EXISTS dim_placement (
    placement_id    TEXT PRIMARY KEY,
    campaign_name   TEXT,
    channel         TEXT,
    placement_type  TEXT,
    creative        TEXT,
    post_category   TEXT,
    discount_value  REAL,
    cost            REAL,
    publication_time TEXT,
    created_at      TEXT,
    is_synthetic    INTEGER DEFAULT 0
);

-- ============================================================
-- 2. dim_user — пользователь (только хеши, без имён)
-- ============================================================
CREATE TABLE IF NOT EXISTS dim_user (
    user_id_hash        TEXT PRIMARY KEY,
    username_hash       TEXT,
    first_seen          TEXT,
    first_placement_id  TEXT,
    source_system       TEXT,
    FOREIGN KEY (first_placement_id) REFERENCES dim_placement(placement_id)
);

-- ============================================================
-- 3. fact_touch — заход в бота (нажал «Старт»)
--    Связи: dim_placement → fact_touch (по какой рекламе пришёл)
--           dim_user       → fact_touch (кто пришёл)
-- ============================================================
CREATE TABLE IF NOT EXISTS fact_touch (
    touch_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id_hash  TEXT NOT NULL,
    placement_id  TEXT,
    touch_type    TEXT,
    timestamp     TEXT,
    is_synthetic  INTEGER DEFAULT 0,
    FOREIGN KEY (user_id_hash) REFERENCES dim_user(user_id_hash),
    FOREIGN KEY (placement_id) REFERENCES dim_placement(placement_id)
);

-- ============================================================
-- 4. fact_bot_event — что смотрел в боте
--    Связь: fact_touch → fact_bot_event
-- ============================================================
CREATE TABLE IF NOT EXISTS fact_bot_event (
    event_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id_hash  TEXT NOT NULL,
    touch_id      INTEGER NOT NULL,
    event_type    TEXT,
    item          TEXT,
    timestamp     TEXT,
    is_synthetic  INTEGER DEFAULT 0,
    FOREIGN KEY (user_id_hash) REFERENCES dim_user(user_id_hash),
    FOREIGN KEY (touch_id)     REFERENCES fact_touch(touch_id)
);

-- ============================================================
-- 5. fact_lead — заявка (нажал «Хочу этот курс»)
--    Связь: fact_touch → fact_lead
-- ============================================================
CREATE TABLE IF NOT EXISTS fact_lead (
    lead_id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id_hash            TEXT NOT NULL,
    touch_id                INTEGER NOT NULL,
    course_interest         TEXT,
    self_reported_source    TEXT,
    conversation_started_at TEXT,
    manager_id              TEXT,
    status                  TEXT,
    is_synthetic            INTEGER DEFAULT 0,
    FOREIGN KEY (user_id_hash) REFERENCES dim_user(user_id_hash),
    FOREIGN KEY (touch_id)     REFERENCES fact_touch(touch_id)
);

-- ============================================================
-- 6. fact_order — оплата (менеджер или импорт base.xlsx)
--    Связь: fact_lead → fact_order
-- ============================================================
CREATE TABLE IF NOT EXISTS fact_order (
    order_id               TEXT PRIMARY KEY,
    user_id_hash           TEXT NOT NULL,
    lead_id                INTEGER,
    student_id             TEXT,
    amount                 REAL,
    variable_costs         REAL,
    variable_costs_source  TEXT,
    timestamp              TEXT,
    source_system          TEXT,
    is_synthetic           INTEGER DEFAULT 0,
    FOREIGN KEY (user_id_hash) REFERENCES dim_user(user_id_hash),
    FOREIGN KEY (lead_id)     REFERENCES fact_lead(lead_id)
);

-- ============================================================
-- 7. fact_order_item — курсы внутри заказа
--    Связь: fact_order → fact_order_item
--    (так не теряются пакеты — один заказ = несколько курсов)
-- ============================================================
CREATE TABLE IF NOT EXISTS fact_order_item (
    item_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id   TEXT NOT NULL,
    course     TEXT,
    amount     REAL,
    FOREIGN KEY (order_id) REFERENCES fact_order(order_id)
);

-- ============================================================
-- 8. fact_attribution — атрибуция (считает /report)
--    Связь: fact_order ~ fact_attribution
--    Доля выручки каждому касанию
-- ============================================================
CREATE TABLE IF NOT EXISTS fact_attribution (
    attribution_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id             TEXT NOT NULL,
    touch_id             INTEGER NOT NULL,
    placement_id         TEXT,
    attribution_model    TEXT,
    weight               REAL,
    attributed_revenue   REAL,
    attributed_margin    REAL,
    window_days          INTEGER,
    calculated_at        TEXT,
    FOREIGN KEY (order_id)     REFERENCES fact_order(order_id),
    FOREIGN KEY (touch_id)     REFERENCES fact_touch(touch_id),
    FOREIGN KEY (placement_id) REFERENCES dim_placement(placement_id)
);

-- ============================================================
-- Индексы для ускорения JOIN и фильтрации
-- ============================================================

-- По user_id_hash (используется почти во всех JOIN)
CREATE INDEX IF NOT EXISTS idx_touch_user      ON fact_touch(user_id_hash);
CREATE INDEX IF NOT EXISTS idx_event_user      ON fact_bot_event(user_id_hash);
CREATE INDEX IF NOT EXISTS idx_lead_user       ON fact_lead(user_id_hash);
CREATE INDEX IF NOT EXISTS idx_order_user      ON fact_order(user_id_hash);

-- По touch_id (связь событий с касанием)
CREATE INDEX IF NOT EXISTS idx_event_touch     ON fact_bot_event(touch_id);
CREATE INDEX IF NOT EXISTS idx_lead_touch      ON fact_lead(touch_id);
CREATE INDEX IF NOT EXISTS idx_attr_touch      ON fact_attribution(touch_id);

-- По placement_id (фильтрация по каналу/кампании в отчётах)
CREATE INDEX IF NOT EXISTS idx_touch_placement  ON fact_touch(placement_id);
CREATE INDEX IF NOT EXISTS idx_attr_placement  ON fact_attribution(placement_id);

-- По order_id (разбор состава заказа)
CREATE INDEX IF NOT EXISTS idx_item_order      ON fact_order_item(order_id);
CREATE INDEX IF NOT EXISTS idx_attr_order      ON fact_attribution(order_id);

-- По lead_id (связь заказа с заявкой)
CREATE INDEX IF NOT EXISTS idx_order_lead       ON fact_order(lead_id);

-- По is_synthetic (быстрая фильтрация демо-данных)
CREATE INDEX IF NOT EXISTS idx_touch_synth     ON fact_touch(is_synthetic);
CREATE INDEX IF NOT EXISTS idx_event_synth     ON fact_bot_event(is_synthetic);
CREATE INDEX IF NOT EXISTS idx_lead_synth      ON fact_lead(is_synthetic);
CREATE INDEX IF NOT EXISTS idx_order_synth    ON fact_order(is_synthetic);
CREATE INDEX IF NOT EXISTS idx_attr_synth      ON fact_attribution(is_synthetic);
CREATE INDEX IF NOT EXISTS idx_placement_synth ON dim_placement(is_synthetic);
