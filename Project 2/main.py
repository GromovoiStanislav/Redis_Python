import asyncio
import os

import aioredis
from dotenv import load_dotenv

load_dotenv()


async def strings():
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


async def hashes():
    redis = aioredis.from_url("redis://localhost", db=0, decode_responses=True)

    print('************** Hash *****************')

    await redis.hmset("hash", mapping={"key1": "value1", "key2": "value2", "key3": 123})
    result = await redis.hgetall("hash")  # {'key1': 'value1', 'key2': 'value2', 'key3': '123'}

    assert result == {
        "key1": "value1",
        "key2": "value2",
        "key3": "123",  # note that Redis returns int as string
    }
    print(result)

    await redis.hset("hash", "key3", 12345)
    await redis.hsetnx("hash", "key3", 10)
    print(await redis.hgetall("hash"))  # {'key1': 'value1', 'key2': 'value2', 'key3': '12345'}

    print(await redis.hmget("hash", "key3"))  # ['12345']
    print(await redis.hmget("hash", "key1", "key2"))  # ['value1', 'value2']
    print(await redis.hmget("hash", ["key1", "key2"]))  # ['value1', 'value2']

    print(await redis.hkeys("hash"))  # ['key1', 'key2', 'key3']
    print(await redis.hvals("hash"))  # ['value1', 'value2', '12345']
    print(await redis.hlen("hash"))  # 3

    await redis.hincrby("hash", "key3", 10)
    print(await redis.hget("hash", "key3"))  # 12355

    await redis.hincrbyfloat("hash", "key3", 1.5)
    print(await redis.hget("hash", "key3"))  # 12356.5

    await redis.hdel("hash", "key3")
    print(await redis.hget("hash", "key3"))  # None
    print(await redis.hexists("hash", "key3"))  # False

    # Генерируем данные и добавляем их в хэш
    for i in range(1, 1001):  # Создаем 1000 ключей и значений
        field = f'key{i}'
        value = f'value{i}'
        await redis.hset("big_hash", field, value)

    cursor = 0  # Инициализируем курсор значением "0"
    while True:
        # Выполняем HSCAN с текущим курсором
        cursor, data = await redis.hscan("big_hash", cursor=cursor, count=10)

        print(f"Cursor: {cursor}")
        print(f"Data: {data}")

        # Обрабатываем данные, например, выводим их на экран
        for field, value in data.items():
            print(f"Field: {field}, Value: {value}")

        # Если курсор равен "0", то это означает, что мы просканировали все данные
        if cursor == 0:
            break

    # remove in 10 sec
    await redis.expire("hash", 10)
    print(await redis.ttl("hash"))  # 10

    if await redis.exists("big_hash"):
        await redis.delete("big_hash")
        if await redis.exists("big_hash"):
            print('"big_hash" exists')
        else:
            print('"big_hash" not found...')  # "hash" not found...

    await redis.close()


async def pipeline():
    redis = await aioredis.from_url("redis://localhost", db=0, decode_responses=True)

    print('************** Pipeline *****************')  # Transactions

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


async def lists():
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

        print(await redis.sort('my-list', alpha=True))  # ['CC', 'b', 'c']
        print(await redis.lrange('my-list', 0, -1))  # ['CC', 'c', 'b']

        # Remove key in 10 sec
        await redis.expire('my-list', 10)
        print(await redis.ttl('my-list'))  # 10

        # delete now
        await redis.delete('new-list')
        if await redis.exists('new-list'):
            print('new-list exists')
        else:
            print('Not found...')  # Not found...


