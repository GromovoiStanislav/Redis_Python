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



    print('************** List/Array *****************')



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
