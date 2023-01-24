from ..core import DataType


class Field(DataType):
    pass


class Text(Field):
    pass


class Integer(Field):
    pass


class Decimal(Field):
    pass


class Boolean(Field):
    pass


class Array(Field):

    item_type = None

    @classmethod
    def __class_getitem__(cls, item_type):
        """Set the content types for a newly created dynamically type"""
        return type(
            f"{item_type.__name__}_{cls.__name__}",
            (cls,),
            {"item_type": item_type},
        )
