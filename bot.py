
import asyncio
import random
import json
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Не задана переменная BOT_TOKEN")

SCORES_FILE = "scores.json"

if os.path.exists(SCORES_FILE):
    with open(SCORES_FILE, "r", encoding="utf-8") as file:
        scores = {
            int(user_id): score
            for user_id, score in json.load(file).items()
        }
else:
    scores = {}

waiting_for_answer = {}

tasks = [
    {"question": "Реши уравнение: 3x + 7 = 22", "answer": "5"},
    {"question": "Найди 15% от 200", "answer": "30"},
    {"question": "Вычисли: 48 / 6 + 7", "answer": "15"},
    {"question": "Реши уравнение: 2x - 4 = 10", "answer": "7"},
    {"question": "Найди 25% от 80", "answer": "20"},
]

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📘 Решать задания")],
        [KeyboardButton(text="📊 Мой прогресс")],
        [KeyboardButton(text="ℹ️ Помощь")],
    ],
    resize_keyboard=True,
)

bot = Bot(token=TOKEN)
dp = Dispatcher()


def save_scores():
    with open(SCORES_FILE, "w", encoding="utf-8") as file:
        json.dump(scores, file, ensure_ascii=False, indent=4)


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет! Я тренажёр по математике для ОГЭ.\n"
        "Выбирай, что будем делать:",
        reply_markup=menu,
    )


@dp.message(lambda message: message.text == "📘 Решать задания")
async def task(message: Message):
    user_id = message.from_user.id
    selected_task = random.choice(tasks)
    waiting_for_answer[user_id] = selected_task["answer"]
    await message.answer(
        selected_task["question"] + "\n\nНапиши ответ числом."
    )


@dp.message(lambda message: message.text == "📊 Мой прогресс")
async def progress(message: Message):
    user_id = message.from_user.id
    user_score = scores.get(user_id, 0)
    await message.answer(f"📊 Твои баллы: {user_score}")


@dp.message(lambda message: message.text == "ℹ️ Помощь")
async def help_message(message: Message):
    await message.answer(
        "Нажми «📘 Решать задания», чтобы получить задачу.\n"
        "Отправляй ответы сообщением в чат."
    )


@dp.message(
    lambda message: message.from_user.id in waiting_for_answer
    and message.text is not None
    and message.text not in [
        "📘 Решать задания",
        "📊 Мой прогресс",
        "ℹ️ Помощь",
        "/start",
    ]
)
async def check_answer(message: Message):
    user_id = message.from_user.id
    scores.setdefault(user_id, 0)
    answer = message.text.strip()
    correct_answer = waiting_for_answer.pop(user_id)

    if answer == correct_answer:
        scores[user_id] += 1
        result = "Верно!"
    else:
        result = f"Не совсем. Правильный ответ: {correct_answer}."

    save_scores()
    await message.answer(
        f"{result}\nТвои баллы: {scores[user_id]}"
    )


@dp.message()
async def other(message: Message):
    await message.answer(
        "Используй кнопки меню, чтобы выбрать действие."
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
