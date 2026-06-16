from typing import Any, Dict, Iterable, List, Optional, Tuple

import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool

from .config import get_settings

_pool: Optional[MySQLConnectionPool] = None


def init_pool() -> MySQLConnectionPool:
    """Create the MySQL connection pool once and reuse it."""
    global _pool
    if _pool is None:
        settings = get_settings()
        _pool = MySQLConnectionPool(
            pool_name="faq_pool",
            pool_size=5,
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci",
            autocommit=False,
        )
    return _pool


def get_connection():
    return init_pool().get_connection()


def fetch_all(sql: str, params: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def fetch_one(sql: str, params: Tuple[Any, ...] = ()) -> Optional[Dict[str, Any]]:
    rows = fetch_all(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params: Tuple[Any, ...] = ()) -> int:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid or cursor.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def execute_many(sql: str, params: Iterable[Tuple[Any, ...]]) -> int:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.executemany(sql, params)
        conn.commit()
        return cursor.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
