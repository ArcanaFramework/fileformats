"""Only required to hold the automatically generated version for the "core" extras"""

import types
import inspect
from ._version import __version__


def check_optional_dependency(module: types.ModuleType | None) -> None:
    if module is None:
        frame = inspect.currentframe()
        prev_frame = None
        while frame:
            # Find the frame where the extra_implementation method was called
            if frame.f_code.co_name == "extra_implementation":
                return frame.f_locals["workflow"]  # local var "workflow" in construct
            prev_frame = frame
            frame = frame.f_back
        raise ImportError(
            f"The optional dependency '{module.__name__}' is not installed required to use the "
            "{} method. It is "
        )


__all__ = ["__version__"]
