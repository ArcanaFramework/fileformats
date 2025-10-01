from fileformats.application import Document, Zip


class Wordprocessingml_Document(Zip, Document):
    ext = ".docx"


class Wordprocessingml_Template(Zip, Document):
    ext = ".dotx"
