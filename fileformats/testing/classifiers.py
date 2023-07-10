import typing as ty
import attrs
from fileformats.core import DataType
from fileformats.generic import File
from fileformats.field import Singular
from fileformats.core.mixin import WithClassifiers


class FileClassifier(DataType):
    pass


class A(FileClassifier):
    pass


class B(FileClassifier):
    pass


class C(FileClassifier):
    pass


class D(FileClassifier):
    pass


class E(C):
    pass


class F(WithClassifiers, File):
    classifiers_attr_name = "content_types"
    content_types = ()
    ext = ".f"


class G(F):
    ext = ".g"


class H(WithClassifiers, File):
    classifiers_attr_name = "content_types"
    content_types = ()
    ext = ".h"

    allowed_classifiers = (A, B, C)


class J(H):
    ext = ".j"


class K(WithClassifiers, File):

    ext = ".k"
    classifiers_attr_name = "new_classifiers_attr"
    new_classifiers_attr = ()
    ordered_classifiers = True


class L(WithClassifiers, File):

    ext = ".l"
    classifiers_attr_name = "new_classifiers_attr"
    new_classifiers_attr = ()
    ordered_classifiers = True


class M(WithClassifiers, File):
    classifiers_attr_name = "content_types"
    content_types = None  # Should be None not ()
    ext = ".m"
    multiple_classifiers = False


class N(WithClassifiers, File):
    classifiers_attr_name = "content_types"
    content_types = ()
    ext = ".n"


@attrs.define
class TestField(Singular):

    value: ty.Any


class P(WithClassifiers, File):
    ext = ".p"
    classifiers_attr_name = "content_types"
    content_types = ()


class Q(WithClassifiers, File):
    ext = ".z"
    classifiers_attr_name = "new_classifiers_attr"
    # MISSING default value for "new_classifiers_attr"


class R(WithClassifiers, File):

    ext = ".r"
    classifiers_attr_name = "new_classifiers_attr"
    new_classifiers_attr = ()
    ordered_classifiers = True
