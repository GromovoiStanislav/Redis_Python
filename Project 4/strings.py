import redis
import time
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

    print('************** Strings *****************')

    # redis_client.set_response_callback('GET', lambda x: x.decode('utf-8'))

    redis_client.set('favoriteflavor', 'Mint Choc Chip')
    print(redis_client.getset('favoriteflavor', 'Vanilla Bean').decode())  # Mint Choc Chip
    print(redis_client.get('favoriteflavor').decode())  # Vanilla Bean

    redis_client.mset({"Germany": "Berlin", "France": "Paris", "USA": "Washington"})
    if (redis_client.exists("Germany")):
        print(redis_client.get("Germany").decode())
    else:
        print("Cannot find...")

    # Set expire date = 1 day from now
    redis_client.set('favoriteflavor', 'ToDelete', ex=60 * 60 * 24)
    print(redis_client.ttl('favoriteflavor'))  # Expires: 86400

    # Set expire date = 5 sec from now
    redis_client.set('favoriteflavor', 'ToDelete', px=10 * 1000)
    print(redis_client.ttl('favoriteflavor'))  # Expires: 10

    # Set expire date = 12 hours from now
    redis_client.set('anotherflavor', 'ToDelete', px=60 * 60 * 12 * 1000)
    print(redis_client.ttl('anotherflavor'))  # Expires: 43200

    redis_client.execute_command("SET", 'onetimecoupon', 'halftimeoff')
    print(redis_client.getdel('onetimecoupon').decode())  # halftimeoff
    print(redis_client.execute_command("GET", 'onetimecoupon'))  # None

    redis_client.set('limitedtimecoupon', 'freeicecream')
    # Remove key in 60 sex
    print(redis_client.getex('limitedtimecoupon', ex=60))  # freeicecream
    print(redis_client.ttl('limitedtimecoupon'))  # 60
    # Remove key in 30 sec
    print(redis_client.getex('limitedtimecoupon', px=30 * 1000))
    print(redis_client.ttl('limitedtimecoupon'))  # 10

    # Remove key in 10 sec
    redis_client.setex("Germany", 10, "Berlin")
    print(redis_client.ttl('Germany'))  # 10
    # Remove key in 1 sec
    redis_client.psetex("France", 1000, "Paris")
    print(redis_client.ttl('France'))  # 1
    time.sleep(2)
    print(redis_client.exists("France"))  # 0

    # Remove key in 10 sec
    redis_client.expire("USA", 10)
    print(redis_client.ttl('USA'))  # 10

    # delete now
    if redis_client.exists("USA"):
        redis_client.delete("USA")

        if redis_client.exists("USA"):
            print('USA exists')
        else:
            print('Not found...')

    print('************** incr *****************')
    redis_client.set("counter", 0)
    redis_client.incr("counter")

    print(redis_client.get("counter"))  # b'1'
    redis_client.incrby("counter")
    print(redis_client.get("counter"))  # b'2'
    redis_client.incr("counter", 10)
    print(redis_client.get("counter"))  # b'12'
    redis_client.incrby("counter", 10)
    print(redis_client.get("counter"))  # b'22'

    redis_client.decr("counter")
    print(redis_client.get("counter").decode())  # 21
    redis_client.decrby("counter")
    print(redis_client.get("counter").decode())  # 20
    redis_client.decr("counter", 5)
    print(redis_client.get("counter").decode())  # 15
    redis_client.decrby("counter", 5)
    print(redis_client.get("counter").decode())  # 10

    redis_client.quit()


if __name__ == "__main__":
    main()
