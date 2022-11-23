import numpy as np
import io
import zlib
import requests
import time
from src.routes.util.cfg import BackEnd_API


def compress_nparr(nparr):
    bytestream = io.BytesIO()
    np.save(bytestream, nparr)
    uncompressed = bytestream.getvalue()
    compressed = zlib.compress(uncompressed)
    return compressed  # , len(uncompressed), len(compressed)


def uncompress_nparr(bytestring):
    return np.load(io.BytesIO(zlib.decompress(bytestring)))


uri = BackEnd_API


class ModelApi:
    def __init__(self, name, uri_model):
        self.model_name = name
        self.uri_model = uri_model

    def forward(self, x):
        # print(type(x))
        obj = compress_nparr(x)
        # print(obj)
        st = time.time()
        response = requests.post(uri + self.uri_model, files={'obj': obj})
        # print(response.content)
        response = uncompress_nparr(response.content)
        return time.time() - st, response

    def get(self):
        return requests.get(uri + self.uri_model).content

    def get_model(self):
        return requests.get(uri + self.uri_model + '/model').content
