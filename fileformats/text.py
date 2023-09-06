from .core import __version__  # noqa
from fileformats.core.mixin import WithMagicNumber
from fileformats.generic import File


class Text(File):
    iana_mime = None
    binary = False


# General formats
class Plain(Text):
    iana_mime = "text/plain"


class TextFile(Text):
    ext = ".txt"


class Csv(Text):
    ext = ".csv"
    iana_mime = "text/csv"


class Tsv(Text):
    ext = ".tsv"
    iana_mime = "text/tab-separated-values"


class Html(Text):
    ext = ".html"
    alternate_exts = (".htm",)
    iana_mime = "text/html"


class Markdown(Text):
    iana_mime = "text/markdown"
    ext = ".md"
    alternate_exts = (".markdown",)


class RestructedText(Text):
    ext = ".rst"
    iana_mime = "text/x-rst"


class _1d_interleaved_parityfec(Text):
    """"""

    iana_mime = "text/1d-interleaved-parityfec"
    ext = None


class CacheManifest(WithMagicNumber, File):
    """"""

    iana_mime = "text/cache-manifest"
    ext = ".appcache"
    alternate_exts = ('"manifest"',)
    magic_number = b"CACHE MANIFEST"


class Calendar(Text):
    """This media type is designed
    for widespread use by Internet calendaring and scheduling
    applications.  In addition, applications in the workflow and
    document management area might find this content-type applicable.
    The iTIP [2446bis], iMIP [2447bis], and CalDAV [RFC4791] Internet
    protocols directly use this media type also."""

    iana_mime = "text/calendar"
    ext = ".ics"
    alternate_exts = (".ifb",)


class Cql(Text):
    """"""

    iana_mime = "text/cql"
    ext = ".CQL"


class CqlExpression(Text):
    """"""

    iana_mime = "text/cql-expression"
    ext = None


class CqlIdentifier(Text):
    """"""

    iana_mime = "text/cql-identifier"
    ext = None


class Css(Text):
    """"""

    iana_mime = "text/css"
    ext = ".css"


class CsvSchema(Text):
    """"""

    iana_mime = "text/csv-schema"
    ext = None


class Dns(Text):
    """DNS-related software, including software storing and using certificates stored in DNS."""

    iana_mime = "text/dns"
    ext = ".soa"
    alternate_exts = (".zone", None)


class Encaprtp(Text):
    """"""

    iana_mime = "text/encaprtp"
    ext = None


class Fhirpath(Text):
    """"""

    iana_mime = "text/fhirpath"
    ext = None


class Flexfec(Text):
    """Multimedia applications that want to improve resiliency against packet loss by sending redundant data in addition to the source media."""

    iana_mime = "text/flexfec"
    ext = None


class Fwdred(Text):
    """It is expected that real-time audio/video, text streaming, and
    conferencing tools/applications that want protection against
    losses of a large number of consecutive frames will be interested
    in using this type."""

    iana_mime = "text/fwdred"
    ext = None


class Gff3(Text):
    """

    TODO: Although no byte sequences can be counted on
    to always be present, GFF3 data in ASCII-compatible character
    sets (including UTF-8) often begin with hexadecimal 23 23 67 66
    66 2d 76 65 72 73 69 6f 6e 20 33 ("##gff-version 3")."""

    iana_mime = "text/gff3"
    ext = ".gff3"


class GrammarRefList(Text):
    """MRCPv2 clients and servers"""

    iana_mime = "text/grammar-ref-list"
    ext = None


class Hl7v2(Text):
    """"""

    iana_mime = "text/hl7v2"
    ext = None


class Javascript(Text):
    """Script interpreters as
    discussed in RFC 9239."""

    iana_mime = "text/javascript"
    ext = ".js"
    alternate_exts = (".mjs",)


class JcrCnd(Text):
    """Used by content repositories that implement the Content Repository For Java API (JCR)"""

    iana_mime = "text/jcr-cnd"
    ext = ".cnd"


class Mizar(Text):
    """"""

    iana_mime = "text/mizar"
    ext = ".miz"


class N3(Text):
    """

    TODO: Notation3 documents may have the strings '@prefix' or '@base' (case dependent) near the
    beginning of the document."""

    iana_mime = "text/n3"
    ext = ".n3"


class Parameters(Text):
    """Applications that use RTSP
    and have additional parameters they like to read and set using the
    RTSP GET_PARAMETER and SET_PARAMETER methods."""

    iana_mime = "text/parameters"
    ext = None


class Parityfec(Text):
    """"""

    iana_mime = "text/parityfec"
    ext = None


