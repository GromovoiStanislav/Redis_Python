import redis
import time


redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

pubsub = redis_client.pubsub()

pubsub.subscribe('my_channel')

for message in pubsub.listen():
    if message['type'] == 'message':
        data = message['data'].decode('utf-8')
        print(f"Получено сообщение: {data}")

        if data == 'exit':
            break

    time.sleep(0.1)  # Пауза в 100 миллисекунд