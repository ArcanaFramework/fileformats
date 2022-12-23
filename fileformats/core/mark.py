from .utils import CONVERTER_ANNOTATIONS


def converter(output_format):
    def decorator(meth):
        anot = meth.__annotations__
        anot[CONVERTER_ANNOTATIONS] = output_format
        return meth

    return decorator
