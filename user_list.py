from redis_client import RedisClient
import json

class UserList:
    def __init__(self, client):
        self.client = client # redis client

    def add_user(self, uid):
        user_list = set(self.get_user_list())
        user_list.add(uid)
        impr_history_str = json.dumps(list(user_list))
        self.client.set("user_list", impr_history_str)

    def get_user_list(self):
        res = self.client.get("user_list")
        if not res:
            return []
        return json.loads(res)