"""
Reaksiya botlar tizimi (bitta fayl)
-----------------------------------
- MENU_TOKEN      : asosiy bot (/start bosilganda reaksiya botlar ro'yxatini chiqaradi)
- REACTION_TOKENS : reaksiya botlar (kanal postiga har biri o'z emojisini qo'yadi)

Ishga tushirish:
    pip install aiogram
    python reaksiya_bot.py

Foydalanuvchi: menu botga /start -> botni tanlaydi -> kanalga ADMIN qilib qo'shadi.
Shundan keyin bot kanaldagi har bir yangi postga o'z emojisini qo'yadi.
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import ReactionTypeEmoji
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ============================ SOZLAMALAR ============================

# 1) Asosiy (menyu) bot tokeni
MENU_TOKEN = "8977440527:AAEoWBOU0Qe2euOGhZ3ZxGlJNsvio0YnpGk"

# 2) Reaksiya botlar tokenlari (tartib bilan: 01, 02, 03 ...)
REACTION_TOKENS = [
    "8984621826:AAGYu3sEm-Vl3a6poaCQxTSrXg1dmQsZneQ",
    "8764969883:AAGVpfPdCTENHS3aApa1jKOudvglnFEPx0w",
    "8825221690:AAHILSeH888tcOccajj7LLLJwIosEpRgWBE",
    "8688115729:AAESMiXCcfvVWuRryY4xDNJ3OD52hpsOEqc",
    "8715530539:AAFdc_Gwxjwma-gjnhdrrqFiWKsQKQqjcS0",
    "8840176737:AAErcJigIAlOtq_JDlF_p1G4k3wWmUzo2CQ",
    "8885537199:AAHZp81Vdgega1m9hcyy5nJaHQEZvKyga5s",
    "8634319596:AAFeJu_IpZ5ZO_J3P0q9uMiNUrH_vE60fHo",
    "8817581130:AAGj8j9PnE6MdrVJayxSNkzEZsRLEohSI9c",
    "8836434459:AAHgcsikDQBf-kZfNKThcEIeJo3x97HCCsg",
    "8872228575:AAFtNtTMTUElZAe9GL12kl0YMZkCn9Yqcmg",
    "8864533381:AAGVygzAJWJi7Bl8glZgMaunEQqBqaIEqS8",
    "8324057139:AAHAeGpBFAo0VVIvTBOamG0vE6xGIaKlwhg",
    "8984798217:AAG-63xsZjBlWA9jJOwvUyjuQUAgwSlJwwU",
    "8983311434:AAFKRCxDxDHY6FdPcpMGDqeLSmUbgLntAIQ",
    "8765157177:AAEEnA0DYj6oswvtF56qy7zNaIFkwJsUcZ0",
]

# 3) Har bir reaksiya bot uchun emoji (Telegram ruxsat bergan emojilar bo'lishi shart)
EMOJIS = [
    "❤", "🔥", "🎉", "👏", "😁", "🤩", "😍", "💯",
    "🥰", "🐳", "⚡", "🕊", "😇", "🍓", "💋", "😱",
]

# ====================================================================

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("reaksiya")

assert len(REACTION_TOKENS) == len(EMOJIS), "Tokenlar va emojilar soni teng bo'lishi kerak"

TOKEN_EMOJI = dict(zip(REACTION_TOKENS, EMOJIS))

# username'lar ishga tushganda get_me() orqali avtomatik to'ldiriladi
BOT_USERNAMES: list[str] = []


# ----------------------- REAKSIYA BOTLAR -----------------------
react_dp = Dispatcher()


@react_dp.channel_post()
async def on_channel_post(message: types.Message, bot: Bot):
    emoji = TOKEN_EMOJI.get(bot.token)
    if not emoji:
        return
    try:
        await bot.set_message_reaction(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reaction=[ReactionTypeEmoji(emoji=emoji)],
        )
    except Exception as e:
        log.warning("Reaksiya qo'yilmadi (%s, chat %s): %s", emoji, message.chat.id, e)


# ----------------------- MENYU BOT -----------------------
menu_dp = Dispatcher()


def main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Kanalga reaksiya qo'shish", callback_data="choose")
    return kb.as_markup()


def choose_kb():
    kb = InlineKeyboardBuilder()
    for i, username in enumerate(BOT_USERNAMES, 1):
        emoji = EMOJIS[i - 1]
        kb.button(
            text=f"{emoji} Reaksiya bot {i:02d}",
            url=f"https://t.me/{username}?startchannel=true&admin=post_messages",
        )
    kb.adjust(2)
    kb.row(types.InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back"))
    return kb.as_markup()


@menu_dp.message(CommandStart())
async def start(m: types.Message):
    await m.answer(
        "👋 Salom! Men kanal postlariga avtomatik reaksiya qo'yuvchi botlar markaziman.\n\n"
        "Boshlash uchun pastdagi tugmani bosing.",
        reply_markup=main_kb(),
    )


@menu_dp.callback_query(F.data == "choose")
async def choose(c: types.CallbackQuery):
    await c.message.edit_text(
        "📣 <b>Kanalga qo'shish uchun botni tanlang:</b>\n\n"
        "Tanlangan bot ochilgach, kanalingizni tanlang va uni administrator qilib tasdiqlang.\n"
        "Bir nechta botni qo'shsangiz, postlarda turli emojilar paydo bo'ladi.",
        reply_markup=choose_kb(),
        parse_mode="HTML",
    )
    await c.answer()


@menu_dp.callback_query(F.data == "back")
async def back(c: types.CallbackQuery):
    await c.message.edit_text(
        "👋 Salom! Men kanal postlariga avtomatik reaksiya qo'yuvchi botlar markaziman.\n\n"
        "Boshlash uchun pastdagi tugmani bosing.",
        reply_markup=main_kb(),
    )
    await c.answer()


# ----------------------- ISHGA TUSHIRISH -----------------------
async def main():
    menu_bot = Bot(token=MENU_TOKEN)
    react_bots = [Bot(token=t) for t in REACTION_TOKENS]

    # Reaksiya botlarning username'larini olamiz (menyu tugmalari uchun)
    for b in react_bots:
        me = await b.get_me()
        BOT_USERNAMES.append(me.username)
        log.info("Reaksiya bot tayyor: @%s -> %s", me.username, TOKEN_EMOJI[b.token])

    menu_me = await menu_bot.get_me()
    log.info("Menyu bot tayyor: @%s", menu_me.username)

    await asyncio.gather(
        menu_dp.start_polling(menu_bot, allowed_updates=["message", "callback_query"]),
        react_dp.start_polling(
            *react_bots,
            allowed_updates=["channel_post"],
            handle_signals=False,
        ),
    )


if __name__ == "__main__":
    asyncio.run(main())
