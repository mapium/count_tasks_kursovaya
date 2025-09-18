from db.database import cursor, conn
import psycopg2
from core.security import ph
from argon2.exceptions import VerifyMismatchError

def register_user(username, password):
    username = username.strip()
    password_hash = ph.hash(password)
    try:
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s)', (username, password_hash))
        conn.commit()
        return True
    except psycopg2.IntegrityError:
        conn.rollback()
        return False

def authorize_user(username, password):
    username = username.strip()
    cursor.execute('SELECT password_hash FROM users WHERE username = %s', (username,))
    result = cursor.fetchone()
    if result is None or result['password_hash'] is None:
        return False
    stored_hash = result['password_hash']
    try:
        ph.verify(stored_hash, password)
        return True
    except VerifyMismatchError:
        return False