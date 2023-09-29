import asyncio
import aioredis


async def main1():
    redis = aioredis.from_url("redis://localhost", db=0)
    await redis.set("key", "string-value")
    bin_value = await redis.get("key")
    assert bin_value == b"string-value"
    print(bin_value)

    redis = aioredis.from_url("redis://localhost", db=0, decode_responses=True)
    str_value = await redis.get("key")
    assert str_value == "string-value"
    print(str_value)

    await redis.close()


async def main2():
    redis = aioredis.from_url("redis://localhost", db=0, decode_responses=True)
    await redis.hmset("hash", mapping={"key1": "value1", "key2": "value2", "key3": 123})
    result = await redis.hgetall("hash")

    assert result == {
        "key1": "value1",
        "key2": "value2",
        "key3": "123",  # note that Redis returns int as string
    }
    print(result)
    await redis.close()



async def main3():
    redis = await aioredis.from_url("redis://localhost", db=0, decode_responses=True)
    async with redis.pipeline(transaction=True) as pipe:
        ok1, ok2 = await (pipe.set("key1", "value1").set("key2", "value2").execute())
    assert ok1
    assert ok2
    print(ok1,ok2)
    print(await redis.get("key1"), await redis.get("key2"))


if __name__ == '__main__':
    asyncio.run(main1())
    asyncio.run(main2())
    asyncio.run(main3())
