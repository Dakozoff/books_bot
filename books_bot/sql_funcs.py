import sqlite3

base = sqlite3.connect('database.db')

def add_book(title, author, genre, description):
    base.execute(f"INSERT INTO books(title, author, genre, description) VALUES('{title}', '{author}', '{genre}', '{description}')")
    base.commit()

    return True