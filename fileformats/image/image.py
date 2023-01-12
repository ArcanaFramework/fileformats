from abc import ABCMeta
from .base import File


# General image formats
class ImageFile(File, metaclass=ABCMeta):
    pass


class Gif(ImageFile):
    ext = "gif"


class Png(ImageFile):
    ext = "png"


class Jpeg(ImageFile):
    ext = "jpg"
