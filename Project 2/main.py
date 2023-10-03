import asyncio
import os

import aioredis
from dotenv import load_dotenv

load_dotenv()


async def main1():
    redis = aioredis.from_url("redis://localhost", db=0)

    print('************** Strings *****************')

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

    if await redis.exists("my-key22"):
        print('"my-key22" exists')
    else:
        print('"my-key22" not found...')

    # Remove key in 1 day from now
    await redis.set('ToDelete1', 'ToDelete', ex=60 * 60 * 24)
    print(await redis.ttl('ToDelete1'))  # 86400

    # Remove key in 30 sec from now
    await redis.set('ToDelete2', 'ToDelete', px=30 * 1000)
    print(await redis.ttl('ToDelete2'))  # 30

    # Remove key in 30 sec from now
    await redis.setex("ToDelete3", 30, "Berlin")
    print(await redis.ttl('ToDelete3'))  # 30

    # Remove key in 30 sec from now
    await redis.psetex("ToDelete4", 30 * 1000, "Paris")
    print(await redis.ttl('ToDelete4'))  # 30

    # remove in 10 sec
    await redis.expire("ToDelete1", 10)
    print(await redis.ttl("ToDelete1"))  # 10

    if await redis.exists("ToDelete1"):
        await redis.delete("ToDelete1")
        if await redis.exists("ToDelete1"):
            print('"ToDelete1" exists')
        else:
            print('"ToDelete1" not found...')

    print('************** incr *****************')

    await redis.set("counter", 0)
    await redis.incr("counter")
    print(await redis.get("counter"))  # 1
    await redis.incrby("counter")
    print(await redis.get("counter"))  # 2
    await redis.incr("counter", 10)
    print(await redis.get("counter"))  # 12
    await redis.incrby("counter", 10)
    print(await redis.get("counter"))  # 22

    await redis.decr("counter")
    print(await redis.get("counter"))  # 21
    await redis.decrby("counter")
    print(await redis.get("counter"))  # 20
    await redis.decr("counter", 5)
    print(await redis.get("counter"))  # 15
    await redis.decrby("counter", 5)
    print(await redis.get("counter"))  # 10

    await redis.close()


async def main2():
    redis = aioredis.from_url("redis://localhost", db=0, decode_responses=True)

    print('************** Hash *****************')

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

    await redis.hincrby("hash", "key3", 10)
    print(await redis.hget("hash", "key3"))  # 12355

    # remove in 10 sec
    await redis.expire("hash", 10)
    print(await redis.ttl("hash"))  # 10

    if await redis.exists("hash"):
        await redis.delete("hash")
        if await redis.exists("hash"):
            print('"hash" exists')
        else:
            print('"hash" not found...')

    await redis.close()


async def main3():

    redis = await aioredis.from_url("redis://localhost", db=0, decode_responses=True)

    print('************** Pipeline *****************') # Transactions

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


async def main4():
    REDIS_URL = os.environ.get('REDIS_URL')

    # List
    async with aioredis.from_url(REDIS_URL, db=0, decode_responses=True) as redis:

        print('************** List *****************')

        if await redis.exists("my-list"):
            await redis.delete('my-list')

        if await redis.exists("new-list"):
            await redis.delete('new-list')

        await redis.rpush('my-list', 'a', 'b', 'c')
        await redis.rpush('my-list', 'd')

        print(await redis.lrange('my-list', 0, -1))  # ['a', 'b', 'c', 'd']
        print(await redis.llen('my-list'))  # 4
        print(await redis.lpos('my-list', 'b'))  # 1
        print(await redis.lpos('my-list', 'G'))  # None
        print(await redis.lindex('my-list', 10))  # None

        await redis.linsert('my-list', 'BEFORE', 'b', 'BB')
        await redis.linsert('my-list', 'AFTER', 'b', 'CC')
        await redis.lset('my-list', 0, 'AA')
        print(await redis.lrange('my-list', 0, -1))  # ['AA', 'BB', 'b', 'CC', 'c', 'd']

        await redis.lrem('my-list', 0, 'BB')
        print(await redis.lrange('my-list', 0, -1))  # ['AA', 'b', 'CC', 'c', 'd']

        print(await redis.lpop('my-list'))  # AA
        print(await redis.rpop('my-list'))  # d
        print(await redis.lrange('my-list', 0, -1))  # ['b', 'CC', 'c']

        print(await redis.rpoplpush('my-list', 'my-list'))  # c
        print(await redis.lrange('my-list', 0, -1))  # ['c', 'b', 'CC']

        while await redis.llen('my-list'):
            await redis.rpoplpush('my-list', 'new-list')

        print(await redis.lrange('my-list', 0, -1))  # []
        print(await redis.lrange('new-list', 0, -1))  # ['c', 'b', 'CC']

        print(await redis.execute_command("lMOVE", 'new-list', 'my-list', 'LEFT', 'RIGHT'))  # c
        print(await redis.execute_command("lMOVE", 'new-list', 'my-list', 'LEFT', 'RIGHT'))  # b
        print(await redis.execute_command("lMOVE", 'new-list', 'my-list', 'LEFT', 'LEFT'))  # CC
        print(await redis.lrange('my-list', 0, -1))  # ['CC', 'c', 'b']
        print(await redis.lrange('new-list', 0, -1))  # []

        # Remove key in 10 sec
        await redis.expire('my-list', 10)
        print(await redis.ttl('my-list'))  # 10

        # delete now
        await redis.delete('new-list')
        if await redis.exists('new-list'):
            print('new-list exists')
        else:
            print('Not found...')  # Not found...


async def main_pool():
    print('************** Pool *****************')

    pool = aioredis.ConnectionPool.from_url("redis://localhost", max_connections=10, decode_responses=True)
    redis = aioredis.Redis(connection_pool=pool)
    
    await redis.execute_command("set", "my-key", "my-value")
    val = await redis.execute_command("get", "my-key")
    print("raw value:", val)


if __name__ == '__main__':
    asyncio.run(main1())
    asyncio.run(main2())
    asyncio.run(main3())
    asyncio.run(main4())
    asyncio.run(main_pool())
