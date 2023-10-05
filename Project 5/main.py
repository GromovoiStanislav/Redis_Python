import json
import sqlite3

import redis


def get_users():
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cache_value = redis_client.get("users:friends")
    if cache_value is not None:
        return json.loads(cache_value)

    cursor.execute("SELECT id, name FROM users;")
    result = cursor.fetchall()
    redis_client.set("users:friends", json.dumps(result), ex=30)

    conn.close()
    redis_client.close()
    return result


if __name__ == "__main__":
    print(get_users())
