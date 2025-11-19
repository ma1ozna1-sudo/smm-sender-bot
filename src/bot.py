import asyncio
import json
from pathlib import Path

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from config import BOT_TOKEN, ADMIN_ID

router = Router()

USERS_FILE = Path("users.json")


def load_users() -> list[int]:
    if USERS_FILE.exists():
        try:
            data = json.loads(USERS_FILE.read_text(encoding="utf-8"))
            return [int(x) for x in data]
        except Exception:
            return []
    return []


def save_users(user_ids: list[int]) -> None:
    USERS_FILE.write_text(
        json.dumps(user_ids, ensure_ascii=False, indent=2), encoding="utf-8"
    )


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    users = load_users()
    user_id = message.from_user.id

    if user_id not in users:
        users.append(user_id)
        save_users(users)

    text = (
        "👋 Привіт!\n\n"
        "Це простий SMM-sender бот.\n"
        "Я зберігаю твій чат і можу отримувати розсилки від власника бота."
    )
    await message.answer(text)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    text = (
        "ℹ️ Команди бота:\n"
        "/start — підписатися на розсилку\n"
        "/help — коротка довідка\n\n"
        "Для адміністратора:\n"
        "/send <текст> — розіслати повідомлення всім підписникам."
    )
    await message.answer(text)


@router.message(Command("send"))
async def cmd_send(message: Message) -> None:
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Ця команда тільки для адміністратора.")
        return

    # текст после /send
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "Напиши текст розсилки після команди, наприклад:\n/send Новий пост на каналі!"
        )
        return

    broadcast_text = parts[1].strip()
    users = load_users()
    if not users:
        await message.answer("Немає підписників для розсилки.")
        return

    sent = 0
    failed = 0

    for user_id in users:
        try:
            await message.bot.send_message(chat_id=user_id, text=broadcast_text)
            sent += 1
        except Exception:
            failed += 1

    await message.answer(
        f"✅ Розсилка завершена.\n" f"Успішно: {sent}\n" f"Помилки: {failed}"
    )


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не заданий. Додай його в .env")

    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(router)

    print("🤖 SMM sender bot запущено...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
