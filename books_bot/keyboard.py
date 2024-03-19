import sqlite3

from aiogram import types

base = sqlite3.connect('database.db')

def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    key_list_books = types.KeyboardButton(text='Список книг')
    key_find_book = types.KeyboardButton(text='Найти книгу (ключ слово)')
    key_add_book = types.KeyboardButton(text='Добавить книгу')
    key_find_genres = types.KeyboardButton(text='Найти книгу (жанр)')

    keyboard.row(key_list_books, key_find_book)
    keyboard.add(key_add_book, key_find_genres)

    return keyboard

def generate_books_keyboard():
    keyboard = types.InlineKeyboardMarkup()

    books = base.execute(f"SELECT * FROM books").fetchall()
    for book in books:
        key_book = types.InlineKeyboardButton(text=f"{book[0]} ({book[1]})", callback_data=f'book:{book[0]}')
        keyboard.add(key_book)

    return keyboard

def generate_book_genres():
    keyboard = types.InlineKeyboardMarkup()

    genres = base.execute(f"SELECT * FROM genres").fetchall()
    for genre in genres:
        key_genre = types.InlineKeyboardButton(text=genre[0], callback_data=f'genre:{genre[0]}')
        keyboard.add(key_genre)

    return keyboard

def book_keyboard(name):
    keyboard = types.InlineKeyboardMarkup()

    key_remove = types.InlineKeyboardButton(text='Удалить книгу', callback_data=f'remove_book:{name}')
    key_back = types.InlineKeyboardButton(text='Вернуться назад', callback_data='back')

    keyboard.add(key_remove)
    keyboard.add(key_back)

    return keyboard