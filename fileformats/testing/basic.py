from fileformats.generic import File


class Foo(File):

    ext = ".foo"
    binary = False


class Bar(File):

    ext = ".bar"
    binary = False


class Baz(File):

    ext = ".baz"
    binary = False


class Qux(File):

    ext = ".qux"
    binary = False