async def sets():
    async with aioredis.from_url("redis://localhost", db=0, decode_responses=True) as redis:
        print('************** Set *****************')

        print(await redis.sadd("users:1:tokens", 'Tm1='))  # 1
        print(await redis.sadd("users:1:tokens", 'Tm1='))  # 0
        print(await redis.sadd("users:1:tokens", 'Tm2=', 'Tm3=', 'Tm4=', 'Tm5=', 'Tm6=', 'Tm7=', 'Tm22='))  # 7
        print(
            await redis.smembers("users:1:tokens"))  # {'Tm22=', 'Tm3=', 'Tm6=', 'Tm2=', 'Tm5=', 'Tm1=', 'Tm4=', 'Tm7='
        print(await redis.scard("users:1:tokens"))  # 8

        # Returns if member is a member of the set stored at key
        print(await redis.sismember("users:1:tokens", 'Tm2='))  # True
        print(await redis.sismember("users:1:tokens", 'Tm20='))  # False

        await redis.sadd('users:2:tokens', 'Tm2=', 'Tm3=', 'Tm14=', 'Tm15=', 'Tm16=', 'Tm17=', 'Tm22=')

        # Returns the members of the set resulting from the difference between the first set and all the successive sets.
        print(await redis.sdiffstore('diff', 'users:2:tokens', 'users:1:tokens'))  # 4
        print(await redis.smembers("diff"))  # {'Tm15=', 'Tm16=', 'Tm14=', 'Tm17='}
        diff = await redis.sdiff('users:2:tokens', 'users:1:tokens')
        print(diff)  # {'Tm15=', 'Tm16=', 'Tm14=', 'Tm17='}

        print(await redis.sdiffstore('diff', 'users:1:tokens', 'users:2:tokens'))  # 5
        print(await redis.smembers("diff"))  # {'Tm4=', 'Tm6=', 'Tm1=', 'Tm5=', 'Tm7='}
        diff = await redis.sdiff('users:1:tokens', 'users:2:tokens')
        print(diff)  # {'Tm4=', 'Tm6=', 'Tm1=', 'Tm5=', 'Tm7='}

        # Returns the members of the set resulting from the intersection of all the given sets
        print(await redis.sinterstore('inter', 'users:2:tokens', 'users:1:tokens'))  # 3
        print(await redis.smembers("inter"))  # {'Tm22=', 'Tm2=', 'Tm3='}
        inter = await redis.sinter('users:1:tokens', 'users:2:tokens')
        print(inter)  # {'Tm22=', 'Tm2=', 'Tm3='}

        # Returns the members of the set resulting from the union of all the given sets
        print(await redis.sunionstore('union', 'users:2:tokens', 'users:1:tokens'))  # 12
        print(await redis.smembers(
            "union"))  # {'Tm6=', 'Tm3=', 'Tm7=', 'Tm1=', 'Tm15=', 'Tm2=', 'Tm4=', 'Tm16=', 'Tm5=', 'Tm14=', 'Tm22=', 'Tm17='}
        union = await redis.sunion('users:1:tokens', 'users:2:tokens')
        print(
            union)  # {'Tm6=', 'Tm3=', 'Tm7=', 'Tm1=', 'Tm15=', 'Tm2=', 'Tm4=', 'Tm16=', 'Tm5=', 'Tm14=', 'Tm22=', 'Tm17='}

        # Get one or multiple random members from a set
        print(await redis.srandmember("users:1:tokens"))  # Tm22=
        print(await redis.srandmember("users:1:tokens", 3))  # ['Tm4=', 'Tm6=', 'Tm3=']

        # Remove and return a random member of set
        print(await redis.smembers("users:2:tokens"))  # {'Tm2=', 'Tm15=', 'Tm17=', 'Tm22=', 'Tm16=', 'Tm14=', 'Tm3='}
        print(await redis.spop("users:2:tokens"))  # Tm17=
        print(await redis.smembers("users:2:tokens"))  # {'Tm2=', 'Tm15=', 'Tm22=', 'Tm16=', 'Tm14=', 'Tm3='}

        # Remove one or more members from a set
        print(
            await redis.smembers("users:1:tokens"))  # {'Tm6=', 'Tm5=', 'Tm3=', 'Tm7=', 'Tm2=', 'Tm1=', 'Tm4=', 'Tm22='}
        await redis.srem("users:1:tokens", 'Tm22=', 'Tm7=')
        print(await redis.smembers("users:1:tokens"))  # {'Tm4=', 'Tm1=', 'Tm3=', 'Tm2=', 'Tm6=', 'Tm5='}

        # Move a member from one set to another
        print(await redis.smove('users:1:tokens', 'users:2:tokens', 'Tm3='))  # True
        print(await redis.smove('users:1:tokens', 'users:2:tokens', 'Tm22='))  # False
        print(await redis.smembers("users:1:tokens"))  # {'Tm6=', 'Tm1=', 'Tm5=', 'Tm2=', 'Tm4='}
        print(await redis.smembers("users:2:tokens"))  # {'Tm22=', 'Tm2=', 'Tm3=', 'Tm14=', 'Tm16=', 'Tm17='}

        cursor = 0
        while True:
            # Выполняем SSCAN с текущим курсором
            cursor, data = await redis.sscan('users:1:tokens', cursor=cursor, count=10)

            print(f"Cursor: {cursor}")
            print(f"Data: {data}")

            # Обрабатываем данные, например, выводим их на экран
            for item in data:
                print(f"Item: {item}")

            # Если курсор равен "0", то это означает, что мы просканировали все данные
            if cursor == 0:
                break

        if await redis.exists('users:1:tokens'):
            print(await redis.exists('users:1:tokens'))  # 1
            print(await redis.type('users:1:tokens'))  # set
            print(await redis.delete('users:1:tokens'))  # 1
            print(await redis.type('users:1:tokens'))  # none
            print(await redis.exists('users:1:tokens'))  # 0


