from fileformats.core import ClassifierCategory
from fileformats.generic import File
from fileformats.core.mixin import WithClassifiers


class CategoryA(ClassifierCategory):
    pass


class CategoryB(ClassifierCategory):
    pass


class U(CategoryA):
    pass


class V(CategoryA):
    pass


class W(V):
    pass


class X(CategoryB):
    pass


class Y(X):
    pass


class Z(Y):
    pass


class Classified(WithClassifiers, File):
    classifiers_attr_name = "classifiers"
    classifiers = ()
    ext = ".cls"
