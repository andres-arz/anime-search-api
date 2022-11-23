import io
import threading

from PIL import Image
import numpy as np
import requests
from io import BytesIO
from src.routes.nn.app.model.util import img_util as util
from src.routes.nn.app.model.tech.api import ModelApi
from src.routes.util.vectorSearch import VectorSearch
from src.routes.util.cfg import imageServerURL_224, imageServerURL_512


def load_image(image_file, width=512, height=512, deepcolor=3):
    ib = None
    if type(image_file) == bytes:
        ib = image_file
    elif type(image_file) == str:
        try:
            rq = requests.get(image_file, timeout=2, stream=True)

            if int(rq.headers['Content-Length']) > 8000000 or 'image' not in rq.headers['Content-Type']:
                return ib, 'Invalid url'

            ib = BytesIO(rq.content).read()
        except Exception as e:
            print(e)
            return ib, 'Invalid url'

    # Load image from bytes (troubles with OpenCV)
    img = Image.open(io.BytesIO(ib)).convert('RGB')
    return util.img2ndarray(img=img, width=width, height=height, deepcolor=deepcolor)


class Matematika(ModelApi):
    """
    In development
    - Handwriting limit calculus OCR (DONE ACC: 95.6%)
    - Autocorrector for the results from the model
        - U-Net (DONE ACC: 98.6%) fastest
        - LSTM (DONE ACC: 99.2) too slow
        - BI-LSTM (DONE ACC 99.2) too slow
        - Attention (in development)
    - Matematika solver (in research)
    """

    def inference(self, image_file):
        pass


class Face2Keypoints(ModelApi):
    """
    Generate a 3d key points map from a picture of people
    Discharged, not enough resources in the server
    """

    def inference(self, image_file):
        if type(image_file) != bytes:
            image_bytes = image_file.read()
        else:
            image_bytes = image_file

        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        _, img = util.img2ndarray(img=img, width=224, height=224, deepcolor=3)

        # print(img.shape)
        _, resp = self.forward(img)

        P = resp.reshape(68, 3) * 224

        jawPoints = [0, 17]
        rigthEyebrowPoints = [17, 22]
        leftEyebrowPoints = [22, 27]
        noseRidgePoints = [27, 31]
        noseBasePoints = [31, 36]
        rightEyePoints = [36, 42]
        leftEyePoints = [42, 48]
        outerMouthPoints = [48, 60]
        innerMouthPoints = [60, 68]

        listOfAllConnectedPoints = [jawPoints, rigthEyebrowPoints, leftEyebrowPoints,
                                    noseRidgePoints, noseBasePoints,
                                    rightEyePoints, leftEyePoints, outerMouthPoints, innerMouthPoints]

        data = []

        for conPts in listOfAllConnectedPoints:
            xPts = P[conPts[0]:conPts[-1], 0]
            yPts = P[conPts[0]:conPts[-1], 1]
            zPts = P[conPts[0]:conPts[-1], 2]

            toInt = lambda x: [int(k) for k in x]

            data.append({
                'x': toInt(xPts),
                'y': toInt(yPts),
                'z': toInt(zPts),
                'type': 'scatter3d',
                'mode': 'lines'
            })

        return data


class Pic2scratch(ModelApi):
    """
    Deprecated, that was the first step to make a pix2pix imagen colored
    """

    def inference(self, image_file):
        if type(image_file) != bytes:
            image_bytes = image_file.read()
        else:
            image_bytes = image_file

        x = Image.open(io.BytesIO(image_bytes)).convert('RGB')

        x = np.array(x.getdata()).reshape((x.size[1], x.size[0], 3)).astype(np.float32)[..., ::-1]
        x = x[:, :, ::-1]
        tx, ty = x.shape[:2]

        if tx % 2 == 1:
            x = x[:-1]
        if ty % 2 == 1:
            x = x[:, :-1]

        tx = tx // 2
        ty = ty // 2

        lm = 32

        i1, i2 = x[tx - lm:], x[:tx + lm]
        i3, i4 = i1[:, ty - lm:], i2[:, ty - lm:]
        i1, i2 = i1[:, :ty + lm], i2[:, :ty + lm]

        def getImg(img):
            sh = img.shape[:2][::-1]
            o, img = util.img2ndarray(img=Image.fromarray(img.astype(np.uint8)), width=512, height=512,
                                      deepcolor=3)
            img = img * 2 - 1
            return o, img, sh

        offset = []
        imgs = []
        sh = []

        for p in [i1, i2, i3, i4]:
            o, i, s = getImg(p)
            offset.append(o)
            imgs.append(i)
            sh.append(s)

        _, res = self.forward(np.array(imgs))  # .astype(np.float32)
        res = res * 0.5 + 0.5

        res_f = []
        for r, o, s in zip(res, offset, sh):
            if o[0] == 0:
                t = r[:, o[1]:-o[1]]
            else:
                t = r[o[0]:-o[0], :]

            t = Image.fromarray((t * 255).astype(np.uint8)).resize(s)
            # res = cv2.resize(res, sh)
            t = np.array(t.getdata()).reshape(s[1], s[0], 3)
            res_f.append(t)

        # i1 = foward(i1)[lm:, :-lm]
        # i2 = foward(i2)[:-lm, :-lm]
        # i3 = foward(i3)[lm:, lm:]
        # i4 = foward(i4)[:-lm, lm:]

        i1 = res_f[0][lm:, :-lm]
        i2 = res_f[1][:-lm, :-lm]
        i3 = res_f[2][lm:, lm:]
        i4 = res_f[3][:-lm, lm:]

        res = np.concatenate((np.concatenate((i2, i4), axis=1),
                              np.concatenate((i1, i3), axis=1)), axis=0)

        # res = (res - res.min()) / (res.max() - res.min())

        return res

    __call__ = inference


