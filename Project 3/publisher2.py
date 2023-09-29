import asyncio
import aioredis


async def main():
    redis = aioredis.from_url("redis://localhost")

    while True:
        message = input("Введите сообщение для отправки (или 'q' для выхода): ")
        if message == 'q':
            break
        await redis.publish('channel:2', message)


if __name__ == "__main__":
    asyncio.run(main())
