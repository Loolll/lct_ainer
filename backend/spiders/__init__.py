from misc.db import get_db

from . import bruteforce_houses


async def main():
    pool = await get_db()

    await bruteforce_houses.bruteforce(pool)
