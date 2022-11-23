from src.routes.nn.app.proyectos import Pic2scratch
from fastapi import APIRouter
from fastapi import File
import base64
from PIL import Image
import numpy as np
import io

router_Pic2scratch = APIRouter()

model_p2s = Pic2scratch(uri_model='pic2scratch',
                        name='pic2scratch')


@router_Pic2scratch.get('/', include_in_schema=False)
async def get_pic2scratch():
    return model_p2s.get()


@router_Pic2scratch.get('/model', include_in_schema=False)
async def get_pic2scratch_model():
    return model_p2s.get_model()


@router_Pic2scratch.post('/')
async def post_pic2scratch(image: bytes = File()):
    re = model_p2s(image)
    re = re.astype(np.uint8)
    im_pil = Image.fromarray(re)
    buf = io.BytesIO()
    im_pil.save(buf, format='PNG')
    byte_im = buf.getvalue()
    # print(byte_im[0])
    my_string = base64.b64encode(byte_im)
    # return Response(content=byte_im, media_type="image/png")
    return my_string
