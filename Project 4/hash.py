import redis
import os
from dotenv import load_dotenv

load_dotenv()


def main():
    # Создаем подключение к серверу Redis
    REDIS_URL = os.environ.get('REDIS_URL')

    if REDIS_URL:
        redis_client = redis.from_url(REDIS_URL)
    else:
        redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    # Выполняем команду FLUSHALL для очистки всей базы данных
    redis_client.flushall()

    print('************** Hash *****************')

    redis_client.hset("hash:001", mapping={"key1": "value1", "key2": "value2", "key3": 123})
    print(redis_client.hgetall("hash:001"))  # {b'key1': b'value1', b'key2': b'value2', b'key3': b'123'}

    redis_client.hset("hash:001", "key3", 12345)
    print(redis_client.hget("hash:001", "key3").decode())

    redis_client.hincrby("hash:001", "key3", 10)
    print(redis_client.hget("hash:001", "key3").decode())  # 12355

    hash_data = redis_client.hgetall("hash:001")
    print(hash_data)  # {b'key1': b'value1', b'key2': b'value2', b'key3': b'12345'}

    # Преобразование бинарных данных в строковый формат
    decoded_data = {key.decode(): value.decode() for key, value in hash_data.items()}
    print(decoded_data)  # {'key1': 'value1', 'key2': 'value2', 'key3': '12345'}

    redis_client.hdel("hash:001", "key3")
    print(redis_client.hgetall("hash:001")) # {b'key1': b'value1', b'key2': b'value2'}

    if redis_client.exists("hash:001"):
        print('hash:001 exists')
    else:
        print('Not found...')

    # Remove key in 10 sec
    redis_client.expire("hash:001", 10)
    print(redis_client.ttl('hash:001'))  # 10

    # delete now
    if redis_client.exists("hash:001"):
        redis_client.delete("hash:001")

        if redis_client.exists("hash:001"):
            print('hash:001 exists')
        else:
            print('Not found...')

    redis_client.quit()


if __name__ == "__main__":
    main()
