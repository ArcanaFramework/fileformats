Quick start
===========

Validate an mp4 audio file's extension and magic number simply by instantiating the class.


.. code-block:: python

   >>> from fileformats.audio import Mp4
   >>> mp4_file = Mp4("/path/to/audio.mp4")  # checks existence, file ext. and magic number
   >>> str(mp4_file)
   "/path/to/audio.mp4"

The created ``FileSet`` object implements ``os.PathLike`` so can used in place of ``str``
or ``pathlib.Path`` in most cases, e.g. when opening files

   >>> fp = open(mp4_file, "rb")
   >>> contents = fp.read()

or in string templates, e.g.

   >>> import subprocess
   >>> subprocess.run(f"cp {mp4_file} new-dest.mp4", shell=True)
