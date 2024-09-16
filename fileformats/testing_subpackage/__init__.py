from fileformats.core import Classifier, DataType
from fileformats.core.mixin import WithClassifiers


class SubpackageClassified(WithClassifiers, DataType):
    classifiers_attr_name = "classifiers"
    classifiers = ()
    allowed_classifiers = (Classifier,)
    generically_classifiable = False


class Psi(DataType):
    pass


class Zeta(Classifier):
    pass


class Theta(Classifier):
    pass
