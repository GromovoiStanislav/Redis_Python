import redis
import os
from dotenv import load_dotenv

load_dotenv()


def main():
    # Создаем подключение к серверу Redis
    REDIS_URL = os.environ.get('REDIS_URL')
    print(REDIS_URL)
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
    print(redis_client.get('favoriteflavor'))  # Vanilla Bean

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

    print('************** List/Array *****************')

    print('************** Hash *****************')

    redis_client.hmset("hash", {"key1": "value1", "key2": "value2", "key3": 123})
    print(redis_client.hgetall("hash"))  # {b'key1': b'value1', b'key2': b'value2', b'key3': b'123'}

    redis_client.hset("hash", "key3", 12345)
    hash_data = redis_client.hgetall("hash")
    print(hash_data)  # {b'key1': b'value1', b'key2': b'value2', b'key3': b'12345'}
    # Преобразование бинарных данных в строковый формат
    decoded_data = {key.decode("utf-8"): value.decode("utf-8") for key, value in hash_data.items()}
    print(decoded_data)  # {'key1': 'value1', 'key2': 'value2', 'key3': '12345'}

    # # ***********************************
    # # 3) Streams: MINID Trimming Strategy
    # print('3. Streams: MINID Trimming Strategy')
    # # First record: [{"id":"1617307200000-0","message":{"couponcode":"weekendsale","userid":"6935"}}]
    # print(redis_client.xrange('redemptions', '-', '+', count=1))
    # # Last record: [{"id":"1617314919000-0","message":{"couponcode":"weekendsale","userid":"5577"}}]
    # print(redis_client.xrevrange('redemptions', '+', '-', count=1))
    # print(redis_client.xlen('redemptions'))  # 250
    # # Trimming to the specified timestamp
    # print(redis_client.xtrim('redemptions', strategy='MINID', threshold=1617307696000))  # 16
    # print(redis_client.xlen('redemptions'))  # 234
    # # First record changed: [{"id":"1617307696000-0","message":{"couponcode":"weekendsale","userid":"529"}}]
    # print(redis_client.xrange('redemptions', '-', '+', count=1))
    # # Add with trim strategy, dropping messages behind the threshold id
    # print(
    #     redis_client.xadd('redemptions', {'couponcode': 'weekendsale', 'userid': '9002'},
    #                         trim={'strategy': 'MINID', 'threshold': 1617307851000}))
    # print(redis_client.xlen('redemptions'))  # 230
    #
    # # ***********************************
    # # 4) Hashes: HRANDFIELD Command
    # print('4. Hashes: HRANDFIELD Command')
    # # {"10":"Szechuan... }
    # print(redis_client.hgetall('entrees'))
    # # Returns a random field name
    # # Random: 19
    # print(redis_client.hrandfield('entrees'))
    # # Returns 2 different fields with values
    # # With 2 values: {"10":"Szechuan Shredded Beef","19":"Fried Mushrooms with Black Bean Sauce"}
    # print(redis_client.hrandfieldcountwithvalues('entrees', 2))
    # # Returns a single value when random numbers are the same
    # # {"10":"Szechuan Shredded Beef"}
    # print(redis_client.hrandfieldcountwithvalues('entrees', -2))
    #
    # # ***********************************
    # # 5) Sets: SMISMEMBER Command
    # print('5. Sets: SMISMEMBER Command')
    # # Return all members
    # print(redis_client.smembers('winninglotto'))
    # # Returns array of booleans - true/false per specified member to probe
    # print(redis_client.smismember('winninglotto', ["1", "3", "7", "19", "22", "33"]))

    redis_client.quit()


if __name__ == "__main__":
    main()
