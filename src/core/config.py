import os
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(ROOT, ".env")          # .env всегда ищем в папке проекта, откуда бы ни запускали
load_dotenv(ENV_PATH)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "").replace(" ", "").split(",") if x}
MANAGER_CHAT_ID = int(os.getenv("MANAGER_CHAT_ID") or 0) or None   # куда слать уведомления: личка или общий чат
# Telegram ID менеджеров через запятую - кому разрешено жать «Оплатил» и вводить сумму
MANAGER_IDS = {int(x) for x in os.getenv("MANAGER_IDS", "").replace(" ", "").split(",") if x}
# Username менеджеров без @, через запятую. Если их несколько, заявки распределяются по очереди
MANAGER_USERNAMES = [u.strip().lstrip("@") for u in os.getenv("MANAGER_USERNAME", "postupashki_manager").split(",") if u.strip()]
MANAGER_USERNAME = MANAGER_USERNAMES[0]
HASH_SALT = os.getenv("HASH_SALT", "change-me")
_db = os.getenv("DB_PATH", "data/bot.db")
DB_PATH = _db if os.path.isabs(_db) else os.path.join(ROOT, _db)
# Комиссия эквайринга как доля от суммы (0.03 = 3%). Нужна для ROMI по марже. 0 = не учитываем
ACQUIRING_RATE = float(os.getenv("ACQUIRING_RATE") or 0)
# Окно атрибуции: покупка засчитывается рекламе, если касание было не раньше чем за N дней
ATTRIBUTION_WINDOW_DAYS = int(os.getenv("ATTRIBUTION_WINDOW_DAYS") or 30)
