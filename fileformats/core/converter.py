from __future__ import annotations
import attrs
from pydra.engine import Workflow
import pydra.engine.core


@attrs.define
class ConverterWrapper:
    """Wraps a converter task in a workflow so that the in_file and out_file names can
    be mapped onto their standardised names, "in_file" and "out_file" if necessary
    """

    task_spec: pydra.engine.core.TaskBase
    in_file: str = None
    out_file: str = None

    def __call__(self, name=None, **kwargs):
        if name is None:
            name = f"{self.task.__name__}_wrapper"
        wf = Workflow(name=name, lzin=["in_file"] + list(kwargs))
        kwargs[self.in_file] = wf.lzin.in_file
        wf.add(self.task_spec(name="task", **kwargs))
        wf.set_output([("out_file", getattr(wf.task.lzout, self.out_file))])
        return wf
