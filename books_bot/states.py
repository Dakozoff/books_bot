from aiogram.dispatcher.filters.state import State, StatesGroup

class AddBook(StatesGroup):
    title = State()
    author = State()
    genre = State()
    description = State()

class FindBook(StatesGroup):
    text = State()
    genre = State()