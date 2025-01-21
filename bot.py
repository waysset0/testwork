import asyncio
import logging
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart

BOT_TOKEN = '7833652636:AAGjHmuHGqTbeRPSvvcBJpwcAc4YsCN-9Cg'
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart()) 
async def start_command(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Получить данные по товару', callback_data='success')]])
    await message.answer("Привет! Нажми кнопку, чтобы получить данные по товару с Wildberries", reply_markup=kb)

@dp.callback_query() # функция для обработки кнопки
async def get_wb_data(callback_query: CallbackQuery):
    await bot.edit_message_text(
        text="Введите артикул товара с Wildberries:",
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id
    )

@dp.message() # функция для получения и обработки артикулов
async def handle_article(message: types.Message):
    article = message.text
    await message.answer(f"Ты ввёл артикул: {article}. Теперь обрабатываю его через API Wildberries...")
    try:
        async with httpx.AsyncClient() as client: # запрос к fastapi для получения данных о продукте
            response = await client.get(f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={article}")
            product_data = response.json()
            await message.answer(f"Данные о продукте:\nНазвание: {product_data['data']['products'][0]['name']}\nАртикул: {product_data['data']['products'][0]['id']}\nЦена: {product_data['data']['products'][0]['salePriceU'] / 100}\nРейтинг: {product_data['data']['products'][0]['reviewRating']}\nКоличество на складах: {product_data['data']['products'][0]['totalQuantity']}")
    except:
        await message.answer(f"Не удалось получить информацию о товаре.")

async def main(): # запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
