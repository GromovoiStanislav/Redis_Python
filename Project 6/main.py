import asyncio
import json

import aiosqlite
import aioredis


async def get_users():
    redis_client = await aioredis.from_url('redis://localhost', db=0, encoding='utf-8')

    async with aiosqlite.connect('database.db') as conn:
        cursor = await conn.cursor()

        cache_value = await redis_client.get("users:friends")
        if cache_value is not None:
            return json.loads(cache_value)

        await cursor.execute("SELECT id, name FROM users;")
        result = await cursor.fetchall()
        await redis_client.set("users:friends", json.dumps(result), ex=30)

    await redis_client.close()
    return result


async def main():
    print(await get_users())


if __name__ == "__main__":
    asyncio.run(main())

