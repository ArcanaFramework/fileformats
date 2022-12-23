from enum import Enum


class DataQuality(Enum):
    """The quality of a data item. Can be manually specified or set by
    automatic quality control methods
    """

    usable = 100
    noisy = 75
    questionable = 50
    artefactual = 25
    unusable = 0

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    @classmethod
    def default(self):
        return self.questionable
