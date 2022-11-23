from src.routes.nn.app.proyectos import Pic2Tag
from fastapi import APIRouter, Request, File
import json
import time
from src.routes.bd import db as _db_
db = _db_()

router_Pic2Tag = APIRouter()

tags = json.load(open('./src/routes/nn/app/proyectos/resources/tags.json'))
tags_id = {tags[x]['id']: x for x in tags}

model_p2t = Pic2Tag(uri_model='anime_pic2tag',
                    name='pic2tag',
                    tags_id=tags_id)


@router_Pic2Tag.get('/', include_in_schema=False)
async def get_pic2tag():
    return model_p2t.get()


@router_Pic2Tag.get('/model', include_in_schema=False)
async def get_pic2tag_model():
    return model_p2t.get_model()


@router_Pic2Tag.post('/')
async def post_pic2tag(request: Request,
        image: bytes = File(), threshold: float = 0.4):
    try:
        ip = request.headers.get('x-forwarded-for').split(',')[0]
        user_agent = request.headers.get('user-agent')
    except:
        ip = 'localhost'
        user_agent = 'localhost'
    # print(ip, user_agent)
    global_time = time.time()
    r, meta = model_p2t.inference(image, threshold)
    global_time = time.time() - global_time
    # print(im_hash)
    if ip != 'localhost-':
        meta['source'] = 'UPLOAD'
        meta['ip'] = ip
        meta['ua'] = user_agent
        meta['global_time'] = global_time
        meta['status'] = 'OK'
        db.post_tagging(meta=meta)

    return r
