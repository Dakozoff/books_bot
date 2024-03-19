import logging
import sqlite3

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode
from aiogram import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import *
from sql_funcs import *
from keyboard import *
from states import AddBook, FindBook

base = sqlite3.connect('database.db')

# Инициализация бота

bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer(f"Добро пожаловать!", reply_markup=main_keyboard())

# Обработчик колбэков

@dp.callback_query_handler()
async def callbacks_handler(call: types.CallbackQuery, state: FSMContext):
    data = call.data

    if data.startswith('book:'):
        name = data.split(':')[1]

        book = base.execute(f"SELECT * FROM books WHERE title='{name}'").fetchone()
        book_text = (
            f"Название: {book[0]}\n"
            f"Автор: {book[1]}\n"
            f"Жанр: {book[3]}\n"
            f"Описание: {book[2]}"
        )

        await call.message.edit_text(text=book_text, reply_markup=book_keyboard(name))

    elif data == 'back':
        response = "Список книг:"
        await call.message.edit_text(text=response, reply_markup=generate_books_keyboard())

    elif data.startswith('remove_book:'):
        name = data.split(':')[1]

        base.execute(f"DELETE FROM books WHERE title='{name}'")
        base.commit()

        delete_text = (
            "Книга была удалена"
        )

        await call.message.edit_text(text=delete_text)

# Обработчик сообщений

@dp.message_handler()
async def messages_handler(message: types.Message, state: FSMContext):
    text = message.text

    if text == 'Список книг':
        response = "Список книг:"
        await message.answer(text=response, reply_markup=generate_books_keyboard())

    elif text == 'Добавить книгу':
        await message.answer("Введите название книги:")
        await AddBook.title.set()

    elif text == 'Найти книгу (ключ слово)':
        await message.answer("Введите ключевое слово для поиска:")
        await FindBook.text.set()

    elif text == 'Найти книгу (жанр)':
        await message.answer("Введите жанр для поиска:")
        await FindBook.genre.set()

# Обработчики событий

@dp.message_handler(state=FindBook.genre)
async def process_find_book_genre(message: types.Message, state: FSMContext):
    genre = message.text

    books = base.execute(f"SELECT * FROM books").fetchall()

    keyboard = types.InlineKeyboardMarkup()

    for book in books:
        name_book = book[0]
        author_book = book[1]
        genre_book = book[2]

        if genre.lower() == genre_book.lower():
            key_book = types.InlineKeyboardButton(text=f'{name_book} ({author_book})', callback_data=f'book:{name_book}')
            keyboard.add(key_book)

    await message.answer(f"Результаты поиска по жанру \"{genre}\":", reply_markup=keyboard)
    await state.finish()

@dp.message_handler(state=FindBook.text)
async def process_find_book(message: types.Message, state: FSMContext):
    keyword = message.text

    books = base.execute(f"SELECT * FROM books").fetchall()

    keyboard = types.InlineKeyboardMarkup()

    for book in books:
        name_book = book[0]
        author_book = book[1]

        if keyword.lower() in name_book.lower() or keyword.lower() in author_book.lower():
            key_book = types.InlineKeyboardButton(text=f'{name_book} ({author_book})', callback_data=f'book:{name_book}')
            keyboard.add(key_book)

    await message.answer(f"Результаты поиска по ключевому слову \"{keyword}\":", reply_markup=keyboard)
    await state.finish()

@dp.message_handler(state=AddBook.title)
async def process_title(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text
    await message.answer("Введите автора книги:")
    await AddBook.author.set()

@dp.message_handler(state=AddBook.author)
async def process_author(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['author'] = message.text
    await message.answer("Введите жанр книги или выберите из предложенных вариантов:", reply_markup=generate_book_genres())
    await AddBook.genre.set()

@dp.callback_query_handler(state=AddBook.genre)
async def process_callback_genre(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if call.data.startswith('genre:'):
            data['genre'] = call.data.split(':')[1]

    await call.message.answer("Введите описание книги:")
    await AddBook.description.set()

@dp.message_handler(state=AddBook.genre)
async def process_genre(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['genre'] = message.text
    await message.answer("Введите описание книги:")
    await AddBook.description.set()

@dp.message_handler(state=AddBook.description)
async def process_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text

        add_book(title=data['title'], author=data['author'], description=data['description'], genre=data['genre'])

    await message.answer("Книга успешно добавлена!")
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)