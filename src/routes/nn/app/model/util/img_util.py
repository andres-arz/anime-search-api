import numpy as np


# import cv2


def resize(img, w, h, deepcolor):
    p = img.size / np.array([w, h])
    s = img.size
    r = s / (p[0] if s[0] > s[1] else p[1])

    img = img.resize((int(r[0]), int(r[1])))
    img = np.array(img.getdata()).reshape(img.size[1], img.size[0], deepcolor)
    re = np.zeros((h, w, deepcolor))
    offset = np.array((np.array(re.shape[:2]) - np.array(img.shape[:2])) // 2, dtype=np.int32)
    re[offset[0]:offset[0] + img.shape[0], offset[1]:offset[1] + img.shape[1]] = img

    return offset, re


# def resize(img, w=256, h=256):
#     p = img.shape[:2] / np.array([w, h])
#     s = img.shape[:2]
#     r = s / (p[0] if s[0] > s[1] else p[1])
#
#     img = cv2.resize(img, (int(r[1]), int(r[0])))
#
#     re = np.zeros((w, h, 3))
#
#     if min(re.shape[:2]) > min(img.shape[:2]):
#         offset = np.array((np.array(re.shape[:2]) - np.array(img.shape[:2])) / 2, dtype=np.int32)
#     else:
#         p = np.array(img.shape[:2]) / min(w, h)
#         s = img.shape[:2]
#         r = s / (p[0] if s[0] > s[1] else p[1])
#
#         img = cv2.resize(img, (int(r[1]), int(r[0])))
#         offset = np.array((np.array(re.shape[:2]) - np.array(img.shape[:2])) / 2, dtype=np.int32)
#     re[offset[0]:offset[0] + img.shape[0], offset[1]:offset[1] + img.shape[1]] = img
#     # print(re)
#     return offset, re


def normalize(input_image):
    # input_image = (input_image - input_image.min()) / (input_image.max() - input_image.min())
    input_image = input_image / 255
    # input_image = (input_image / 127.5) - 1
    return input_image


def load(image_file, w, h, deepcolor):
    offset, input_image = resize(image_file, w, h, deepcolor=deepcolor)

    # print(input_image.shape)
    # print(input_image.mean())
    input_image = normalize(input_image)  # [..., ::-1]

    # cv2.imshow('o', input_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    input_image = np.expand_dims(input_image, axis=0)
    return offset, input_image


def img2ndarray(img, width, height, deepcolor):
    return load(image_file=img, w=width, h=height, deepcolor=deepcolor)