class Pic2Tag(ModelApi):
    def __init__(self, name, uri_model, tags_id):
        super().__init__(name, uri_model)
        self.tags_id = tags_id

    def inference(self, image_file, threshold):
        _, img = load_image(image_file=image_file)

        time_inference, resp = self.forward(img[None])
        resp = resp[0]
        a = [(x, y) for x, y in enumerate(resp) if y >= threshold]
        data = [[self.tags_id[x], float(y)] for x, y in a]
        data.sort(key=lambda x: x[1])

        data_dc = [{'tag': t, 'score': s} for t, s in data[::-1]]

        meta = {
            'time_inference': time_inference,
            'result': resp.tolist(),
        }

        return data_dc, meta


class Pic2Encoder(ModelApi):
    def inference(self, image_file):
        _, img = load_image(image_file)
        if type(img) == str:
            return img

        _, resp = self.forward(img[None])  # .astype(np.float32)

        return resp.tolist()


class PicSearch(ModelApi):

    def __init__(self, name, uri_model):
        super().__init__(name, uri_model)
        self.search = VectorSearch()

    def prepare_response(self, payloads, limit):

        ok = [{'img': '', 'score': -1} for _ in range(limit)]

        meta_result = [{} for _ in range(limit)]

        def resp_img(i, idx):
            meta_result[idx] = {
                'id_image': i[0],
                'status': ['NOT FOUND IN POOL'],
                'score': -1,
                'id_source': 2
            }
            ok[idx]['id'] = i[0]
            try:
                meta_result[idx]['score'] = i[1]
                meta_result[idx]['status'] = ['OK']

                if i[-1] == 'danbooru':
                    ok[idx]['source'] = f'https://danbooru.donmai.us/posts/{i[0]}'
                    pool_id = 0
                else:
                    ok[idx]['source'] = f'https://gelbooru.com/index.php?page=post&s=view&id={i[0]}'
                    pool_id = 1

                ok[idx]['preview'] = f'{imageServerURL_224}/{pool_id}/{i[0]}'
                ok[idx]['img'] = f'{imageServerURL_512}/{pool_id}/{i[0]}'
                ok[idx]['score'] = i[1]

                ok[idx]['pool'] = i[-1]

            except Exception as e:
                print(e)

        th = []
        for idx, i in enumerate(payloads):
            th.append(threading.Thread(target=resp_img, args=[i, idx]))
            th[-1].start()
        for i in th:
            i.join()

        return ok, meta_result

    def inference_url(self, image_file, limit=9, pool_id=-1):
        _, img = load_image(image_file)
        if type(img) == str:
            return None, img

        meta = {}

        time_embdeing, resp = self.forward(img[None])
        meta['time_embdeing'] = time_embdeing

        meta['query'] = resp[0].tolist()
        time_search, payloads = self.search.search(vector=resp[0],
                                                   limit=limit,
                                                   pool_id=pool_id,
                                                   compress=self.search.mean)
        meta['time_search'] = time_search

        ok, meta_result = self.prepare_response(payloads=payloads, limit=limit)

        meta['results'] = meta_result
        return ok, meta

    def inference_idx(self, pool_id, item_id, limit=9):
        _, payloads = self.search.search_by_id(pool=int(pool_id),
                                               item=item_id,
                                               limit=limit)

        ok, _ = self.prepare_response(payloads=payloads, limit=limit)

        return ok