class ProvenanceNotation(Text):
    """

    TODO: PROV-N documents may have the strings 'document' near the beginning of the document."""

    iana_mime = "text/provenance-notation"
    ext = ".provn"


class Prs_Fallenstein_Rst(Text):
    """"""

    iana_mime = "text/prs.fallenstein.rst"
    ext = ".txt"
    alternate_exts = (".rst",)


class Prs_Lines_Tag(Text):
    """

    TODO: All tag data streams start Tag-xxx-version - where xxx is the particular tag type."""

    iana_mime = "text/prs.lines.tag"
    ext = ".tag"
    alternate_exts = (None,)


class Prs_Prop_Logic(Text):
    """"""

    iana_mime = "text/prs.prop.logic"
    ext = ".txt"


class Raptorfec(Text):
    """Real-time multimedia applications like video streaming, audio streaming, and video conferencing."""

    iana_mime = "text/raptorfec"
    ext = None


class Red(Text):
    """"""

    iana_mime = "text/RED"
    ext = None


class Rfc822_headers(Text):
    """"""

    iana_mime = "text/rfc822-headers"
    ext = None


class RichText(Text):
    """"""

    iana_mime = "text/rtf"
    ext = ".rtf"


class RtpEncAescm128(Text):
    """"""

    iana_mime = "text/rtp-enc-aescm128"
    ext = None


class Rtploopback(Text):
    """"""

    iana_mime = "text/rtploopback"
    ext = None


class Rtx(Text):
    """"""

    iana_mime = "text/rtx"
    ext = None


class Sgml(Text):
    """"""

    iana_mime = "text/SGML"
    ext = None


class Shaclc(Text):
    """An implementations of SHACLC
    is part of the TopQuadrant SHACL API

    TODO: SHACLC documents will likely have the words
    PREFIX or BASE (case sensitive) near the beginning of the
    document. However, the same words may appear in Turtle and
    SPARQL documents."""

    iana_mime = "text/shaclc"
    ext = ".shaclc"
    alternate_exts = (".shc",)


class Shex(Text):
    """"""

    iana_mime = "text/shex"
    ext = ".shex"


class Spdx(Text):
    """The "charset" parameter is not used for the
    defined subtype because the charset information is transported
    inside the payload."""

    iana_mime = "text/spdx"
    ext = ".spdx"


class Strings(Text):
    """"""

    iana_mime = "text/strings"
    ext = None


class T140(Text):
    """This type is only defined for transfer via
    RTP."""

    iana_mime = "text/t140"
    ext = None


class Troff(Text):
    """"""

    iana_mime = "text/troff"
    ext = None


class Turtle(Text):
    """

    TODO: Turtle documents may have the strings '@prefix' or '@base' (case dependent) near the
    beginning of the document."""

    iana_mime = "text/turtle"
    ext = ".ttl"


class Ulpfec(Text):
    """Multimedia applications that seek to improve resiliency to loss by sending additional data with the media stream."""

    iana_mime = "text/ulpfec"
    ext = None


class UriList(Text):
    """"""

    iana_mime = "text/uri-list"
    ext = ".uris"
    alternate_exts = (".uri",)


class Vcard(Text):
    """They are numerous, diverse,
    and include mail user agents, instant messaging clients, address
    book applications, directory servers, and customer relationship
    management software."""

    iana_mime = "text/vcard"
    ext = ".vcf"
    alternate_exts = (".vcard",)


class Vtt(Text):
    """Web browsers and other video
    players.

    TODO: WebVTT files all begin with one of the following byte sequences (where "EOF" means the end of the file):
    EF BB BF 57 45 42 56 54 54 0A EF BB BF 57 45 42 56 54 54 0D EF BB BF 57 45 42 56 54 54 20 EF BB BF 57 45 42 56 54 54 09 EF BB BF 57 45 42 56 54 54 EOF 57 45 42 56 54 54 0A 57 45 42 56 54 54 0D 57 45 42 56 54 54 20 57 45 42 56 54 54 09 57 45 42 56 54 54 EOF
    (An optional UTF-8 BOM, the ASCII string "WEBVTT", and finally a space, tab, line break, or the end of the file.)"""

    iana_mime = "text/vtt"
    ext = ".vtt"


class Wgsl(Text):
    """"""

    iana_mime = "text/wgsl"
    ext = ".wgsl"


class XmlExternalParsedEntity(Text):
    """"""

    iana_mime = "text/xml-external-parsed-entity"
    ext = ".ent"
    alternate_exts = (None,)


from fileformats.application import (  # noqa
    Json,
    Xml,
    Yaml,
)  # These are sometimes/historically considered part of the text registry so we import them here
