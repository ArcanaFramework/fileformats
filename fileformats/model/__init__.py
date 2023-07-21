from ..core import __version__
from ..core.mixin import WithMagicNumber
from fileformats.generic import File


class Model(File):

    iana_mime = None


class _3mf(Model):
    """3D modeling and slicing  software"""

    iana_mime = "model/3mf"
    ext = ".3mf"


class E57(Model):
    """"""

    iana_mime = "model/e57"
    ext = None


class GltfBinary(Model):
    """"""

    iana_mime = "model/gltf-binary"
    ext = None


class Gltf__Json(Model):
    """"""

    iana_mime = "model/gltf+json"
    ext = ".gltf"


class Jt(Model):
    """"""

    iana_mime = "model/JT"
    ext = ".jt"


class Iges(Model):
    """"""

    iana_mime = "model/iges"
    ext = None


class Mtl(Model):
    """"""

    iana_mime = "model/mtl"
    ext = ".mtl"


class Obj(Model):
    """"""

    iana_mime = "model/obj"
    ext = ".obj"


class Prc(WithMagicNumber, File):
    """"""

    iana_mime = "model/prc"
    ext = ".prc"
    magic_number = "505243"


class Step(Model):
    """"""

    iana_mime = "model/step"
    ext = ".p21"
    alternate_exts = (".stp", ".step", ".stpnc", ".210")


class Step__Xml(Model):
    """"""

    iana_mime = "model/step+xml"
    ext = ".stpx"


class Step__Zip(Model):
    """"""

    iana_mime = "model/step+zip"
    ext = ".stpz"


class StepXml__Zip(Model):
    """"""

    iana_mime = "model/step-xml+zip"
    ext = ".stpxz"


class Stl(Model):
    """"""

    iana_mime = "model/stl"
    ext = ".stl"


class U3d(WithMagicNumber, File):
    """"""

    iana_mime = "model/u3d"
    ext = ".u3d"
    magic_number = "55334400"


class X3d_vrml(WithMagicNumber, File):
    """"""

    iana_mime = "model/x3d-vrml"
    ext = ".x3dv"
    magic_number = b"#X3D"


class X3d__Fastinfoset(Model):
    """"""

    iana_mime = "model/x3d+fastinfoset"
    ext = ".x3db"


class X3d__Xml(Model):
    """"""

    iana_mime = "model/x3d+xml"
    ext = ".x3d"
