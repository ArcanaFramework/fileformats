from .base import Image
from fileformats.core.mixin import WithMagicNumber


class Aces(WithMagicNumber, Image):
    """TODO: or 76 2F 31 01 02 04 00 00 The attribute acesImageContainerFlag has value 1"""

    iana_mime = "image/aces"
    ext = ".exr"
    magic_number = "762f310102000000"


class Apng(WithMagicNumber, Image):
    """"""

    iana_mime = "image/apng"
    ext = ".apng"
    magic_number = "89504e470d0a1a0a"


class Avci(Image):
    """"""

    iana_mime = "image/avci"
    ext = ".avci"


class Avcs(Image):
    """"""

    iana_mime = "image/avcs"
    ext = ".avcs"


class Avif(Image):
    """"""

    iana_mime = "image/avif"
    ext = ".avif"
    alternative_exts = (".heif", ".heifs", ".hif")


class Cgm(Image):
    """"""

    iana_mime = "image/cgm"
    ext = None


class Dicom_rle(Image):
    """"""

    iana_mime = "image/dicom-rle"
    ext = ".drle"


class Dpx(WithMagicNumber, Image):
    """TODO: 0x53445058 (most-significant byte first
    file) or 58 50"""

    iana_mime = "image/dpx"
    ext = ".dpx"
    magic_number = "53445058"


class Emf(Image):
    """TODO: 0x01000000 (little-endian DWORD 0x00000001), corresponding to
    the EMR_HEADER Type field.
    The next field (EMR_HEADER Size) should be at least 88 (little-
    endian DWORD 0x00000050)."""

    iana_mime = "image/emf"
    ext = ".emf"


class Fits(WithMagicNumber, Image):
    """TODO: "SIMPLE = T"  Jeff Uphoff of the National Radio Astronomy Observatory (NRAO) has contributed database entries for the magic number file which is used by the Unix "file" command. Magic number files with these entries are distributed with a variety of Unix-like operating systems. In addition to recognizing a FITS file using the string given above, the Uphoff entries also recognize the data type of the pixels in the PHDU."""

    iana_mime = "image/fits"
    ext = ".fits"
    alternative_exts = (".fit", ".fts", None)
    magic_number = b"SIMPLE = T"


class G3fax(Image):
    """"""

    iana_mime = "image/g3fax"
    ext = None


class Heic(Image):
    """"""

    iana_mime = "image/heic"
    ext = ".heic"


class Heic_sequence(Image):
    """"""

    iana_mime = "image/heic-sequence"
    ext = ".heics"


class Heif(Image):
    """"""

    iana_mime = "image/heif"
    ext = ".heif"


class Heif_sequence(Image):
    """"""

    iana_mime = "image/heif-sequence"
    ext = ".heifs"


class Hej2k(Image):
    """"""

    iana_mime = "image/hej2k"
    ext = ".hej2"


class Hsj2(Image):
    """"""

    iana_mime = "image/hsj2"
    ext = ".hsj2"


class J2c(WithMagicNumber, Image):
    """"""

    iana_mime = "image/j2c"
    ext = ".j2c"
    alternative_exts = (".J2C", ".j2k", ".J2K")
    magic_number = "ff4fff51"


class Jls(Image):
    """"""

    iana_mime = "image/jls"
    ext = ".jls"


class Jp2(WithMagicNumber, Image):
    """"""

    iana_mime = "image/jp2"
    ext = ".jp2"
    alternative_exts = (".jpg2",)
    magic_number = "c6a5020200d0a870a"


class Jph(Image):
    """TODO: See Section 4.4 of RFC 3745"""

    iana_mime = "image/jph"
    ext = ".jph"


class Jphc(WithMagicNumber, Image):
    """"""

    iana_mime = "image/jphc"
    ext = ".jhc"
    magic_number = "ff4fff51"


class Jpm(WithMagicNumber, Image):
    """"""

    iana_mime = "image/jpm"
    ext = ".jpm"
    alternative_exts = (".jpgm",)
    magic_number = "c6a5020200d0a870a"


