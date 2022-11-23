import requests
import numpy as np
import time
from src.routes.util.cfg import vectorSearchURL_vector, vectorSearchURL_imageId


class CompressionMethod:
    """
    Auto Encoder in development
    """

    def mean(self, v, f=8, d=np.float32):
        return v.reshape(-1, f).mean(axis=1).astype(d).tolist()


class VectorSearch(CompressionMethod):
    def search(self, vector, limit, pool_id, compress=None):
        js = {
            'vector': compress(vector) if compress is not None else vector.tolist(),
            'limit': limit,
            'pool': pool_id
        }
        st = time.time()
        res = requests.post(vectorSearchURL_vector, json=js)
        return time.time() - st, res.json()

    def search_by_id(self, pool, item, limit):
        js = {
            'id_pool': pool,
            'id_vector': int(item),
            'limit': limit
        }
        st = time.time()
        res = requests.post(vectorSearchURL_imageId, json=js)
        return time.time() - st, res.json()
