# -*- coding: utf-8 -*-
"""
Бот-визитка для канала «Нейросети по-простому».
Показывает услуги по разработке ботов, примеры, принимает заявки.
Библиотека: python-telegram-bot 22.x
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# ════════════════════════════════════════════
#  ⚙️ НАСТРОЙКИ — МЕНЯЙ ТОЛЬКО ЭТОТ БЛОК
# ════════════════════════════════════════════
BOT_TOKEN   = os.getenv("BOT_TOKEN", "ВСТАВЬ_ТОКЕН_БОТА")  # токен от @BotFather (лучше через переменную окружения)
OWNER_ID    = int(os.getenv("OWNER_ID", "0"))              # твой Telegram ID (узнать: @userinfobot) — сюда падают заявки
OWNER_USER  = os.getenv("OWNER_USER", "твой_юзернейм")     # твой @ без собачки, для кнопки «написать»
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/ai_i_boty")  # ссылка на канал

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Кто сейчас оформляет заявку (user_id -> True). Память в процессе, без БД — боту-визитке хватает.
WRITING_ORDER = set()

# ════════════════════════════════════════════
#  📝 ТЕКСТЫ
# ════════════════════════════════════════════
WELCOME = (
    "👋 Привет! Я бот-визитка канала «Нейросети по-простому».\n\n"
    "Здесь ты можешь посмотреть, какие боты я делаю, глянуть примеры "
    "и оставить заявку на своего бота.\n\n"
    "Выбери, что интересно 👇"
)

SERVICES = (
    "🤖 *РАЗРАБОТКА TELEGRAM-БОТОВ*\n"
    "_Пишу ботов на Python и Node.js под твою задачу. Живой код, а не конструктор._\n\n"

    "🟢 *СТАРТ — от 700 ₽*\n"
    "Простой бот: приветствия, авто-ответы, FAQ, кнопочное меню.\n"
    "_Для небольшого чата или личного проекта._\n\n"

    "🔵 *ЧАТ-БОТ — от 1 500 ₽*\n"
    "Модерация, статистика, игры, реакции, рассылки.\n"
    "_Оживляет сообщество и снимает рутину с админа._\n\n"

    "🟣 *AI-БОТ — от 2 500 ₽*\n"
    "Бот с нейросетью внутри: отвечает, генерит тексты, ведёт диалог с характером.\n"
    "_Свой ИИ-помощник прямо в Telegram._\n\n"

    "🟠 *БОТ-ПАРСЕР — от 3 000 ₽*\n"
    "Следит за источником (сайт/Discord/канал) и шлёт уведомления: цены, сток, новости.\n"
    "_Перестаёшь следить вручную — бот делает это за тебя._\n\n"

    "🟡 *ПОД КЛЮЧ — договоримся*\n"
    "Своя идея? Опиши — оценю и честно скажу, берусь или нет.\n\n"

    "━━━━━━━━━━\n"
    "✅ Помогу с запуском и хостингом\n"
    "✅ Бесплатные правки после сдачи\n"
    "✅ Оплата: 50% сейчас / 50% по готовности"
)

EXAMPLES = (
    "💼 *Примеры моих работ:*\n\n"
    "🔹 *«Джо»* — бот-компаньон для чата с ИИ-характером: отвечает на вопросы, "
    "ведёт игры, дуэли мемов, систему кармы и реакций. Полностью кастомный.\n\n"
    "🔹 *Бот-парсер* — мониторит источник 24/7 и шлёт уведомления в Telegram "
    "(сток предметов, события, цены). С базой данных и фильтрами.\n\n"
    "_Живую демонстрацию покажу в переписке — напиши мне._"
)

# ════════════════════════════════════════════
#  ⌨️ КЛАВИАТУРЫ
# ════════════════════════════════════════════
def main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 Услуги и цены", callback_data="services")],
        [InlineKeyboardButton("💼 Примеры работ", callback_data="examples")],
        [InlineKeyboardButton("📝 Заказать бота", callback_data="order")],
        [InlineKeyboardButton("📢 Наш канал", url=CHANNEL_URL)],
    ])

def back_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Заказать бота", callback_data="order")],
        [InlineKeyboardButton("⬅️ В меню", callback_data="menu")],
    ])

def menu_only_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ В меню", callback_data="menu")]])

# ════════════════════════════════════════════
#  🎯 ХЕНДЛЕРЫ
# ════════════════════════════════════════════
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    WRITING_ORDER.discard(update.effective_user.id)  # сброс режима заявки, если был
    await update.message.reply_text(WELCOME, reply_markup=main_kb())

async def on_button(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "menu":
        WRITING_ORDER.discard(q.from_user.id)
        await q.edit_message_text(WELCOME, reply_markup=main_kb())

    elif data == "services":
        await q.edit_message_text(SERVICES, reply_markup=back_kb(), parse_mode="Markdown")

    elif data == "examples":
        await q.edit_message_text(EXAMPLES, reply_markup=back_kb(), parse_mode="Markdown")

    elif data == "order":
        WRITING_ORDER.add(q.from_user.id)
        await q.edit_message_text(
            "📝 *Оформление заявки*\n\n"
            "Опиши одним сообщением, какой бот тебе нужен:\n"
            "• что он должен делать\n"
            "• для чата, канала или отдельно\n"
            "• есть ли срок / бюджет\n\n"
            "Напиши прямо сюда — я передам это разработчику, и он свяжется с тобой.",
            reply_markup=menu_only_kb(), parse_mode="Markdown"
        )

async def on_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Ловит текст. Если человек в режиме заявки — пересылает её владельцу."""
    uid = update.effective_user.id
    if uid not in WRITING_ORDER:
        # просто текст вне заявки — мягко направляем в меню
        return await update.message.reply_text(
            "Жми /start, чтобы открыть меню 👇", reply_markup=main_kb())

    WRITING_ORDER.discard(uid)
    user = update.effective_user
    uname = f"@{user.username}" if user.username else "без юзернейма"

    # 1) подтверждение заказчику
    await update.message.reply_text(
        "✅ Заявка отправлена! Разработчик свяжется с тобой в ближайшее время.\n\n"
        f"Если что — можешь написать напрямую: @{OWNER_USER}",
        reply_markup=menu_only_kb()
    )

    # 2) пересылаем заявку владельцу
    if OWNER_ID:
        text = (
            "🔔 *НОВАЯ ЗАЯВКА*\n\n"
            f"От: {user.first_name} ({uname}, ID `{user.id}`)\n\n"
            f"Сообщение:\n{update.message.text}"
        )
        try:
            await ctx.bot.send_message(chat_id=OWNER_ID, text=text, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Не смог отправить заявку владельцу: {e}")

async def on_error(update, ctx):
    logger.error(f"Ошибка: {ctx.error}")

# ════════════════════════════════════════════
#  🚀 ЗАПУСК
# ════════════════════════════════════════════
def main():
    if BOT_TOKEN == "ВСТАВЬ_ТОКЕН_БОТА":
        logger.error("❌ BOT_TOKEN не задан! Укажи токен в настройках или переменной окружения.")
        return
    if not OWNER_ID:
        logger.warning("⚠️ OWNER_ID не задан — заявки не будут приходить тебе в личку. Укажи свой ID.")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.add_error_handler(on_error)

    logger.info("✅ Бот-визитка запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
