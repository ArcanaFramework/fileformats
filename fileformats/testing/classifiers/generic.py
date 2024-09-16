from fileformats.core import Classifier
from fileformats.generic import UnicodeFile
from fileformats.core.mixin import WithClassifiers


class CategoryA(Classifier):
    pass


class CategoryB(Classifier):
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


class Classified(WithClassifiers, UnicodeFile):
    classifiers_attr_name = "classifiers"
    classifiers = ()
    exclusive_classifiers = (CategoryA, CategoryB)
    ext = ".cls"
