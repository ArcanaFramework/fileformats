from fileformats.core import Classifier, DataType
from fileformats.core.mixin import WithClassifiers


class SubpackageClassified(WithClassifiers, DataType):
    classifiers_attr_name = "classifiers"
    classifiers = ()
    multiple_classifiers = True
    allowed_classifiers = (Classifier,)
    generically_classifies = False


class Psi(DataType):
    pass


class Zeta(Classifier):
    pass


class Theta(Classifier):
    pass
