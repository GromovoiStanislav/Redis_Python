import asyncio

import aiosqlite


async def seed():
    async with aiosqlite.connect('database.db') as db:

        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                age INTEGER
            )
        ''')
        await db.commit()

        employees_data = [
            ('John Doe', 30),
            ('Jane Smith', 25),
            ('Bob Johnson', 35)
        ]
        await db.executemany('INSERT INTO users (name, age) VALUES (?, ?)', employees_data)
        await db.commit()


if __name__ == '__main__':
    asyncio.run(seed())
