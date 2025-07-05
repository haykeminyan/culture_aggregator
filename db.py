from typing import Optional
import asyncpg
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

config = {
    "database": os.getenv("POSTGRES_DB", "culture_aggregator"),
    "user": os.getenv("POSTGRES_USER", "admin"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "port": int(os.getenv("POSTGRES_PORT", 5432)),
}

dsn = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"

_pool: Optional[asyncpg.pool.Pool] = None


async def get_pool() -> asyncpg.pool.Pool:
    """
    Получает или создаёт пул соединений с базой данных.
    """
    global _pool
    if _pool is None:
        try:
            _pool = await asyncpg.create_pool(
                dsn=dsn,
                min_size=1,
                max_size=10,
            )
            logger.info("Database connection pool created.")
        except Exception as e:
            logger.exception("Failed to create database connection pool.")
            raise e
    return _pool


async def close_pool():
    """
    Закрывает пул соединений.
    """
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed.")
