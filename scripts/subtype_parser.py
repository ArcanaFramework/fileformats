import pprint


def extract_mime_info(text):
    mime_info = {}
    lines = text.strip().split("\n")
    key = None
    value = ""
    for line in lines:
        if ":" in line:
            if key is not None:
                mime_info[key] = value.strip()
                value = ""
            key, line = line.split(":", 1)
            key = key.strip().lower().replace(" ", "_")
        value += line + " "
    if key is not None:
        mime_info[key] = value.strip()
    return mime_info


text = """
Name : Leon Bottou

E-mail : leonb&research.att.com

MIME media type name : Image

MIME subtype name : Vendor Tree - vnd.djvu

Required parameters : none

Optional parameters :
none

Encoding considerations :
Binary or base64 is preferred.

Security considerations :
The specified components of the DjVu media format are of a descriptive nature
and provide information that is useful to facilitate viewing and rendering of
images by a recipient.  As such, the DjVu media format does not in itself
create additional security risks, since the fields are not used to induce any
particular behavior by the recipient application.

The DjVu media format has an extensible structure, so that it is theoretically
possible that fields could be defined in the future which could be used to
induce particular actions on the part of the recipient, thus presenting
additional security risks, but this type of capability is not supported in the
referenced DjVu specification.

The DjVu media format does not specify a way to certify the authenticity of a
document.  Such a warranty might be provided by other means, for instance by
signing the complete contents of an email containing DjVu media data.

Interoperability considerations :
DjVu represents document images using multiple layers encoded using different
encoding methods.  Future extensions of the DjVu format might define new
encoding methods that would not be supported by older viewers. DjVu viewer
implementations should detect and report this condition by comparing the DjVu
version number embedded in every DjVu media file with the highest supported
DjVu version number.  They should then decode those layers they can decode and
display these layers only.

Published specification :
* SPECIFICATION OF THE DJVU IMAGE COMPRESSION FORMAT.
  1999-04-29, AT&T Labs.
    This is the original specification of DjVu.
    Copies are available at the following URLs:
        http://www.djvuzone.org/djvu/sci/djvuspec          (DjVu)
        http://djvu.sourceforge.net/specs/djvu2spec.djvu   (DjVu)
        http://djvu.sourceforge.net/specs/djvu2spec.ps.gz  (ps.gz)

* DIFFERENCES BETWEEN DJVU2 and DJVU3
  2001/10/22, Leon Bottou, AT&T Labs
    This is a compilation of the changes between the AT&T
    specification and the currently released
    Lizardtech source code.
        http://djvu.sourceforge.net/specs/djvu3changes.txt (Text)

* DJVU SOURCE CODE
Various open-source implementations (GNU Public License) have been
made available by both AT&T-Labs Research and Lizardtech, Inc.
These files are availablke at the following URL:
        http://sourceforge.net/project/djvu

Applications which use this media :
Imaging, messaging, web publishing.

Additional information :

1. Magic number(s) :

ASCII "FORM" at offset 4 and ASCII "DJVU"
or "DJVM" or "PM44" or "BM44" at offset 12.

2. File extension(s) : djvu, djv
3. Macintosh file type code : DJVU
4. Object Identifiers:

General information on DjVu is available
at http://www.djvuzone.org .

Commercial software is available from Lizardtech, Inc
at http://www.lizardtech.com .

Open source software (encoders, decoders, viewers, utilities)
is available at http://djvu.sourceforge.net .

Person to contact for further information :

1. Name : Leon Bottou
2. E-mail : <leonb&users.sourceforge.net>

Intended usage : Common

DjVu is a web-centric format for distributing documents and images.  DjVu is
designed for distributing scanned documents, digital documents, or
high-resolution pictures. DjVu content downloads faster, displays and renders
faster, looks nicer on a screen, and consume less client resources than
competing formats. DjVu images display instantly and can be smoothly zoomed
and panned with no lengthy re-rendering.  DjVu is used by hundreds of
academic, commercial, governmental, and non-commercial web sites around the
world.

Author/Change controller :
Other contact persons:
- Leon Bottou <leonb&research.att.com>
- Yann Le Cun <yann&research.att.com>
"""

pprint.pprint(extract_mime_info(text))
