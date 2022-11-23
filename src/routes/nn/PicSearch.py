from src.routes.nn.app.proyectos import PicSearch
from fastapi import APIRouter, Request, Form, File

import time

from src.routes.bd import db as _db_

db = _db_()

router_PicSearch = APIRouter()

model_p2s = PicSearch(uri_model='pic2encoder',
                      name='picSearch')


@router_PicSearch.get('/', include_in_schema=False)
async def get_PicSearch():
    return model_p2s.get()


@router_PicSearch.get('/model', include_in_schema=False)
async def get_PicSearch_model():
    return model_p2s.get_model()


def prepare_params(limit, pool):
    if limit is None:
        limit = 9
    if pool is None:
        pool = []
    else:
        """
        IDK how to send a list in a Form from react, with a request from python works fine but its work
        """
        if len(pool) == 1 and pool[0] in ['', '0,1', '1,0', '0', '1']:
            if pool[0] == '':
                pool = [0, 1]
            else:
                pool = pool[0].split(',')
        else:
            for i in pool:
                if i not in [0, 1, '0', '1']:
                    return 'Pool id not allowed (Empty = All, 0 = Danbooru, 1 = Gelbooru)'
    limit = int(limit)
    if 0 < limit <= 32:
        limit = 9
    return limit, pool


def search(image, limit, pool):
    global_time = time.time()
    r, meta = model_p2s.inference_url(image_file=image, limit=limit, pool_id=pool)
    global_time = time.time() - global_time
    return global_time, r, meta


@router_PicSearch.post('/url/')
async def post_PicSearch_by_url(request: Request,
                                image: str = Form(), pool: list = Form(['0', '1']), limit=Form(9)):
    limit, pool = prepare_params(limit=limit, pool=pool)

    try:
        ip = request.headers.get('x-forwarded-for').split(',')[0]
        user_agent = request.headers.get('user-agent')
    except:
        ip = 'localhost'
        user_agent = 'localhost'

    global_time, r, meta = search(image=image, limit=limit, pool=pool)
    if r is None:
        return meta

    if ip != 'localhost':
        meta['source'] = 'UPLOAD'
        meta['ip'] = ip
        meta['ua'] = user_agent
        meta['global_time'] = global_time
        meta['status'] = 'OK'

        db.post_search(meta=meta)

    return r


@router_PicSearch.post('/')
async def post_PicSearch(request: Request,
                         # user_agent: Union[str, None] = Header(default=None, include_in_schema=False),
                         image: bytes = File(), pool: list = Form(['0', '1']), limit=Form(9)):
    limit, pool = prepare_params(limit=limit, pool=pool)

    try:
        ip = request.headers.get('x-forwarded-for').split(',')[0]
        user_agent = request.headers.get('user-agent')
    except:
        ip = 'localhost'
        user_agent = 'localhost'

    global_time, r, meta = search(image=image, limit=limit, pool=pool)
    if r is None:
        return meta

    if ip != 'localhost':
        meta['source'] = 'UPLOAD'
        meta['ip'] = ip
        meta['ua'] = user_agent
        meta['global_time'] = global_time
        meta['status'] = 'OK'
        db.post_search(meta=meta)

    return r


@router_PicSearch.get('/{pool_id}/{item_id}/{limit}')
async def get_PicSearch(pool_id, item_id, limit=9):
    limit = int(str(limit))
    if type(limit) is int and 0 < limit <= 32:

        r = model_p2s.inference_idx(pool_id, item_id, limit=limit)

        return r
    else:
        return 'Limit not allowed'
