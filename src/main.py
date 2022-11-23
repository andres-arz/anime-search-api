from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware

from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.security import APIKeyHeader, APIKeyQuery

from src.routes.nn import Pic2scratch, Pic2Tag, Pic2Encoder_4096, PicSearch, Pic2Tag_v2
from src.routes.util import accessControl as ac

import time
import hashlib

# from keycloak import KeycloakOpenID


hashlib.sha256()
api_key_header = APIKeyHeader(name='token-api-key', auto_error=False)
api_key_query = APIKeyQuery(name='token-api-key', auto_error=False)


async def sessionValidation(request: Request):
    if 'user_token' in request.session:
        if request.session['user_token'] == '368FA16CD3E4107A908B3CC1AA4208341D4AD7C03D440F4D1A6EB8709557BEF9':
            pass


app = FastAPI()

app.include_router(Pic2scratch.router_Pic2scratch,
                   prefix='/pic2scratch',
                   dependencies=[Depends(sessionValidation)])
app.include_router(Pic2Tag.router_Pic2Tag,
                   prefix='/pic2tag',
                   dependencies=[Depends(sessionValidation)])
app.include_router(Pic2Tag_v2.router_Pic2Tag,
                   prefix='/pic2tag_v2',
                   dependencies=[Depends(sessionValidation)])
app.include_router(Pic2Encoder_4096.router_Pic2Encoder_4096,
                   prefix='/pic2encoder',
                   dependencies=[Depends(sessionValidation)])
app.include_router(PicSearch.router_PicSearch,
                   prefix='/picsearch',
                   dependencies=[Depends(sessionValidation)])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]

)


async def accessValidation(request):
    base = 'http://127.0.0.1:8000'
    # base = 'https://arz.ai'
    access_allowwed = [f'{base}/login']
    OK = False
    if request.url in access_allowwed or request.method == 'OPTIONS':
        OK = True
    elif 'token-api-key' in request.headers:
        if request.headers['token-api-key'] == '368FA16CD3E4107A908B3CC1AA4208341D4AD7C03D440F4D1A6EB8709557BEF9':
            # if request.method != 'OPTIONS':
            OK = True
    elif 'token-api-key' in request.query_params:
        if request.query_params['token-api-key'] == '368FA16CD3E4107A908B3CC1AA4208341D4AD7C03D440F4D1A6EB8709557BEF9':
            # if request.method != 'OPTIONS':
            OK = True
    return OK


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    # OK = await accessValidation(request)
    # print(request.headers)
    # print(request.session)
    # print(request.cookies)
    if request.method == 'POST':
        if int(request.headers['content-length']) > 8388608:
            response = ac.returnJson_413()
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response

    if True:
        # print('response')
        response = await call_next(request)
    else:
        response = ac.returnJson_403()
        response.headers['Access-Control-Allow-Origin'] = '*'
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/", include_in_schema=False)
async def root():
    response = RedirectResponse(url='/docs')
    return response


app.add_middleware(SessionMiddleware, secret_key="RULE_THE_WORLD")


@app.get("/login", include_in_schema=True)
async def login(request: Request):
    k = f'time: {time.time()} \t key: RULE THE WORLD'
    # print(k)
    t = hashlib.sha224(k.encode()).hexdigest()
    request.session['user_token'] = '368FA16CD3E4107A908B3CC1AA4208341D4AD7C03D440F4D1A6EB8709557BEF9'
    # request.cookies['user_token'] = t
    # print(t)
    return ac.returnJson_200({'status': 'OK', 'action': 'User is logged in'})


@app.get("/logout", include_in_schema=True)
async def logout(request: Request):
    request.session.clear()
    # request.cookies.clear()
    return ac.returnJson_200({'status': 'OK', 'action': 'User is logged out'})
