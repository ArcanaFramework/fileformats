from fileformats.core import Classifier, ClassifierCategory
from fileformats.generic import File
from fileformats.core.mixin import WithClassifiers


class CategoryA(ClassifierCategory):
    pass


class CategoryB(ClassifierCategory):
    pass


class U(Classifier):

    classifier_category = CategoryA


class V(Classifier):

    classifier_category = CategoryA


class W(V):
    pass


class X(Classifier):

    classifier_category = CategoryB


class Y(X):
    pass


class Z(Y):
    pass


class Classified(WithClassifiers, File):
    classifiers_attr_name = "classifiers"
    classifiers = ()
    ext = ".cls"
