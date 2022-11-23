from src.routes.nn.app.proyectos import Pic2Encoder
from fastapi import APIRouter
from fastapi import File

router_Pic2Encoder_4096 = APIRouter()

model_p2e = Pic2Encoder(uri_model='pic2encoder',
                        name='Pic2Encoder_2048')


@router_Pic2Encoder_4096.get('/', include_in_schema=False)
async def get_pic2encoder():
    return model_p2e.get()


@router_Pic2Encoder_4096.get('/model', include_in_schema=False)
async def get_pic2encoder_model():
    return model_p2e.get_model()


@router_Pic2Encoder_4096.post('/')
async def post_Pic2Encoder_4096(image: bytes = File()):
    re = model_p2e.inference(image)
    return re
