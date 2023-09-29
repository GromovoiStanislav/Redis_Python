import redis
import threading

# Глобальная переменная для сигнала о завершении
exit_signal = threading.Event()


# Функция для прослушивания сообщений Redis
def listen_for_channel_1():
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
    pubsub = redis_client.pubsub()
    pubsub.subscribe('channel-1', 'channel-2')

    # В бесконечном цикле слушаем сообщения
    for message in pubsub.listen():
        if message['type'] == 'message':
            data = message['data'].decode('utf-8')
            channel = message['channel'].decode('utf-8')
            print_message(channel, data)

            if data == 'exit':
                exit_signal.set()
                break


def listen_for_channel_2():
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
    pubsub = redis_client.pubsub()

    # Подписываемся на каналы, соответствующие паттерну
    pubsub.psubscribe('channel-*')  # Подписываемся на все каналы, начинающиеся с 'channel-'

    # В бесконечном цикле слушаем сообщения
    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            data = message['data'].decode('utf-8')
            channel = message['channel'].decode('utf-8')
            pattern = message['pattern'].decode('utf-8')
            print_message(channel, data, pattern)

            if data == 'exit':
                exit_signal.set()
                break


# Основной поток программы

def print_message(channel, message, pattern=""):
    if (pattern == ""):
        print(f"Получено сообщение: {message} из {channel}")
    else:
        print(f"Получено сообщение из канала '{channel}' соответствующего паттерну '{pattern}': {message}")


# Основной поток программы
def main():
    # Создаем и запускаем два отдельных потока для прослушивания каналов
    thread1 = threading.Thread(target=listen_for_channel_1)
    thread2 = threading.Thread(target=listen_for_channel_2)

    thread1.daemon = True  # Помечаем потоки как демоны
    thread2.daemon = True

    thread1.start()
    thread2.start()

    # Ожидаем завершения обоих потоков прослушивания
    thread1.join()
    thread2.join()


if __name__ == "__main__":
    main()
