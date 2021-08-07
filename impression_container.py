from redis_client import RedisClient
import json

class ImpressionContainer:
    def __init__(self, client):
        self.client = client # redis client

    def set_impr(self, uid, gid):
        impr_history = set(self.get_impr(uid))
        impr_history.add(gid)
        impr_history_str = json.dumps(list(impr_history))
        self.client.set("impr:"+str(uid), impr_history_str)

    def get_impr(self, uid):
        res = self.client.get("impr:"+str(uid))
        if not res:
            return []
        return json.loads(res)