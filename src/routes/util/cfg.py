import json

cfg = json.load(open('./src/config.json'))

vectorSearchURL_vector = cfg['vectorSearchURL_vector']
# vectorSearchURL_vector = 'http://127.0.0.1:8001/picsearch'
vectorSearchURL_imageId = cfg['vectorSearchURL_imageId']
# vectorSearchURL_imageId = 'http://127.0.0.1:8001/picsearch/by_id'
imageServerURL_224 = cfg['imageServerURL_224']
imageServerURL_512 = cfg['imageServerURL_512']

connectionDB = cfg['connectionDB']

BackEnd_API = cfg['BackEnd_API']
