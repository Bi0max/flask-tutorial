import sqlite3


def connection():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    return c, conn