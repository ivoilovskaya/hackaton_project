"""
Карта данных: что мы знаем, что начали собирать, что оцениваем и что пока узнать нельзя.
Для каждого «собираемого» поля считается, насколько оно реально заполнено в базе.
Используется командой /datamap и предупреждениями в /report.
"""
from core import config

CANNOT_KNOW = [
    "клики по ссылке без нажатия «Старт» — Telegram их не показывает",
    "содержание переписки с менеджером — бот её не видит",
    "клиенты, написавшие менеджеру напрямую, минуя бота",
    "инкрементальность: купил бы человек без рекламы — нужен эксперимент (holdout)",
]


def one(conn, sql, *args):
    return conn.execute(sql, args).fetchone()[0] or 0


def collect(conn) -> dict:
    """Числа для карты данных и список пробелов (warnings)."""
    d = {
        "hist_orders": one(conn, "SELECT COUNT(*) FROM fact_order WHERE source_system='base_xlsx'"),
        "hist_revenue": one(conn, "SELECT SUM(amount) FROM fact_order WHERE source_system='base_xlsx'"),
        "placements": one(conn, "SELECT COUNT(*) FROM dim_placement WHERE placement_type!='unknown'"),
        "no_category": one(conn, "SELECT COUNT(*) FROM dim_placement WHERE placement_type!='unknown' AND post_category IS NULL"),
        "no_campaign": one(conn, "SELECT COUNT(*) FROM dim_placement WHERE placement_type!='unknown' AND campaign_name IS NULL"),
        "discount_no_value": one(conn, "SELECT COUNT(*) FROM dim_placement WHERE post_category='discount' AND discount_value IS NULL"),
        "unknown_tags": one(conn, "SELECT COUNT(*) FROM dim_placement WHERE placement_type='unknown'"),
        "touches": one(conn, "SELECT COUNT(*) FROM fact_touch"),
        "touches_tagged": one(conn, "SELECT COUNT(*) FROM fact_touch WHERE placement_id IS NOT NULL"),
        "leads": one(conn, "SELECT COUNT(*) FROM fact_lead"),
        "leads_untagged": one(conn, "SELECT COUNT(*) FROM fact_lead l LEFT JOIN fact_touch t USING(touch_id) "
                                    "WHERE t.placement_id IS NULL"),
        "leads_answered": one(conn, "SELECT COUNT(*) FROM fact_lead l LEFT JOIN fact_touch t USING(touch_id) "
                                    "WHERE t.placement_id IS NULL AND l.self_reported_source NOT IN ('skip') "
                                    "AND l.self_reported_source IS NOT NULL"),
        "leads_open": one(conn, "SELECT COUNT(*) FROM fact_lead WHERE status='open'"),
        "bot_orders": one(conn, "SELECT COUNT(*) FROM fact_order WHERE source_system='bot'"),
        "no_course": one(conn, "SELECT COUNT(DISTINCT order_id) FROM fact_order_item i JOIN fact_order o USING(order_id) "
                               "WHERE o.source_system='bot' AND i.course='не указан'"),
        "acquiring": config.ACQUIRING_RATE,
    }
    w = []
    if not d["hist_orders"]:
        w.append("история продаж не загружена — отправьте боту base.xlsx")
    if not d["placements"]:
        w.append("нет ни одного размещения — создайте ссылки через /newlink")
    if d["no_category"]:
        w.append(f"у {d['no_category']} размещ. не указан тип поста (sale / discount / launch / native / content)")
    if d["discount_no_value"]:
        w.append(f"у {d['discount_no_value']} скидочных размещ. не указан размер скидки")
    if d["unknown_tags"]:
        w.append(f"{d['unknown_tags']} меток пришли по ссылкам, которых нет в /newlink — у них нет канала и стоимости")
    if not d["acquiring"]:
        w.append("не задан ACQUIRING_RATE — ROMI по марже не отличается от ROMI по выручке")
    if d["no_course"]:
        w.append(f"в {d['no_course']} оплатах не указан курс")
    if d["leads_open"]:
        w.append(f"{d['leads_open']} лидов без отметки «Оплатил» — купили не все или менеджер не отметил")
    d["warnings"] = w
    return d


def render(d: dict, rub) -> str:
    """Текст для /datamap: четыре уровня знания."""
    pct = lambda a, b: f"{a}/{b}" if b else "0"
    ok = lambda cond: "✅" if cond else "⚠️"
    lines = [
        "<b>📌 Знаем — факты из base.xlsx</b>",
        "сумма, курсы, student_id, время оплаты",
        f"{ok(d['hist_orders'])} загружено заказов: {d['hist_orders']}" + (f", {rub(d['hist_revenue'])}" if d["hist_orders"] else ""),
        "источник этих продаж неизвестен",
        "",
        "<b>📥 Начали собирать — бот и /newlink</b>",
        f"{ok(d['placements'])} размещений с каналом, стоимостью и датой публикации: {d['placements']}",
        f"{ok(not d['no_category'])} тип поста указан: {pct(d['placements'] - d['no_category'], d['placements'])}",
        f"{ok(not d['no_campaign'])} кампания указана: {pct(d['placements'] - d['no_campaign'], d['placements'])}",
        f"{ok(not d['discount_no_value'])} скидка указана у скидочных постов"
        + (f" (нет у {d['discount_no_value']})" if d["discount_no_value"] else ""),
        f"{ok(d['touches'])} заходов в бота с временем: {d['touches']}, из них по рекламной метке: {d['touches_tagged']}",
        f"{ok(d['leads'])} лидов (интерес + начало диалога): {d['leads']}",
        f"{ok(d['leads_answered'] == d['leads_untagged'])} ответили «откуда узнал» (среди пришедших без метки): "
        f"{pct(d['leads_answered'], d['leads_untagged'])}",
        f"{ok(d['bot_orders'])} оплат, связанных с лидом: {d['bot_orders']}",
        f"{ok(d['acquiring'])} эквайринг: " + (f"{d['acquiring']:.1%} (ставка-допущение)" if d["acquiring"] else "не задан"),
        "",
        "<b>📊 Оцениваем — модель, а не факт</b>",
        f"атрибуция (last / first / linear), окно {config.ATTRIBUTION_WINDOW_DAYS} дн., ROMI — см. /report",
        "",
        "<b>❓ Пока нельзя узнать даже с ботом</b>",
        *[f"• {x}" for x in CANNOT_KNOW],
    ]
    if d["warnings"]:
        lines += ["", "<b>Что исправить сейчас</b>", *[f"• {x}" for x in d["warnings"]]]
    return "\n".join(lines)
