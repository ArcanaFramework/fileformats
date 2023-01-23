class Field(DataType):
    pass


class String(Field):
    pass


class Integer(Field):
    pass


class Float(Field):
    pass


class Boolean(Field):
    pass


class Array(Field):

    item_type = None
