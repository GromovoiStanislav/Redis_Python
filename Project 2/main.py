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

    await redis.set("my-key", "my-value")
    val = await redis.get("my-key")
    print(val)


    async with redis.client() as conn:
        await conn.set("my-key", "value")
        val = await conn.get("my-key")
        print(val)


    await redis.mset({"key:1": "value1", "key:2": "value2"})
    print(await redis.mget("key:1", "key:2"))

    await redis.execute_command("set", "my-key", "some value")
    print(await redis.execute_command("get", "my-key"))

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

    await redis.hset("hash", "key3", 12345)
    print(await redis.hgetall("hash"))

    await redis.close()


async def main3():
    # Transactions
    redis = await aioredis.from_url("redis://localhost", db=0, decode_responses=True)
    async with redis.pipeline(transaction=True) as pipe:
        ok1, ok2 = await (pipe.set("key1", "value1").set("key2", "value2").execute())
    assert ok1
    assert ok2
    print(ok1, ok2)
    print(await redis.get("key1"), await redis.get("key2"))

    await redis.delete("foo", "bar")
    async with redis.pipeline(transaction=True) as pipe:
        res = await pipe.incr("foo").incr("bar").execute()
    print(res)
    await redis.close()


async def main_pool():
    pool = aioredis.ConnectionPool.from_url("redis://localhost", max_connections=10, decode_responses=True)
    redis = aioredis.Redis(connection_pool=pool)
    await redis.execute_command("set", "my-key", "my-value")
    val = await redis.execute_command("get", "my-key")
    print("raw value:", val)


if __name__ == '__main__':
    asyncio.run(main1())
    asyncio.run(main2())
    asyncio.run(main3())
    asyncio.run(main_pool())
