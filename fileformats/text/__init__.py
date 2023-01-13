from fileformats.core import File


# General formats
class Plain(File):
    ext = ".txt"


class Csv(File):
    ext = ".csv"


class Tsv(File):
    ext = ".tsv"


class Html(File):
    ext = (".html", ".htm")


class DataSerialization(File):
    "Base class for text-based hierarchical data-serialization formats, e.g. JSON, YAML"


class Json(DataSerialization):
    ext = ".json"


class Yaml(DataSerialization):
    ext = (".yml", ".yaml")
