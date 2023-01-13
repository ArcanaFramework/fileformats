from fileformats.core.generic import File


# General image formats
class Image(File):
    pass


class Gif(Image):
    ext = ".gif"
    iana = "image/gif"


class Png(Image):
    ext = ".png"
    iana = "image/png"


class Jpeg(Image):
    ext = (".jpg", ".jpeg")
    iana = "image/jpeg"
