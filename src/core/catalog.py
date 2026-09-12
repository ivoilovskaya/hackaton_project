"""
Каталог курсов для бота.

name  — название ровно как в base.xlsx (чтобы оплаты склеивались с данными).
price — ориентир: самая частая цена этого курса в base.xlsx после 13.08 (вне распродажи).
desc  — ЗАГЛУШКИ. Реальных описаний курсов в данных нет, их нужно заменить текстами Поступашек.
"""

COURSES = {
    "ml_start":  {"name": "ML старт",            "price": 8950, "desc": "Первые шаги в машинном обучении."},
    "ml_pro":    {"name": "ML про",              "price": 8950, "desc": "Продвинутое ML для собеседований в BigTech."},
    "ai_agents": {"name": "AI агенты",           "price": 8950, "desc": "Новый курс про AI-агентов."},
    "ds":        {"name": "Data Science",        "price": 6950, "desc": "Data Science от данных до модели."},
    "de":        {"name": "Data Engenering",     "price": 6950, "desc": "Data Engineering: хранилища и пайплайны."},
    "an_start":  {"name": "Аналитика старт",     "price": 8950, "desc": "Базовая аналитика данных."},
    "an_pro":    {"name": "Аналитика про",       "price": 8950, "desc": "Аналитика для стажировок и работы."},
    "ab":        {"name": "АВ тестам",           "price": 5990, "desc": "Подготовка к A/B-тестам."},
    "alg_start": {"name": "Алгоритмы старт",     "price": 8950, "desc": "Алгоритмы с нуля."},
    "alg_pro":   {"name": "Алгоритмы про",       "price": 8950, "desc": "Алгоритмы для технических собеседований."},
    "alg":       {"name": "Алгоритмы",           "price": 8950, "desc": "Курс по алгоритмам."},
    "be_start":  {"name": "Backend старт",       "price": 8950, "desc": "Backend-разработка с нуля."},
    "be_pro":    {"name": "Backend про",         "price": 8950, "desc": "Backend для стажировок и работы."},
    "linal":     {"name": "Линейная алгебра",    "price": 9950, "desc": "Линейная алгебра для вуза."},
    "matan":     {"name": "Мат анализ",          "price": 9950, "desc": "Математический анализ для вуза."},
    "tv":        {"name": "Теория вероятностей", "price": 9950, "desc": "Теория вероятностей для вуза."},
    "discr":     {"name": "Дискретка",           "price": 8950, "desc": "Дискретная математика."},
    "k_vuzu":    {"name": "К ВУЗу",              "price": 6950, "desc": "Подготовка к поступлению."},
}

DIRECTIONS = {
    "ml":   ("🤖 ML и AI",            ["ml_start", "ml_pro", "ai_agents", "ds", "de"]),
    "an":   ("📊 Аналитика",          ["an_start", "an_pro", "ab"]),
    "alg":  ("🧩 Алгоритмы",          ["alg_start", "alg_pro", "alg"]),
    "be":   ("⚙️ Backend",            ["be_start", "be_pro"]),
    "math": ("📐 Высшая математика",  ["linal", "matan", "tv", "discr"]),
    "uni":  ("🎓 Поступление",        ["k_vuzu"]),
}

# Самые частые пакеты в base.xlsx (24% заказов — пакеты из 2+ курсов). Цена — частая цена пары вне распродажи.
BUNDLES = {
    "b1": {"courses": ["ai_agents", "ml_pro"],  "price": 14950},
    "b2": {"courses": ["an_start", "an_pro"],   "price": 14950},
    "b3": {"courses": ["ml_start", "alg_start"], "price": 14950},
    "b4": {"courses": ["alg_start", "alg_pro"], "price": 14950},
    "b5": {"courses": ["ml_start", "ml_pro"],   "price": 14950},
}


def bundle_title(bid: str) -> str:
    return " + ".join(COURSES[c]["name"] for c in BUNDLES[bid]["courses"])


def rub(x: float) -> str:
    return f"{x:,.0f} ₽".replace(",", " ")
