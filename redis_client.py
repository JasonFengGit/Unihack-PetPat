import redis

class RedisClient:
    def __init__(self, port=7777, db=0, host='localhost'):
        self.client = redis.StrictRedis(host=host, port=port, db=db)

    def get(self, key):
        return self.client.get(key)

    def set(self, key, value):
        return self.client.set(key, value)
