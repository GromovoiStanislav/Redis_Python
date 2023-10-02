import redis
import os
from dotenv import load_dotenv

load_dotenv()


def main():
    REDIS_URL = os.environ.get('REDIS_URL')

    if REDIS_URL:
        with redis.from_url(REDIS_URL) as redis_client:
            working_with_list(redis_client)
    else:
        with redis.StrictRedis(host='localhost', port=6379, db=0) as redis_client:
            working_with_list(redis_client)


def working_with_list(redis_client):
    redis_client.flushall()

    print('************** List/Array *****************')
    redis_client.rpush('my-list', 'a', 'b', 'c')
    redis_client.rpush('my-list', 'd')

    print(redis_client.lrange('my-list', 0, -1))  # [b'a', b'b', b'c', b'd']
    print(redis_client.llen('my-list'))  # 4
    print(redis_client.lpos('my-list', 'b'))  # 1
    print(redis_client.lpos('my-list', 'G'))  # None
    print(redis_client.lindex('my-list', 10))  # None

    redis_client.linsert('my-list', 'BEFORE', 'b', 'BB')
    redis_client.linsert('my-list', 'AFTER', 'b', 'CC')
    redis_client.lset('my-list', 0, 'AA')
    print(redis_client.lrange('my-list', 0, -1))  # [b'AA', b'BB', b'b', b'CC', b'c', b'd']

    redis_client.lrem('my-list', 0, 'BB')
    print(redis_client.lrange('my-list', 0, -1))  # [b'AA', b'b', b'CC', b'c', b'd']

    print(redis_client.lpop('my-list'))  # b'AA'
    print(redis_client.rpop('my-list'))  # b'd'
    print(redis_client.lrange('my-list', 0, -1))  # [b'b', b'CC', b'c']

    print(redis_client.rpoplpush('my-list', 'my-list'))  # b'c'
    print(redis_client.lrange('my-list', 0, -1))  # [b'c', b'b', b'CC']

    while redis_client.llen('my-list'):
        redis_client.rpoplpush('my-list', 'new-list')

    print(redis_client.lrange('my-list', 0, -1))  # []
    print(redis_client.lrange('new-list', 0, -1))  # [b'c', b'b', b'CC']

    print(redis_client.lmove('new-list', 'my-list')) # b'c'
    print(redis_client.lmove('new-list', 'my-list','LEFT', 'RIGHT'))  # b'b'
    print(redis_client.lmove('new-list', 'my-list', 'LEFT', 'LEFT'))  # b'CC'
    print(redis_client.lrange('my-list', 0, -1))  # [b'CC', b'c', b'b']
    print(redis_client.lrange('new-list', 0, -1))  # []

    # Remove key in 10 sec
    redis_client.expire('my-list', 10)
    print(redis_client.ttl('my-list'))  # 10

    # delete now
    redis_client.delete('new-list')
    if redis_client.exists('new-list'):
        print('new-list exists')
    else:
        print('Not found...')


if __name__ == "__main__":
    main()
