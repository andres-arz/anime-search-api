from starlette.responses import JSONResponse
import base64
import json


def imageRequest(session):
    return 'user_token' in session


def tokenValidation(token):
    return True


def access(session):
    if 'session' in session:
        sn = session['session'].split('.')[0]
        # print(sn)
        sn = sn
        sn = sn.encode('ascii')
        sn = base64.b64decode(sn)
        sn = sn.decode('ascii')
        sn = json.loads(sn)

        if 'user_token' in sn:
            return tokenValidation(sn['user_token'])

    return False


def returnJson_403(data=None):
    if data is None:
        data = {'status': 'Error', 'action': 'Access forbidden, access token required or token invalid'}
    return JSONResponse(content=data, media_type="application/json", status_code=403)


def returnJson_413(data=None):
    if data is None:
        data = {'status': 'Error', 'action': 'Max sie 8 mib'}
    return JSONResponse(content=data, media_type="application/json", status_code=413)


def returnJson_200(data=None):
    if data is None:
        data = {'status': 'OK', 'action': 'Action successfull'}
    return JSONResponse(content=data, media_type="application/json", status_code=200)
