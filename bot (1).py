import json
import logging
from pathlib import Path

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ---- Shu uchta qiymatni oʻzgartiring ----
BOT_TOKEN = "BU_YERGA_BOT_TOKENINGIZNI_QOYING"
ADMIN_ID = 1007263663
WEBAPP_URL = "https://SIZNING-NOMINGIZ.github.io/dokon/"
# -----------------------------------------

PRODUCTS_FILE = Path(__file__).parent / "products.json"

logging.basicConfig(level=logging.INFO)


def load_products():
    with open(PRODUCTS_FILE, encoding="utf-8") as f:
        return {p["id"]: p for p in json.load(f)}


def money(n):
    return f"{n:,}".replace(",", " ") + " soʻm"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("Doʻkonni ochish", web_app=WebAppInfo(url=WEBAPP_URL))]],
        resize_keyboard=True,
    )
    await update.message.reply_text(
        "Assalomu alaykum! Telefon aksessuarlarini tanlash uchun pastdagi tugmani bosing.",
        reply_markup=keyboard,
    )


async def on_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        order = json.loads(update.message.web_app_data.data)
        products = load_products()
        lines, total = [], 0
        for item in order["items"]:
            product = products.get(item["id"])
            qty = int(item["qty"])
            if not product or qty < 1:
                continue
            # Narxni mijozdan emas, products.json faylidan olamiz
            sub = product["price"] * qty
            total += sub
            lines.append(f"- {product['name']} x {qty} = {money(sub)}")
        if not lines:
            raise ValueError("boʻsh buyurtma")
    except Exception:
        logging.exception("Buyurtmani oʻqib boʻlmadi")
        await update.message.reply_text("Buyurtmani qabul qilib boʻlmadi. Qaytadan urinib koʻring.")
        return

    user = update.effective_user
    username = f"@{user.username}" if user.username else "username yoʻq"
    text = (
        "Yangi buyurtma\n\n"
        + "\n".join(lines)
        + f"\n\nJami: {money(total)}\n\n"
        f"Ism: {order.get('name', '')}\n"
        f"Telefon: {order.get('phone', '')}\n"
        f"Izoh: {order.get('comment') or '-'}\n"
        f"Telegram: {user.full_name} ({username}), ID {user.id}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=text)
    await update.message.reply_text(
        f"Buyurtmangiz qabul qilindi. Jami: {money(total)}. Tez orada siz bilan bogʻlanamiz."
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, on_order))
    app.run_polling()


if __name__ == "__main__":
    main()