async def json():
    import json
    REDIS_URL = os.environ.get('REDIS_URL')

    async with aioredis.from_url(REDIS_URL, db=0, decode_responses=True) as redis:

        print('************** JSON *****************')

        if await redis.exists("doc"):
            await redis.delete('doc')

        my_dict = {"key1": "value1", "key2": "value2", "key3": 123, "key4": {"a": 2}}
        json_str = json.dumps(my_dict)

        await redis.execute_command('JSON.SET', "doc", '$', json_str)
        print(await redis.execute_command('JSON.GET',
                                          "doc"))  # {"key1":"value1","key2":"value2","key3":123,"key4":{"a":2}} <class 'str'>

        print(await redis.execute_command('JSON.OBJKEYS', "doc"))  # ['key1', 'key2', 'key3', 'key4']
        print(await redis.execute_command('JSON.OBJKEYS', "doc", 'key4'))  # ['a']

        print(await redis.execute_command('JSON.OBJLEN', "doc"))  # 4
        print(await redis.execute_command('JSON.OBJLEN', "doc", 'key4'))  # 1

        await redis.execute_command('JSON.SET', "doc", 'key3', 10)
        await redis.execute_command('JSON.SET', "doc", 'key4.a', 3)

        await redis.execute_command('JSON.SET', "doc", 'key5', '"value5"')
        await redis.execute_command('JSON.SET', "doc", 'key4.b', 4)

        print(await redis.execute_command('JSON.GET',
                                          "doc"))  # {"key1":"value1","key2":"value2","key3":10,"key4":{"a":3,"b":4}},"key5":"value5"}

        print(await redis.execute_command('JSON.GET', "doc", '$.key3'))  # [10] <class 'str'>
        print(await redis.execute_command('JSON.GET', "doc", 'key3'))  # 10 <class 'str'>
        print(await redis.execute_command('JSON.GET', "doc", '$.key4'))  # [{"a":3,"b":4}] <class 'str'>
        print(await redis.execute_command('JSON.GET', "doc", 'key4'))  # {"a":3,"b":4} <class 'str'>
        print(await redis.execute_command('JSON.GET', "doc", '$.key4.a'))  # [3] <class 'str'>
        print(await redis.execute_command('JSON.GET', "doc", 'key4.a'))  # 3  <class 'str'>

        await redis.execute_command('JSON.NUMMULTBY ', "doc", 'key3', 2)
        print(await redis.execute_command('JSON.GET', "doc", 'key3'))  # 20

        await redis.execute_command('JSON.NUMINCRBY  ', "doc", 'key3', 4)
        print(await redis.execute_command('JSON.GET', "doc", 'key3'))  # 24

        await redis.execute_command('JSON.NUMINCRBY  ', "doc", 'key4.a', 4)
        print(await redis.execute_command('JSON.GET', "doc", 'key4.a'))  # 7

        await redis.execute_command('JSON.DEL', "doc", 'key4.a')
        print(await redis.execute_command('JSON.GET',
                                          "doc"))  # {"key1":"value1","key2":"value2","key3":24,"key4":{"b":4},"key5":"value5"}

        await redis.execute_command('JSON.DEL', "doc", 'key4')
        print(await redis.execute_command('JSON.GET',
                                          "doc"))  # {"key1":"value1","key2":"value2","key3":24,"key5":"value5"}

        await redis.execute_command('JSON.CLEAR ', "doc")
        print(await redis.execute_command('JSON.GET', "doc"))  # {}

        # ----------------------------------

        my_dict = {"nums": [1, 2, 3], "colors": ["black", "white"], "max_level": [80, 100, 120]}
        json_str = json.dumps(my_dict)

        await redis.execute_command('JSON.SET', "doc", '$', json_str)
        print(await redis.execute_command('JSON.GET', "doc"))  # {"arr":[1,2,3]} <class 'str'>

        print(await redis.execute_command('JSON.ARRLEN ', "doc", "$.max_level"))  # [3]  <class 'str'>
        print(await redis.execute_command('JSON.ARRLEN ', "doc", "max_level"))  # 3  <class 'str'>

        await redis.execute_command('JSON.ARRAPPEND ', "doc", 'colors ', '"blue"')
        await redis.execute_command('JSON.ARRAPPEND ', "doc", 'nums ', 4, 5, 6)
        print(await redis.execute_command('JSON.GET',
                                          "doc"))  # {"nums":[1,2,3,4,5,6],"colors":["black","white","blue"],"max_level":[80,100,120]}

        print(await redis.execute_command('JSON.GET', "doc", '$.colors'))  # [["black","white","blue"]]
        print(await redis.execute_command('JSON.GET', "doc", '$.colors[*]'))  # ["black","white","blue"]
        print(await redis.execute_command('JSON.GET', "doc", 'colors'))  # ["black","white","blue"]
        print(await redis.execute_command('JSON.GET', "doc", 'colors[0]'))  # "black"
        print(await redis.execute_command('JSON.GET', "doc", 'colors[1]'))  # "white"
        print(await redis.execute_command('JSON.GET', "doc", 'colors[2]'))  # "white"
        print(await redis.execute_command('JSON.GET', "doc", 'colors[-1]'))  # "blue"
        print(await redis.execute_command('JSON.GET', "doc", 'colors[-2]'))  # "white"

        print(await redis.execute_command('JSON.ARRINDEX', "doc", '$.colors', '"blue"'))  # [2]
        print(await redis.execute_command('JSON.ARRINDEX', "doc", 'colors', '"blue"'))  # 2

        print(await redis.execute_command('JSON.GET', "doc", 'colors'))  # ["black","white","blue"]
        await redis.execute_command('JSON.ARRINSERT  ', "doc", 'colors ', 2, '"yellow"', '"gold"')
        print(await redis.execute_command('JSON.GET', "doc", 'colors'))  # ["black","white","yellow","gold","blue"]

        print(await redis.execute_command('JSON.ARRPOP', "doc", 'nums'))  # 6
        print(await redis.execute_command('JSON.GET', "doc", 'nums'))  # [1.2,3,4,5]
        print(await redis.execute_command('JSON.ARRPOP', "doc", 'nums', 0))  # 1
        print(await redis.execute_command('JSON.GET', "doc", 'nums'))  # [2,3,4,5]
        print(await redis.execute_command('JSON.ARRPOP', "doc", 'nums', 2))  # 4
        print(await redis.execute_command('JSON.GET', "doc", 'nums'))  # [2,3,5]

        print(await redis.execute_command('JSON.GET', "doc", 'colors'))  # ["black","white","yellow","gold","blue"]
        await redis.execute_command('JSON.ARRTRIM ', "doc", 'colors', 1, 2)
        print(await redis.execute_command('JSON.GET', "doc", 'colors'))  # ["white","yellow"]

        print(await redis.execute_command('JSON.GET', "doc", 'max_level'))  # [80, 100, 120]
        await redis.execute_command('JSON.NUMINCRBY  ', "doc", 'max_level[0]', 4)
        await redis.execute_command('JSON.NUMINCRBY  ', "doc", 'max_level[-1]', -20)
        await redis.execute_command('JSON.NUMMULTBY   ', "doc", 'max_level[1]', 2)
        print(await redis.execute_command('JSON.GET', "doc", 'max_level'))  # [84, 200, 100]

        json_str = await redis.execute_command('JSON.GET', "doc")
        my_dict = json.loads(json_str)
        print(my_dict)

        # ----------------------------------
        await redis.execute_command('JSON.SET', "doc1", '$', json.dumps({"a": 1, "b": 2, "nested": {"a": 3, "b": 2}}))
        await redis.execute_command('JSON.SET', "doc2", '$', json.dumps({"a": 4, "b": 5, "nested": {"a": 6, "b": 5}}))

        print(await redis.execute_command('JSON.MGET ', "doc1", "doc2", 'nested'))  # ['{"a":3,"b":2}', '{"a":6,"b":5}']
        print(await redis.execute_command('JSON.MGET ', "doc1", "doc2", 'nested.a'))  # ['3', '6']
        print(await redis.execute_command('JSON.MGET ', "doc1", "doc2", 'b'))  # ['2', '5']

        # ----------------------------------

        # Remove key in 10 sec
        await redis.expire('doc1', 10)
        await redis.expire('doc2', 10)
        print(await redis.ttl('doc1'))  # 10

        # delete now
        await redis.delete('doc')
        if await redis.exists('doc'):
            print('doc exists')
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
    asyncio.run(strings())
    asyncio.run(hashes())
    asyncio.run(pipeline())
    asyncio.run(lists())
    asyncio.run(sets())
    asyncio.run(json())
    asyncio.run(main_pool())