class Jpx(WithMagicNumber, Image):
    """"""

    iana_mime = "image/jpx"
    ext = ".jpf"
    magic_number = "c6a5020200d0a870a"


class Jxr(WithMagicNumber, Image):
    """TODO: Data begins with a FILE_HEADER( ) data structure, which begins  with a FIXED_FILE_HEADER_II_2BYTES field equal to 0x4949, followed by a FIXED_FILE_HEADER_0XBC_BYTE field equal to 0xBC, followed by a FILE_VERSION_ID which is equal to 1 for the current version of the Recommendation and International Standard (with other values reserved for future use, as modified in additional parts or amendments, by ITU-T or ISO/IEC).  Within the payload data, JPEG XR IMAGE_HEADER( ) data structures begin with a GDI_SIGNATURE, which is a 64-bit syntax element that has the value 0x574D50484F544F00 that corresponds to "WMPHOTO" using the UTF-8 character set encoding specified in Annex D of ISO/IEC 10646, followed by a byte equal to 0."""

    iana_mime = "image/jxr"
    ext = ".jxr"
    magic_number = "4949bc"


class Jxra(Image):
    """"""

    iana_mime = "image/jxrA"
    ext = ".jxra"


class Jxrs(Image):
    """"""

    iana_mime = "image/jxrS"
    ext = ".jxrs"


class Jxs(WithMagicNumber, Image):
    """"""

    iana_mime = "image/jxs"
    ext = ".jxs"
    magic_number = "c4a5853200d0a870a"


class Jxsc(WithMagicNumber, Image):
    """"""

    iana_mime = "image/jxsc"
    ext = ".jxsc"
    magic_number = "ff10ff50"


class Jxsi(Image):
    """"""

    iana_mime = "image/jxsi"
    ext = ".jxsi"


class Jxss(Image):
    """"""

    iana_mime = "image/jxss"
    ext = ".jxss"


class Ktx(WithMagicNumber, Image):
    """"""

    iana_mime = "image/ktx"
    ext = ".ktx"
    magic_number = "ab4b5458203131bb0d0a1a0a"


class Ktx2(WithMagicNumber, Image):
    """"""

    iana_mime = "image/ktx2"
    ext = ".ktx2"
    magic_number = "ab4b5458203230bb0d0a1a0a"


class Naplps(Image):
    """"""

    iana_mime = "image/naplps"
    ext = None


class Prs___btif(Image):
    """TODO: Since BTIF files are an extension of TIFF 6.0, the magic numbers
    are exactly the same as for TIFF 6.0.  The BTIF file
    specification does not introduce any unique magic numbers
    besides what's already present in TIFF 6.0.  (See attached
    specification)"""

    iana_mime = "image/prs.btif"
    ext = ".btif"
    alternative_exts = (".btf",)


class Prs___pti(Image):
    """"""

    iana_mime = "image/prs.pti"
    ext = ".pti"


class Pwg_raster(WithMagicNumber, Image):
    """"""

    iana_mime = "image/pwg-raster"
    ext = None
    magic_number = "52615332"


class Svg__Xml(Image):
    """TODO: Note that the extension ".svgz" is used as an alias for ".svg.gz" [rfc1952] i.e. octet streams of type image/svg+xml subsequently compressed with gzip."""

    iana_mime = "image/svg+xml"
    ext = ".svg"


class T38(Image):
    """"""

    iana_mime = "image/t38"
    ext = ".T38"


class Tiff_fx(Image):
    """"""

    iana_mime = "image/tiff-fx"
    ext = ".TFX"


class Webp(WithMagicNumber, Image):
    """TODO: The first 4 bytes are 0x52, 0x49, 0x46, 0x46 ('RIFF'), followed by 4 bytes for the RIFF chunk size. The next 7 bytes are 0x57, 0x45, 0x42, 0x50, 0x56, 0x50, 0x38 ('WEBPVP8')."""

    iana_mime = "image/webp"
    ext = ".webp"
    magic_number = "52494646"


class Wmf(WithMagicNumber, Image):
    """TODO: (little-endian DWORD 0x9AC6CDD7)"""

    iana_mime = "image/wmf"
    ext = ".wmf"
    magic_number = "d7cdc69a"
