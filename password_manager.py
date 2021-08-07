from hashlib import sha256
from redis_client import RedisClient

class PasswordManager:
    def __init__(self, client):
        self.client = client # redis_client

    def set(self, user, password):
        hashed_password = str(sha256(password.encode('utf-8')).hexdigest())
        self.client.set(user, hashed_password)

    def check(self, user, password):
        hashed_password = str(sha256(password.encode('utf-8')).hexdigest())
        correct_hash = self.client.get(user)
        return correct_hash and correct_hash.decode() == hashed_password
