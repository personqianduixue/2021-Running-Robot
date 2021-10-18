import numpy as np
from PIL import Image


class AddGaussNoise():

    def __init__(self, mean, var):
        self.mean = mean
        self.var = var

    def __call__(self, image):
        image = np.array(image, dtype=float)
        image = image / 255
        noise = np.random.normal(self.mean, self.var ** 0.5, image.shape)
        out = image + noise

        out = np.clip(out, 0.0, 1.0)
        out = np.uint8(out * 255)
        out = Image.fromarray(out)

        return out


class LightChange():

    def __init__(self, c):
        self.c = c

    def __call__(self, image):
        image = np.array(image, dtype=float)
        image = image / 255
        out = image * self.c

        out = np.clip(out, 0.0, 1.0)
        out = np.uint8(out * 255)
        out = Image.fromarray(out)

        return out
