from redis_client import RedisClient
import json

class RecentLikes:
    def __init__(self, client):
        self.client = client # redis client

    def add_like(self, uid, gid):
        likes = self.get_likes(uid)
        likes.append(gid)
        likes = json.dumps(list(likes))
        self.client.set("likes:"+str(uid), likes)

    def get_likes(self, uid):
        res = self.client.get("likes:"+str(uid))
        if not res:
            return []
        return json.loads(res)