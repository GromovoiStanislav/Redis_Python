import redis


redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

while True:
    message = input("Введите сообщение для отправки (или 'q' для выхода): ")
    if message == 'q':
        break
    redis_client.publish('my_channel', message)
