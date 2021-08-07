
import imp
import re
from embedding_util import *
from recent_likes import RecentLikes
from redis_client import RedisClient
import random

class RecallManager:
    def __init__(self, r_client, impr_container):
        self.id_to_name, self.name_to_id, self.embeddings = read_embeddings("./embeddings")
        self.names = list(self.name_to_id.keys())
        self.index = build_index(self.embeddings)
        self.recent_likes = RecentLikes(r_client)
        self.impr_container = impr_container
        self.feed_cache = []
        self.filter_items = ['cat_168','rabbi3_03', 'cat_102', 'dog2_46', 'cat_218', 'cat_96', 'dog2_73', 'dog2_89', 'dog2_19', 'dog2_51', 'cat2_22']
        self.fix_size = 6

    def hot_recall(self, count = 50):
        re = ['1', '20210808024207', '202108080242071', '2021080802420710', '202108080242072', '202108080242073', '202108080242074', '202108080242075', '202108080242076', '202108080242077', '202108080242078', '202108080242079', 'birds1', 'cat2_78', 'cat_209', 'cat_39', 'cat_5', 'cat_74', 'cat_79', 'dog2_10', 'dog3_08', 'dog4_09', 'dog_29', 'dog_43', 'hamsters_1', 'llama_01', 'llama_12', 'o_4', 'parrot_15', 'rabbi3_06', 'rabbi3_12', 'rabbit2_11', 'rabbit_1']
        random.shuffle(re)
        return re

    def random_recall(self, count = 50):
        return list(set([random.choice(self.names) for _ in range(count)]))

    def i2i_recall(self, uid):
        likes = self.recent_likes.get_likes(uid)[:-6][::-1]
        #print("likes:",likes)
        like_ids = [self.name_to_id[name] for name in likes if name in self.name_to_id]
        results = [self.item2item(item_id) for item_id in like_ids]
        #print('i2i_recall: ', results)
        return results
    
    def item2item(self, item_id):
        return [item for score, item in search(self.index, self.id_to_name, self.embeddings[item_id], 10)[1:]]

    def provide_feed(self, uid, count):
        if not self.feed_cache:
            self.feed_cache = self.snake_merge_recalls([self.hot_recall()]+self.i2i_recall(uid)+[self.random_recall()], self.fix_size, uid)
        if len(self.feed_cache) < count:
            self.feed_cache += self.snake_merge_recalls([self.hot_recall()]+self.i2i_recall(uid)+[self.random_recall()], count - len(self.feed_cache), uid)
        
        imprs = self.impr_container.get_impr(uid)
        #print("I2:",imprs)
        #print("aaaaa", len(self.feed_cache))
        self.feed_cache = [each for each in self.feed_cache if each not in imprs and each not in self.filter_items]
        #print("aaaa", len(self.feed_cache))
        result = self.feed_cache[:count]
        
        #print("lem res", len(result), count)
        self.feed_cache = self.feed_cache[count:]
        if len(self.feed_cache) < self.fix_size//2:
            i2i_recalls = self.i2i_recall(uid)
            self.feed_cache = self.snake_merge_recalls([self.hot_recall()]+i2i_recalls+[self.random_recall()], self.fix_size, uid)
        self.feed_cache = [each for each in self.feed_cache if each not in imprs and each not in self.filter_items]
        
        imprs = self.impr_container.get_impr(uid)
        return result
        
    def snake_merge_recalls(self, recalls, count, uid):
        # recalls = [recall_1, recall_2, recall_3]
        result = []
        visited = set()
        x, y = 0, 0 # y: index in recall_i
        imprs = self.impr_container.get_impr(uid)
        #print("I1:",imprs)
        max_len = max([len(each) for each in recalls])
        count = min(count, sum([len(each) for each in recalls]))
        while len(result) < count and y < max_len:
            if y < len(recalls[x]) and recalls[x][y] not in visited and recalls[x][y] not in imprs and recalls[x][y] not in self.filter_items:
                result.append(recalls[x][y])
                visited.add(recalls[x][y])
            
            x += 1
            if x == len(recalls):
                x = 0
                y += 1
            
        #print("s:", len(result), count)
        return result

            