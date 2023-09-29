import asyncio
import async_timeout
import aioredis

STOPWORD = "STOP"


async def listen_for_channel_1(channel: aioredis.client.PubSub):
    while True:
        try:
            async with async_timeout.timeout(1):
                message = await channel.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    print(f"(Reader) Message Received: {message}")
                    if message["data"] == STOPWORD:
                        print("(Reader) STOP")
                        break

                    data = message['data']
                    _channel = message['channel']
                    pattern = message['pattern']
                    print_message(_channel, data, pattern)

                await asyncio.sleep(0.01)
        except asyncio.TimeoutError:
            pass

    await channel.unsubscribe()
    await channel.close()


async def listen_for_channel_2(channel: aioredis.client.PubSub):
    while True:
        try:
            async with async_timeout.timeout(1):
                message = await channel.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    print(f"(Reader) Message Received: {message}")
                    if message["data"] == STOPWORD:
                        print("(Reader) STOP")
                        break

                    data = message['data']
                    _channel = message['channel']
                    pattern = message['pattern']
                    print_message(_channel, data, pattern)

                await asyncio.sleep(0.01)
        except asyncio.TimeoutError:
            pass

    await channel.unsubscribe()
    await channel.close()


def print_message(channel, message, pattern=None):
    if pattern is None:
        print(f"Получено сообщение: {message} из {channel}")
    else:
        print(f"Получено сообщение из канала '{channel}' соответствующего паттерну '{pattern}': {message}")


async def main():
    redis = aioredis.from_url("redis://localhost", decode_responses=True)

    pubsub1 = redis.pubsub()
    await pubsub1.subscribe("channel:1", "channel:2")
    task1 = asyncio.create_task(listen_for_channel_1(pubsub1))

    pubsub2 = redis.pubsub()
    await pubsub2.psubscribe("channel:*")
    task2 = asyncio.create_task(listen_for_channel_2(pubsub2))

    await asyncio.gather(task1, task2)


if __name__ == "__main__":
    asyncio.run(main())
