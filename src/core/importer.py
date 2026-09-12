"""
Импорт истории продаж из base.xlsx (или base.csv) в fact_order / fact_order_item.

Заказ = строки с одним student_id и одинаковым временем. Сумма в строке — доля цены пакета,
поэтому сумма заказа = сумма строк. Повторный импорт того же файла ничего не дублирует.
"""
import io

import pandas as pd

from core import db

COLUMNS = {"номер студента": "student_id", "сумма": "amount", "курс": "course", "время": "ts",
           "student_id": "student_id", "amount": "amount", "course": "course", "ts": "ts", "timestamp": "ts"}


def read_sales(source, filename: str = "") -> pd.DataFrame:
    """source — путь или BytesIO. Понимает русские заголовки base.xlsx и английские base.csv."""
    name = (filename or str(source)).lower()
    df = pd.read_excel(source) if name.endswith((".xlsx", ".xls")) else pd.read_csv(source)
    df = df.rename(columns={c: COLUMNS.get(str(c).strip().lower(), c) for c in df.columns})
    missing = {"student_id", "amount", "course", "ts"} - set(df.columns)
    if missing:
        raise ValueError(f"В файле нет колонок: {', '.join(sorted(missing))}. "
                         "Нужны: Номер студента, Сумма, Курс, Время")
    df = df.dropna(subset=["student_id", "amount", "course", "ts"])
    if df.amount.dtype == object:
        df["amount"] = df.amount.astype(str).str.replace(r"[\s\u00a0,]", "", regex=True)
    df["amount"] = pd.to_numeric(df.amount)
    if not pd.api.types.is_datetime64_any_dtype(df.ts):
        s = df.ts.astype(str).str.strip()
        parsed = pd.to_datetime(s, format="%d.%m.%Y %H:%M:%S", errors="coerce")
        df["ts"] = parsed.fillna(pd.to_datetime(s[parsed.isna()], errors="coerce"))
    df["student_id"] = df.student_id.astype(str).str.replace(r"\.0$", "", regex=True)
    df["course"] = df.course.astype(str).str.strip()
    return df.dropna(subset=["ts"])


def import_sales(conn, source, salt: str, acquiring_rate: float = 0.0, filename: str = "") -> dict:
    df = read_sales(source, filename)
    orders = (df.groupby(["student_id", "ts"])
                .agg(amount=("amount", "sum"), courses=("course", list)).reset_index())
    added = 0
    for o in orders.itertuples():
        uid = db.legacy_user_hash(o.student_id, salt)
        ts = o.ts.strftime("%Y-%m-%d %H:%M:%S")
        db.upsert_user(conn, uid, source="base_xlsx", ts=ts)
        oid = f"x{o.student_id}_{o.ts:%Y%m%d%H%M%S}"
        # сумма делится между курсами поровну — так же, как в base.xlsx (расхождение максимум в копейки)
        if db.add_order(conn, uid, round(float(o.amount), 2), o.courses, acquiring_rate, ts=ts,
                        source="base_xlsx", student_id=o.student_id, order_id=oid, commit=False):
            added += 1
    conn.commit()
    return {"rows": len(df), "orders": len(orders), "added": added, "skipped": len(orders) - added,
            "revenue": float(orders.amount.sum()), "buyers": df.student_id.nunique(),
            "period": (df.ts.min(), df.ts.max())}


def import_bytes(conn, data: io.BytesIO, filename: str, salt: str, acquiring_rate: float = 0.0) -> dict:
    return import_sales(conn, data, salt, acquiring_rate, filename)
