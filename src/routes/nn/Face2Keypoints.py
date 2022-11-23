from src.routes.nn.app.proyectos import Face2Keypoints
from fastapi import APIRouter
from fastapi import File

router_Face2Keypints = APIRouter()

model_f2k = Face2Keypoints(uri_model='face2keypoints',
                           name='face2keypoints')


@router_Face2Keypints.get('/', include_in_schema=False)
async def get_face2keypoints():
    return model_f2k.get()


@router_Face2Keypints.get('/model', include_in_schema=False)
async def get_face2keypoints_model():
    return model_f2k.get_model()


@router_Face2Keypints.post('/')
async def post_face2keypoints(image: bytes = File()):
    re = model_f2k.inference(image)
    return re
