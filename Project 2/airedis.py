import redis


def main():
    # Создаем подключение к серверу Redis
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    redis_client.set_response_callback('SET', lambda x: x.decode('utf-8'))
    redis_client.set_response_callback('GET', lambda x: x.decode('utf-8'))
    redis_client.set_response_callback('GETSET', lambda x: x.decode('utf-8'))

    # Выполняем асинхронную команду FLUSHALL для очистки всей базы данных
    redis_client.flushall()

    # ***********************************
    # 1) Strings: New Options for the SET Command
    print('1. Strings: New Options for the SET Command')
    redis_client.set('favoriteflavor', 'Mint Choc Chip')
    print(redis_client.getset('favoriteflavor', 'Vanilla Bean'))  # Mint Choc Chip
    print(redis_client.get('favoriteflavor'))  # Vanilla Bean
    # # Set expire date = 1 day from now.
    # redis_client.set('favoriteflavor', 'ToDelete', {'EX': 60 * 60 * 24})
    # print(await redis_client.ttl('favoriteflavor'))  # Expires: 86400
    # # Set expire date = 12 hours from now
    # redis_client.set('anotherflavor', 'ToDelete', {'PX': 60 * 60 * 12 * 1000})
    # print(await redis_client.ttl('anotherflavor'))  # Expires: 43200
    #
    # # ***********************************
    # # 2) Strings: New Alternatives to the GET Command
    # print('2. Strings: New Alternatives to the GET Command')
    # redis_client.set('onetimecoupon', 'halftimeoff')
    # print(await redis_client.getdel('onetimecoupon'))  # halftimeoff
    # print(await redis_client.getdel('onetimecoupon'))  # None
    # #
    # redis_client.set('limitedtimecoupon', 'freeicecream')
    # # Remove key in 1 hour
    # print(await redis_client.getex('limitedtimecoupon', {'PX': 3600000}))  # freeicecream
    # print(await redis_client.ttl('limitedtimecoupon'))  # 3600
    # # Remove key in 2 hours
    # print(await redis_client.getex('limitedtimecoupon', {'EX': 7200}))
    # print(await redis_client.ttl('limitedtimecoupon'))  # 7200
    # # Remove key in 24 hours from now
    # print(await redis_client.getex('limitedtimecoupon', {'EXAT': int(time.time()) + 60 * 60 * 24}))
    # print(await redis_client.ttl('limitedtimecoupon'))  # 86400
    # # Remove key in 12 hours from now
    # print(await redis_client.getex('limitedtimecoupon', {'PXAT': int(time.time() * 1000) + 60 * 60 * 12 * 1000}))
    # print(await redis_client.ttl('limitedtimecoupon'))  # 43200
    #
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
