from fileformats.application import Xml


class Drawingml_Chart___Xml(Xml):
    ext = ".chart"
    mime = "application/vnd.openxmlformats-officedocument.drawingml.chart+xml"


class Drawingml_Diagram___Xml(Xml):
    ext = ".diagram"
    mime = "application/vnd.openxmlformats-officedocument.drawingml.diagram+xml"


class Wordprocessingml_Footnotes___Xml(Xml):
    ext = ".footnotes"
    mime = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"
    )


class Wordprocessingml_Endnotes___Xml(Xml):
    ext = ".endnotes"
    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.endnotes+xml"


class Wordprocessingml_Header___Xml(Xml):
    ext = ".header"
    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"


class Wordprocessingml_Footer___Xml(Xml):
    ext = ".footer"
    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"


class Wordprocessingml_Comments___Xml(Xml):
    ext = ".comments"
    mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"


class Presentationml_Slide___Xml(Xml):
    ext = ".sldx"
    mime = "application/vnd.openxmlformats-officedocument.presentationml.slide+xml"


class Presentationml_SlideLayout___Xml(Xml):
    ext = ".sldlayout"
    mime = (
        "application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"
    )


class Presentationml_SlideMaster___Xml(Xml):
    ext = ".sldmaster"
    mime = (
        "application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"
    )


class Presentationml_NotesSlide___Xml(Xml):
    ext = ".sldnotes"
    mime = "application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"


class Presentationml_HandoutMaster___Xml(Xml):
    ext = ".handoutmaster"
    mime = (
        "application/vnd.openxmlformats-officedocument.presentationml.handoutMaster+xml"
    )


class Presentationml_NotesMaster___Xml(Xml):
    ext = ".notesmaster"
    mime = (
        "application/vnd.openxmlformats-officedocument.presentationml.notesMaster+xml"
    )


class Theme___Xml(Xml):
    ext = ".thmx"
    mime = "application/vnd.openxmlformats-officedocument.theme+xml"


class ThemeOverride___Xml(Xml):
    ext = ".thmoverride"
    mime = "application/vnd.openxmlformats-officedocument.themeOverride+xml"


class VmlDrawing(Xml):
    ext = ".vml"
    mime = "application/vnd.openxmlformats-officedocument.vmlDrawing"
