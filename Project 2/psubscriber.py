import asyncio
import async_timeout
import aioredis

STOPWORD = "STOP"


async def reader(channel: aioredis.client.PubSub):
    while True:
        try:
            async with async_timeout.timeout(1):
                message = await channel.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    print(f"(Reader) Message Received: {message}")
                    if message["data"].decode() == STOPWORD:
                        print("(Reader) STOP")
                        break
                await asyncio.sleep(0.01)
        except asyncio.TimeoutError:
            pass


async def main():
    redis = await aioredis.from_url("redis://localhost")
    pubsub = redis.pubsub()
    await pubsub.psubscribe("channel:*")

    future = asyncio.create_task(reader(pubsub))

    await redis.publish("channel:1", "Hello")
    await redis.publish("channel:2", "World")
    await redis.publish("channel:1", STOPWORD)

    await future


if __name__ == "__main__":
    # asyncio.run(main())
    asyncio.get_event_loop().run_until_complete(main())
