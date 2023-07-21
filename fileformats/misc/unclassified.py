from fileformats.generic import File
from fileformats.core.mixin import WithMagicNumber
from fileformats.serialization import Xml, Json


class _1dInterleavedParityfec(File):
    """"""

    iana_mime = "application/1d-interleaved-parityfec"
    ext = None


class _3gpdashQoeReport__Xml(Xml):
    """"""

    iana_mime = "application/3gpdash-qoe-report+xml"
    ext = None


class _3gpphal__Json(Json):
    """"""

    iana_mime = "application/3gppHal+json"
    ext = None


class _3gpphalforms__Json(Json):
    """"""

    iana_mime = "application/3gppHalForms+json"
    ext = None


class _3gppIms__Xml(Xml):
    """"""

    iana_mime = "application/3gpp-ims+xml"
    ext = None


class A2l(File):
    """"""

    iana_mime = "application/A2L"
    ext = ".a2l"


class Ace__Cbor(File):
    """"""

    iana_mime = "application/ace+cbor"
    ext = None


class Ace__Json(Json):
    """"""

    iana_mime = "application/ace+json"
    ext = None


class Activemessage(File):
    """"""

    iana_mime = "application/activemessage"
    ext = None


class Activity__Json(Json):
    """"""

    iana_mime = "application/activity+json"
    ext = None


class Aif__Cbor(File):
    """"""

    iana_mime = "application/aif+cbor"
    ext = None


class Aif__Json(Json):
    """"""

    iana_mime = "application/aif+json"
    ext = None


class AltoCdni__Json(Json):
    """"""

    iana_mime = "application/alto-cdni+json"
    ext = None


class AltoCdnifilter__Json(Json):
    """"""

    iana_mime = "application/alto-cdnifilter+json"
    ext = None


class AltoCostmap__Json(Json):
    """"""

    iana_mime = "application/alto-costmap+json"
    ext = None


class AltoCostmapfilter__Json(Json):
    """"""

    iana_mime = "application/alto-costmapfilter+json"
    ext = None


class AltoDirectory__Json(Json):
    """"""

    iana_mime = "application/alto-directory+json"
    ext = None


class AltoEndpointprop__Json(Json):
    """"""

    iana_mime = "application/alto-endpointprop+json"
    ext = None


class AltoEndpointpropparams__Json(Json):
    """"""

    iana_mime = "application/alto-endpointpropparams+json"
    ext = None


class AltoEndpointcost__Json(Json):
    """"""

    iana_mime = "application/alto-endpointcost+json"
    ext = None


class AltoEndpointcostparams__Json(Json):
    """"""

    iana_mime = "application/alto-endpointcostparams+json"
    ext = None


class AltoError__Json(Json):
    """"""

    iana_mime = "application/alto-error+json"
    ext = None


class AltoNetworkmapfilter__Json(Json):
    """"""

    iana_mime = "application/alto-networkmapfilter+json"
    ext = None


class AltoNetworkmap__Json(Json):
    """"""

    iana_mime = "application/alto-networkmap+json"
    ext = None


class AltoPropmap__Json(Json):
    """"""

    iana_mime = "application/alto-propmap+json"
    ext = None


class AltoPropmapparams__Json(Json):
    """"""

    iana_mime = "application/alto-propmapparams+json"
    ext = None


class AltoUpdatestreamcontrol__Json(Json):
    """"""

    iana_mime = "application/alto-updatestreamcontrol+json"
    ext = None


class AltoUpdatestreamparams__Json(Json):
    """"""

    iana_mime = "application/alto-updatestreamparams+json"
    ext = None


class Aml(File):
    """"""

    iana_mime = "application/AML"
    ext = ".aml"


class AndrewInset(File):
    """"""

    iana_mime = "application/andrew-inset"
    ext = None


class Applefile(File):
    """"""

    iana_mime = "application/applefile"
    ext = None


class At__Jwt(File):
    """"""

    iana_mime = "application/at+jwt"
    ext = None


class Atf(File):
    """"""

    iana_mime = "application/ATF"
    ext = ".atf"


class Atfx(File):
    """"""

    iana_mime = "application/ATFX"
    ext = ".atfx"


class Atom__Xml(Xml):
    """"""

    iana_mime = "application/atom+xml"
    ext = ".atom"


class Atomcat__Xml(Xml):
    """"""

    iana_mime = "application/atomcat+xml"
    ext = ".atomcat"


class Atomdeleted__Xml(Xml):
    """"""

    iana_mime = "application/atomdeleted+xml"
    ext = ".atomdeleted"


class Atomicmail(File):
    """"""

    iana_mime = "application/atomicmail"
    ext = None


class Atomsvc__Xml(Xml):
    """"""

    iana_mime = "application/atomsvc+xml"
    ext = ".atomsvc"


class AtscDwd__Xml(Xml):
    """"""

    iana_mime = "application/atsc-dwd+xml"
    ext = ".dwd"


class AtscDynamicEventMessage(File):
    """"""

    iana_mime = "application/atsc-dynamic-event-message"
    ext = None


class AtscHeld__Xml(Xml):
    """"""

    iana_mime = "application/atsc-held+xml"
    ext = ".held"


class AtscRdt__Json(Json):
    """"""

    iana_mime = "application/atsc-rdt+json"
    ext = None


class AtscRsat__Xml(Xml):
    """"""

    iana_mime = "application/atsc-rsat+xml"
    ext = ".rsat"


class Atxml(File):
    """"""

    iana_mime = "application/ATXML"
    ext = ".atxml"


class AuthPolicy__Xml(Xml):
    """"""

    iana_mime = "application/auth-policy+xml"
    ext = ".apxml"


class AutomationmlAml__Xml(Xml):
    """"""

    iana_mime = "application/automationml-aml+xml"
    ext = ".aml"


class AutomationmlAmlx__Zip(File):
    """"""

    iana_mime = "application/automationml-amlx+zip"
    ext = ".amlx"


class BacnetXdd__Zip(WithMagicNumber, File):
    """"""

    iana_mime = "application/bacnet-xdd+zip"
    ext = ".xdd"
    magic_number = b"PK\003\004"


class BatchSmtp(File):
    """"""

    iana_mime = "application/batch-SMTP"
    ext = None


class Beep__Xml(Xml):
    """"""

    iana_mime = "application/beep+xml"
    ext = None


class Calendar__Json(Json):
    """"""

    iana_mime = "application/calendar+json"
    ext = None


class Calendar__Xml(Xml):
    """"""

    iana_mime = "application/calendar+xml"
    ext = ".xcs"


class CallCompletion(File):
    """"""

    iana_mime = "application/call-completion"
    ext = None


class Cals_1840(File):
    """"""

    iana_mime = "application/CALS-1840"
    ext = None


class Captive__Json(Json):
    """"""

    iana_mime = "application/captive+json"
    ext = None


class Cbor(File):
    """"""

    iana_mime = "application/cbor"
    ext = ".cbor"


class CborSeq(File):
    """"""

    iana_mime = "application/cbor-seq"
    ext = None


class Cccex(File):
    """"""

    iana_mime = "application/cccex"
    ext = ".c3ex"


class Ccmp__Xml(Xml):
    """"""

    iana_mime = "application/ccmp+xml"
    ext = ".ccmp"


class Ccxml__Xml(Xml):
    """"""

    iana_mime = "application/ccxml+xml"
    ext = None


class Cda__Xml(Xml):
    """"""

    iana_mime = "application/cda+xml"
    ext = None


class Cdfx__Xml(Xml):
    """"""

    iana_mime = "application/CDFX+XML"
    ext = ".cdfx"


class CdmiCapability(File):
    """"""

    iana_mime = "application/cdmi-capability"
    ext = ".cdmia"


class CdmiContainer(File):
    """"""

    iana_mime = "application/cdmi-container"
    ext = ".cdmic"


class CdmiDomain(File):
    """"""

    iana_mime = "application/cdmi-domain"
    ext = ".cdmid"


class CdmiObject(File):
    """"""

    iana_mime = "application/cdmi-object"
    ext = ".cdmio"


class CdmiQueue(File):
    """"""

    iana_mime = "application/cdmi-queue"
    ext = ".cdmiq"


class Cdni(File):
    """"""

    iana_mime = "application/cdni"
    ext = None


class Cea(File):
    """"""

    iana_mime = "application/CEA"
    ext = ".cea"


class Cea_2018__Xml(Xml):
    """"""

    iana_mime = "application/cea-2018+xml"
    ext = ".xml"


class Cellml__Xml(Xml):
    """"""

    iana_mime = "application/cellml+xml"
    ext = ".cellml"
    alternative_exts = (".xml", ".cml", None)


class Cfw(File):
    """"""

    iana_mime = "application/cfw"
    ext = None


class City__Json(Json):
    """"""

    iana_mime = "application/city+json"
    ext = ".json"


class Clr(File):
    """"""

    iana_mime = "application/clr"
    ext = ".1clr"


class ClueInfo__Xml(Xml):
    """"""

    iana_mime = "application/clue_info+xml"
    ext = ".clue"


class Clue__Xml(Xml):
    """"""

    iana_mime = "application/clue+xml"
    ext = ".xml"


class Cms(File):
    """"""

    iana_mime = "application/cms"
    ext = ".cmsc"


class Cnrp__Xml(Xml):
    """"""

    iana_mime = "application/cnrp+xml"
    ext = None


class CoapGroup__Json(Json):
    """"""

    iana_mime = "application/coap-group+json"
    ext = ".json"


class CoapPayload(File):
    """"""

    iana_mime = "application/coap-payload"
    ext = None


class Commonground(File):
    """"""

    iana_mime = "application/commonground"
    ext = None


class ConciseProblemDetails__Cbor(File):
    """"""

    iana_mime = "application/concise-problem-details+cbor"
    ext = None


class ConferenceInfo__Xml(Xml):
    """"""

    iana_mime = "application/conference-info+xml"
    ext = ".xml"


class Cpl__Xml(Xml):
    """"""

    iana_mime = "application/cpl+xml"
    ext = ".cpl"
    alternative_exts = (".xml",)


class Cose(File):
    """"""

    iana_mime = "application/cose"
    ext = ".cbor"


class CoseKey(File):
    """"""

    iana_mime = "application/cose-key"
    ext = ".cbor"


class CoseKeySet(File):
    """"""

    iana_mime = "application/cose-key-set"
    ext = ".cbor"


class CoseX509(File):
    """"""

    iana_mime = "application/cose-x509"
    ext = None


class Csrattrs(File):
    """"""

    iana_mime = "application/csrattrs"
    ext = ".csrattrs"


class Csta__Xml(Xml):
    """"""

    iana_mime = "application/csta+xml"
    ext = None


class Cstadata__Xml(Xml):
    """"""

    iana_mime = "application/CSTAdata+xml"
    ext = None


class Csvm__Json(Json):
    """"""

    iana_mime = "application/csvm+json"
    ext = ".json"


class Cwl(File):
    """TODO: CWL documents often start with the US-ASCII string "#!/usr/bin/env
    cwl-runner" (35 33 47 117 115 114 47 98 105 110 47 101 110 118 32
    99 119 108 45 114 117 110 110 101 114) but this is not required.
    All CWL document have the US-ASCII string "cwlVersion" (99 119 108
    86 101 114 115 105 111 110) as either the very first octets, or
    prepended by a newline later (13 10 or 13 or 10) in the file."""

    iana_mime = "application/cwl"
    ext = ".cwl"


class Cwl__Json(Json):
    """TODO: All CWL document have the US-ASCII string "cwlVersion" (99 119 108
    86 101 114 115 105 111 110) as a key in the topmost JSON
    dictionary."""

    iana_mime = "application/cwl+json"
    ext = ".cwl.json"


class Cwt(File):
    """"""

    iana_mime = "application/cwt"
    ext = None


class Cybercash(File):
    """"""

    iana_mime = "application/cybercash"
    ext = None


class Dash__Xml(Xml):
    """"""

    iana_mime = "application/dash+xml"
    ext = ".mpd"


class DashPatch__Xml(Xml):
    """"""

    iana_mime = "application/dash-patch+xml"
    ext = ".mpp"


class Dashdelta(File):
    """"""

    iana_mime = "application/dashdelta"
    ext = ".mpdd"


class Davmount__Xml(Xml):
    """"""

    iana_mime = "application/davmount+xml"
    ext = ".davmount"


class DcaRft(File):
    """"""

    iana_mime = "application/dca-rft"
    ext = None


class Dcd(File):
    """"""

    iana_mime = "application/DCD"
    ext = ".dcd"


class DecDx(File):
    """"""

    iana_mime = "application/dec-dx"
    ext = None


class DialogInfo__Xml(Xml):
    """"""

    iana_mime = "application/dialog-info+xml"
    ext = None


class Dicom(File):
    """"""

    iana_mime = "application/dicom"
    ext = None


class Dicom__Json(Json):
    """"""

    iana_mime = "application/dicom+json"
    ext = None


class Dicom__Xml(Xml):
    """"""

    iana_mime = "application/dicom+xml"
    ext = None


class Dii(File):
    """"""

    iana_mime = "application/DII"
    ext = ".dii"


class Dit(File):
    """"""

    iana_mime = "application/DIT"
    ext = ".dit"


class Dns(File):
    """"""

    iana_mime = "application/dns"
    ext = None


class Dns__Json(Json):
    """"""

    iana_mime = "application/dns+json"
    ext = None


class DnsMessage(File):
    """"""

    iana_mime = "application/dns-message"
    ext = None


class Dots__Cbor(File):
    """"""

    iana_mime = "application/dots+cbor"
    ext = None


class Dpop__Jwt(File):
    """"""

    iana_mime = "application/dpop+jwt"
    ext = None


class Dskpp__Xml(Xml):
    """"""

    iana_mime = "application/dskpp+xml"
    ext = ".xmls"


class Dssc__Der(File):
    """"""

    iana_mime = "application/dssc+der"
    ext = ".dssc"


class Dssc__Xml(Xml):
    """"""

    iana_mime = "application/dssc+xml"
    ext = ".xdssc"


class Dvcs(File):
    """"""

    iana_mime = "application/dvcs"
    ext = ".dvc"


class EdiConsent(File):
    """"""

    iana_mime = "application/EDI-consent"
    ext = None


class Edifact(File):
    """"""

    iana_mime = "application/EDIFACT"
    ext = None


class EdiX12(File):
    """"""

    iana_mime = "application/EDI-X12"
    ext = None


class Efi(WithMagicNumber, File):
    """TODO: The first two octets are the ASCII Characters "M" and "Z" ("MZ" at offset 0) -
    $offset = (read 4-bytes from byte 60) - The ASCII string "PE\0\0" must be found at
    $offset - The value of the two bytes at $offset + 24 must be 0x010b or 0x020b"""

    iana_mime = "application/efi"
    ext = ".*.efi"
    magic_number = b"MZ"


class Elm__Json(Json):
    """"""

    iana_mime = "application/elm+json"
    ext = None


class Elm__Xml(Xml):
    """"""

    iana_mime = "application/elm+xml"
    ext = None


class Emergencycalldata_Cap__Xml(Xml):
    """"""

    iana_mime = "application/EmergencyCallData.cap+xml"
    ext = None


class Emergencycalldata_Comment__Xml(Xml):
    """"""

    iana_mime = "application/EmergencyCallData.Comment+xml"
    ext = ".xml"


class Emergencycalldata_Control__Xml(Xml):
    """"""

    iana_mime = "application/EmergencyCallData.Control+xml"
    ext = ".xml"


class Emergencycalldata_Deviceinfo__Xml(Xml):
    """"""

    iana_mime = "application/EmergencyCallData.DeviceInfo+xml"
    ext = ".xml"


class Emergencycalldata_Ecall_Msd(File):
    """"""

    iana_mime = "application/EmergencyCallData.eCall.MSD"
    ext = None


class Emergencycalldata_Legacyesn__Json(Json):
    """"""

    iana_mime = "application/EmergencyCallData.LegacyESN+json"
    ext = ".json"


class Emergencycalldata_Providerinfo__Xml(Xml):
    """"""

    iana_mime = "application/EmergencyCallData.ProviderInfo+xml"
    ext = ".xml"


class Emergencycalldata_Serviceinfo__Xml(Xml):
    """"""

    iana_mime = "application/EmergencyCallData.ServiceInfo+xml"
    ext = ".xml"


class Emergencycalldata_Subscriberinfo__Xml(Xml):
    """"""

    iana_mime = "application/EmergencyCallData.SubscriberInfo+xml"
    ext = ".xml"


class Emergencycalldata_Veds__Xml(Xml):
    """"""

    iana_mime = "application/EmergencyCallData.VEDS+xml"
    ext = ".xml"


class Emma__Xml(Xml):
    """"""

    iana_mime = "application/emma+xml"
    ext = ".EMMA"
    alternative_exts = (".emma",)


class Emotionml__Xml(Xml):
    """"""

    iana_mime = "application/emotionml+xml"
    ext = ".emotionml"


class Encaprtp(File):
    """"""

    iana_mime = "application/encaprtp"
    ext = None


class Epp__Xml(Xml):
    """"""

    iana_mime = "application/epp+xml"
    ext = ".xml"


class Epub__Zip(File):
    """"""

    iana_mime = "application/epub+zip"
    ext = ".OCF"
    alternative_exts = (".epub",)


class Eshop(File):
    """"""

    iana_mime = "application/eshop"
    ext = None


class Exi(WithMagicNumber, File):
    """TODO: The first four octets may be hexadecimal 24 45 58 49 ("$EXI"). The first
    octet after these, or the first octet of the whole content if they are not present,
    has its high two bits set to values 1 and 0 in that order."""

    iana_mime = "application/exi"
    ext = ".exi"
    magic_number = "24455849"


class ExpectCtReport__Json(Json):
    """"""

    iana_mime = "application/expect-ct-report+json"
    ext = None


class Express(File):
    """"""

    iana_mime = "application/express"
    ext = ".exp"


class Fastinfoset(File):
    """"""

    iana_mime = "application/fastinfoset"
    ext = ".*.finf"


class Fastsoap(File):
    """"""

    iana_mime = "application/fastsoap"
    ext = None


class Fdf(WithMagicNumber, File):
    """TODO: "%FDF-" followed by the FDF
    version number, e.g., "%FDF-1.2". These characters are in
    US-ASCII encoding."""

    iana_mime = "application/fdf"
    ext = ".fdf"
    magic_number = b"%FDF-"


class Fdt__Xml(Xml):
    """"""

    iana_mime = "application/fdt+xml"
    ext = ".fdt"


class Fhir__Json(Json):
    """"""

    iana_mime = "application/fhir+json"
    ext = None


class Fhir__Xml(Xml):
    """"""

    iana_mime = "application/fhir+xml"
    ext = None


class Fits(WithMagicNumber, File):
    """TODO: "SIMPLE = T"  Jeff Uphoff of the National Radio Astronomy Observatory
    (NRAO) has contributed database entries for the magic number file which is used by
    the Unix "file" command. Magic number files with these entries are distributed with
    a variety of Unix-like operating systems. In addition to recognizing a FITS file
    using the string given above, the Uphoff entries also recognize the data type of
    the pixels in the PHDU."""

    iana_mime = "application/fits"
    ext = ".fits"
    alternative_exts = (None,)
    magic_number = b"SIMPLE = T"


class Flexfec(File):
    """"""

    iana_mime = "application/flexfec"
    ext = None


class FrameworkAttributes__Xml(Xml):
    """"""

    iana_mime = "application/framework-attributes+xml"
    ext = None


class Geo__Json(Json):
    """"""

    iana_mime = "application/geo+json"
    ext = ".geojson"


class Geo__JsonSeq(File):
    """"""

    iana_mime = "application/geo+json-seq"
    ext = None


class Geopackage__Sqlite3(WithMagicNumber, File):
    """"""

    iana_mime = "application/geopackage+sqlite3"
    ext = ".gpkg"
    magic_number = "47504b47"


class Geoxacml__Xml(Xml):
    """"""

    iana_mime = "application/geoxacml+xml"
    ext = None


class GltfBuffer(File):
    """"""

    iana_mime = "application/gltf-buffer"
    ext = ".bin"
    alternative_exts = (".glbin", ".glbuf")


class Gml__Xml(Xml):
    """"""

    iana_mime = "application/gml+xml"
    ext = ".gml"


class Gzip(WithMagicNumber, File):
    """"""

    iana_mime = "application/gzip"
    ext = ".gz"
    magic_number = "1f8b"


class H224(File):
    """"""

    iana_mime = "application/H224"
    ext = None


class Held__Xml(Xml):
    """"""

    iana_mime = "application/held+xml"
    ext = ".heldxml"


class Hl7v2__Xml(Xml):
    """"""

    iana_mime = "application/hl7v2+xml"
    ext = None


class Http(File):
    """"""

    iana_mime = "application/http"
    ext = None


class Hyperstudio(File):
    """"""

    iana_mime = "application/hyperstudio"
    ext = None


class IbeKeyRequest__Xml(Xml):
    """"""

    iana_mime = "application/ibe-key-request+xml"
    ext = None


class IbePkgReply__Xml(Xml):
    """"""

    iana_mime = "application/ibe-pkg-reply+xml"
    ext = None


class IbePpData(File):
    """"""

    iana_mime = "application/ibe-pp-data"
    ext = None


class Iges(File):
    """"""

    iana_mime = "application/iges"
    ext = None


class ImIscomposing__Xml(Xml):
    """"""

    iana_mime = "application/im-iscomposing+xml"
    ext = None


class Index(File):
    """"""

    iana_mime = "application/index"
    ext = None


class Index_Cmd(File):
    """"""

    iana_mime = "application/index.cmd"
    ext = None


class Index_Obj(File):
    """"""

    iana_mime = "application/index.obj"
    ext = None


class Index_Response(File):
    """"""

    iana_mime = "application/index.response"
    ext = None


class Index_Vnd(File):
    """"""

    iana_mime = "application/index.vnd"
    ext = None


class Inkml__Xml(Xml):
    """"""

    iana_mime = "application/inkml+xml"
    ext = ".InkML"
    alternative_exts = (".ink", ".inkml")


class Iotp(File):
    """"""

    iana_mime = "application/IOTP"
    ext = None


class Ipfix(File):
    """"""

    iana_mime = "application/ipfix"
    ext = ".ipfix"


class Ipp(File):
    """"""

    iana_mime = "application/ipp"
    ext = None


class Isup(File):
    """"""

    iana_mime = "application/ISUP"
    ext = None


class Its__Xml(Xml):
    """"""

    iana_mime = "application/its+xml"
    ext = ".its"


class JavaArchive(WithMagicNumber, File):
    """"""

    iana_mime = "application/java-archive"
    ext = ".jar"
    magic_number = b"PK\x03\x04"


class Jf2feed__Json(Json):
    """"""

    iana_mime = "application/jf2feed+json"
    ext = None


class Jose(File):
    """"""

    iana_mime = "application/jose"
    ext = None


class Jose__Json(Json):
    """"""

    iana_mime = "application/jose+json"
    ext = None


class Jrd__Json(Json):
    """"""

    iana_mime = "application/jrd+json"
    ext = ".jrd"


class Jscalendar__Json(Json):
    """"""

    iana_mime = "application/jscalendar+json"
    ext = None


class JsonPatch__Json(Json):
    """"""

    iana_mime = "application/json-patch+json"
    ext = ".json-patch"


class JsonSeq(File):
    """"""

    iana_mime = "application/json-seq"
    ext = None


class Jwk__Json(Json):
    """"""

    iana_mime = "application/jwk+json"
    ext = None


class JwkSet__Json(Json):
    """"""

    iana_mime = "application/jwk-set+json"
    ext = None


class Jwt(File):
    """"""

    iana_mime = "application/jwt"
    ext = None


class KpmlRequest__Xml(Xml):
    """"""

    iana_mime = "application/kpml-request+xml"
    ext = None


class KpmlResponse__Xml(Xml):
    """"""

    iana_mime = "application/kpml-response+xml"
    ext = None


class Ld__Json(Json):
    """"""

    iana_mime = "application/ld+json"
    ext = ".jsonld"


class Lgr__Xml(Xml):
    """"""

    iana_mime = "application/lgr+xml"
    ext = ".lgr"


class LinkFormat(File):
    """"""

    iana_mime = "application/link-format"
    ext = ".wlnk"


class Linkset(File):
    """"""

    iana_mime = "application/linkset"
    ext = None


class Linkset__Json(Json):
    """"""

    iana_mime = "application/linkset+json"
    ext = None


class LoadControl__Xml(Xml):
    """"""

    iana_mime = "application/load-control+xml"
    ext = None


class Logout__Jwt(File):
    """"""

    iana_mime = "application/logout+jwt"
    ext = None


class Lost__Xml(Xml):
    """"""

    iana_mime = "application/lost+xml"
    ext = ".lostxml"


class Lostsync__Xml(Xml):
    """"""

    iana_mime = "application/lostsync+xml"
    ext = ".lostsyncxml"


class Lpf__Zip(WithMagicNumber, File):
    """"""

    iana_mime = "application/lpf+zip"
    ext = ".LPF"
    alternative_exts = (".lpf",)
    magic_number = b"PK\x03\x04"


class Lxf(File):
    """"""

    iana_mime = "application/LXF"
    ext = ".lxf"


class MacBinhex40(File):
    """"""

    iana_mime = "application/mac-binhex40"
    ext = None


class Macwriteii(File):
    """"""

    iana_mime = "application/macwriteii"
    ext = None


class Mads__Xml(Xml):
    """"""

    iana_mime = "application/mads+xml"
    ext = ".mads"


class Manifest__Json(Json):
    """"""

    iana_mime = "application/manifest+json"
    ext = ".webmanifest"


class Marc(File):
    """"""

    iana_mime = "application/marc"
    ext = ".mrc"


class Marcxml__Xml(Xml):
    """"""

    iana_mime = "application/marcxml+xml"
    ext = ".mrcx"


class Mathematica(File):
    """"""

    iana_mime = "application/mathematica"
    ext = ".nb"
    alternative_exts = (".ma", ".mb")


class Mathml__Xml(Xml):
    """"""

    iana_mime = "application/mathml+xml"
    ext = ".mml"


class MathmlContent__Xml(Xml):
    """"""

    iana_mime = "application/mathml-content+xml"
    ext = None


class MathmlPresentation__Xml(Xml):
    """"""

    iana_mime = "application/mathml-presentation+xml"
    ext = None


class MbmsAssociatedProcedureDescription__Xml(Xml):
    """"""

    iana_mime = "application/mbms-associated-procedure-description+xml"
    ext = None


class MbmsDeregister__Xml(Xml):
    """"""

    iana_mime = "application/mbms-deregister+xml"
    ext = None


class MbmsEnvelope__Xml(Xml):
    """"""

    iana_mime = "application/mbms-envelope+xml"
    ext = None


class MbmsMskResponse__Xml(Xml):
    """"""

    iana_mime = "application/mbms-msk-response+xml"
    ext = None


class MbmsMsk__Xml(Xml):
    """"""

    iana_mime = "application/mbms-msk+xml"
    ext = None


class MbmsProtectionDescription__Xml(Xml):
    """"""

    iana_mime = "application/mbms-protection-description+xml"
    ext = None


class MbmsReceptionReport__Xml(Xml):
    """"""

    iana_mime = "application/mbms-reception-report+xml"
    ext = None


class MbmsRegisterResponse__Xml(Xml):
    """"""

    iana_mime = "application/mbms-register-response+xml"
    ext = None


class MbmsRegister__Xml(Xml):
    """"""

    iana_mime = "application/mbms-register+xml"
    ext = None


class MbmsSchedule__Xml(Xml):
    """"""

    iana_mime = "application/mbms-schedule+xml"
    ext = None


class MbmsUserServiceDescription__Xml(Xml):
    """"""

    iana_mime = "application/mbms-user-service-description+xml"
    ext = None


class Mbox(WithMagicNumber, File):
    """TODO: mbox database files can be recognized by having a leading character
    sequence of "From", followed by a single Space character (0x20), followed by
    additional printable character data (refer to the description in Appendix A for
    details). However, implementers are cautioned that all such files will not be
    compliant with all of the formatting rules, therefore implementers should treat
    these files with an appropriate amount of circumspection."""

    iana_mime = "application/mbox"
    ext = ".mbox"
    alternative_exts = (None,)
    magic_number = b"From "


class MediaControl__Xml(Xml):
    """"""

    iana_mime = "application/media_control+xml"
    ext = None


class MediaPolicyDataset__Xml(Xml):
    """"""

    iana_mime = "application/media-policy-dataset+xml"
    ext = ".mpf"


class Mediaservercontrol__Xml(Xml):
    """"""

    iana_mime = "application/mediaservercontrol+xml"
    ext = None


class MergePatch__Json(Json):
    """"""

    iana_mime = "application/merge-patch+json"
    ext = None


class Metalink4__Xml(Xml):
    """"""

    iana_mime = "application/metalink4+xml"
    ext = ".meta4"


class Mets__Xml(Xml):
    """"""

    iana_mime = "application/mets+xml"
    ext = ".mets"


class Mf4(File):
    """"""

    iana_mime = "application/MF4"
    ext = ".mf4"


class Mikey(File):
    """"""

    iana_mime = "application/mikey"
    ext = None


class Mipc(File):
    """TODO: To first verify that the file is HDF5 formatted, the data consumer
    must search for the HDF5 superblock. The superblock may begin at
    certain predefined offsets within the HDF5 file, allowing a block
    of unspecified content for users to place additional information
    at the beginning (and end) of the HDF5 file without limiting the
    HDF5 Library’s ability to manage the objects within the file
    itself. This feature was designed to accommodate wrapping an HDF5
    file in another file format or adding descriptive information to
    an HDF5 file without requiring the modification of the actual
    file’s information. The superblock is located by searching for the
    HDF5 format signature at byte offset 0, byte offset 512, and at
    successive locations in the file, each a multiple of two of the"""

    iana_mime = "application/mipc"
    ext = None


class MissingBlocks__CborSeq(File):
    """"""

    iana_mime = "application/missing-blocks+cbor-seq"
    ext = None


class MmtAei__Xml(Xml):
    """"""

    iana_mime = "application/mmt-aei+xml"
    ext = ".maei"


class MmtUsd__Xml(Xml):
    """"""

    iana_mime = "application/mmt-usd+xml"
    ext = ".musd"


class Mods__Xml(Xml):
    """"""

    iana_mime = "application/mods+xml"
    ext = ".mods"


class MossKeys(File):
    """"""

    iana_mime = "application/moss-keys"
    ext = None


class MossSignature(File):
    """"""

    iana_mime = "application/moss-signature"
    ext = None


class MosskeyData(File):
    """"""

    iana_mime = "application/mosskey-data"
    ext = None


class MosskeyRequest(File):
    """"""

    iana_mime = "application/mosskey-request"
    ext = None


class Mp21(File):
    """"""

    iana_mime = "application/mp21"
    ext = ".m21"
    alternative_exts = (".mp21",)


class Mp4(File):
    """"""

    iana_mime = "application/mp4"
    ext = ".mp4"
    alternative_exts = (".mpg4",)


class Mpeg4Generic(File):
    """"""

    iana_mime = "application/mpeg4-generic"
    ext = None


class Mpeg4Iod(File):
    """"""

    iana_mime = "application/mpeg4-iod"
    ext = None


class Mpeg4IodXmt(File):
    """"""

    iana_mime = "application/mpeg4-iod-xmt"
    ext = None


class MrbConsumer__Xml(Xml):
    """"""

    iana_mime = "application/mrb-consumer+xml"
    ext = ".xdf"


class MrbPublish__Xml(Xml):
    """"""

    iana_mime = "application/mrb-publish+xml"
    ext = ".xdf"


class MscIvr__Xml(Xml):
    """"""

    iana_mime = "application/msc-ivr+xml"
    ext = None


class MscMixer__Xml(Xml):
    """"""

    iana_mime = "application/msc-mixer+xml"
    ext = None


class Msword(File):
    """"""

    iana_mime = "application/msword"
    ext = None


class Mud__Json(Json):
    """"""

    iana_mime = "application/mud+json"
    ext = None


class MultipartCore(File):
    """"""

    iana_mime = "application/multipart-core"
    ext = None


class Mxf(File):
    """"""

    iana_mime = "application/mxf"
    ext = ".mxf"


class NQuads(File):
    """"""

    iana_mime = "application/n-quads"
    ext = ".nq"


class NTriples(File):
    """"""

    iana_mime = "application/n-triples"
    ext = ".nt"


class Nasdata(File):
    """"""

    iana_mime = "application/nasdata"
    ext = None


class NewsCheckgroups(File):
    """"""

    iana_mime = "application/news-checkgroups"
    ext = None


class NewsGroupinfo(File):
    """"""

    iana_mime = "application/news-groupinfo"
    ext = None


class NewsTransmission(File):
    """"""

    iana_mime = "application/news-transmission"
    ext = None


class Nlsml__Xml(Xml):
    """"""

    iana_mime = "application/nlsml+xml"
    ext = None


class Node(File):
    """"""

    iana_mime = "application/node"
    ext = ".js"
    alternative_exts = (".cjs",)


class Nss(File):
    """"""

    iana_mime = "application/nss"
    ext = None


class OauthAuthzReq__Jwt(File):
    """"""

    iana_mime = "application/oauth-authz-req+jwt"
    ext = None


class ObliviousDnsMessage(File):
    """"""

    iana_mime = "application/oblivious-dns-message"
    ext = None


class OcspRequest(File):
    """"""

    iana_mime = "application/ocsp-request"
    ext = ".ORQ"


class OcspResponse(File):
    """"""

    iana_mime = "application/ocsp-response"
    ext = ".ORS"


class OctetStream(File):
    """"""

    iana_mime = "application/octet-stream"
    ext = None


class Oda(File):
    """"""

    iana_mime = "application/ODA"
    ext = None


class Odm__Xml(Xml):
    """"""

    iana_mime = "application/odm+xml"
    ext = ".xml"


class Odx(File):
    """"""

    iana_mime = "application/ODX"
    ext = ".odx"


class OebpsPackage__Xml(Xml):
    """"""

    iana_mime = "application/oebps-package+xml"
    ext = ".opf"


class Ogg(WithMagicNumber, File):
    """"""

    iana_mime = "application/ogg"
    ext = ".ogx"
    alternative_exts = (".ogg",)
    magic_number = b"OggS"


class OhttpKeys(File):
    """"""

    iana_mime = "application/ohttp-keys"
    ext = None


class OpcNodeset__Xml(Xml):
    """"""

    iana_mime = "application/opc-nodeset+xml"
    ext = None


class Oscore(File):
    """"""

    iana_mime = "application/oscore"
    ext = None


class Oxps(WithMagicNumber, File):
    """"""

    iana_mime = "application/oxps"
    ext = ".oxps"
    magic_number = "504b0304"


class P21(File):
    """"""

    iana_mime = "application/p21"
    ext = ".p21"
    alternative_exts = (".stp", ".step", ".stpnc", ".210", ".ifc")


class P21__Zip(File):
    """"""

    iana_mime = "application/p21+zip"
    ext = ".stpz"


class P2pOverlay__Xml(Xml):
    """"""

    iana_mime = "application/p2p-overlay+xml"
    ext = ".relo"


class Parityfec(File):
    """"""

    iana_mime = "application/parityfec"
    ext = None


class Passport(File):
    """"""

    iana_mime = "application/passport"
    ext = None


class PatchOpsError__Xml(Xml):
    """"""

    iana_mime = "application/patch-ops-error+xml"
    ext = ".xer"


class Pdf(WithMagicNumber, File):
    """"""

    iana_mime = "application/pdf"
    ext = ".pdf"
    magic_number = b"%PDF-"


class Pdx(File):
    """"""

    iana_mime = "application/PDX"
    ext = ".pdx"


class PemCertificateChain(File):
    """"""

    iana_mime = "application/pem-certificate-chain"
    ext = ".pem"


class PgpEncrypted(File):
    """"""

    iana_mime = "application/pgp-encrypted"
    ext = None


class PgpKeys(File):
    """"""

    iana_mime = "application/pgp-keys"
    ext = ".asc"


class PgpSignature(File):
    """"""

    iana_mime = "application/pgp-signature"
    ext = ".asc"
    alternative_exts = (".sig",)


class PidfDiff__Xml(Xml):
    """"""

    iana_mime = "application/pidf-diff+xml"
    ext = ".xml"


class Pidf__Xml(Xml):
    """"""

    iana_mime = "application/pidf+xml"
    ext = None


class Pkcs10(File):
    """"""

    iana_mime = "application/pkcs10"
    ext = ".p10"


class Pkcs7Mime(File):
    """"""

    iana_mime = "application/pkcs7-mime"
    ext = None


class Pkcs7Signature(File):
    """"""

    iana_mime = "application/pkcs7-signature"
    ext = None


class Pkcs8(File):
    """"""

    iana_mime = "application/pkcs8"
    ext = ".p8"


class Pkcs8Encrypted(File):
    """"""

    iana_mime = "application/pkcs8-encrypted"
    ext = ".p8e"


class Pkcs12(File):
    """"""

    iana_mime = "application/pkcs12"
    ext = ".p12"
    alternative_exts = (".pfx",)


class PkixAttrCert(File):
    """"""

    iana_mime = "application/pkix-attr-cert"
    ext = ".ac"


class PkixCert(File):
    """"""

    iana_mime = "application/pkix-cert"
    ext = ".CER"


class PkixCrl(File):
    """"""

    iana_mime = "application/pkix-crl"
    ext = ".CRL"


class PkixPkipath(File):
    """"""

    iana_mime = "application/pkix-pkipath"
    ext = ".pkipath"


class Pkixcmp(File):
    """"""

    iana_mime = "application/pkixcmp"
    ext = ".PKI"


class Pls__Xml(Xml):
    """"""

    iana_mime = "application/pls+xml"
    ext = None


class PocSettings__Xml(Xml):
    """"""

    iana_mime = "application/poc-settings+xml"
    ext = None


class Postscript(File):
    """"""

    iana_mime = "application/postscript"
    ext = None


class PpspTracker__Json(Json):
    """"""

    iana_mime = "application/ppsp-tracker+json"
    ext = None


class Problem__Json(Json):
    """"""

    iana_mime = "application/problem+json"
    ext = None


class Problem__Xml(Xml):
    """"""

    iana_mime = "application/problem+xml"
    ext = None


class Provenance__Xml(Xml):
    """"""

    iana_mime = "application/provenance+xml"
    ext = ".provx"


class Prs_Alvestrand_TitraxSheet(File):
    """"""

    iana_mime = "application/prs.alvestrand.titrax-sheet"
    ext = None


class Prs_Cww(File):
    """"""

    iana_mime = "application/prs.cww"
    ext = ".cw"
    alternative_exts = ("cww",)


class Prs_Cyn(File):
    """"""

    iana_mime = "application/prs.cyn"
    ext = None


class Prs_Hpub__Zip(File):
    """"""

    iana_mime = "application/prs.hpub+zip"
    ext = ".HPUB"


class Prs_ImpliedDocument__Xml(Xml):
    """"""

    iana_mime = "application/prs.implied-document+xml"
    ext = None


class Prs_ImpliedExecutable(File):
    """"""

    iana_mime = "application/prs.implied-executable"
    ext = None


class Prs_ImpliedStructure(File):
    """"""

    iana_mime = "application/prs.implied-structure"
    ext = None


class Prs_Nprend(File):
    """"""

    iana_mime = "application/prs.nprend"
    ext = ".rnd"
    alternative_exts = (".rct",)


class Prs_Plucker(File):
    """TODO: 60	string		DataPlkr	Plucker document"""

    iana_mime = "application/prs.plucker"
    ext = None


class Prs_RdfXmlCrypt(File):
    """"""

    iana_mime = "application/prs.rdf-xml-crypt"
    ext = ".rdf-crypt"


class Prs_Xsf__Xml(Xml):
    """"""

    iana_mime = "application/prs.xsf+xml"
    ext = ".xsf"
    alternative_exts = (".xml",)


class Pskc__Xml(Xml):
    """"""

    iana_mime = "application/pskc+xml"
    ext = ".pskcxml"


class Pvd__Json(Json):
    """"""

    iana_mime = "application/pvd+json"
    ext = None


class Rdf__Xml(Xml):
    """"""

    iana_mime = "application/rdf+xml"
    ext = ".rdf"


class RouteApd__Xml(Xml):
    """"""

    iana_mime = "application/route-apd+xml"
    ext = ".rapd"


class RouteSTsid__Xml(Xml):
    """"""

    iana_mime = "application/route-s-tsid+xml"
    ext = ".sls"


class RouteUsd__Xml(Xml):
    """"""

    iana_mime = "application/route-usd+xml"
    ext = ".rusd"


class Qsig(File):
    """"""

    iana_mime = "application/QSIG"
    ext = None


class Raptorfec(File):
    """"""

    iana_mime = "application/raptorfec"
    ext = None


class Rdap__Json(Json):
    """"""

    iana_mime = "application/rdap+json"
    ext = None


class Reginfo__Xml(Xml):
    """"""

    iana_mime = "application/reginfo+xml"
    ext = ".rif"


class RelaxNgCompactSyntax(File):
    """"""

    iana_mime = "application/relax-ng-compact-syntax"
    ext = ".rnc"


class Reputon__Json(Json):
    """"""

    iana_mime = "application/reputon+json"
    ext = None


class ResourceListsDiff__Xml(Xml):
    """"""

    iana_mime = "application/resource-lists-diff+xml"
    ext = ".rld"


class ResourceLists__Xml(Xml):
    """"""

    iana_mime = "application/resource-lists+xml"
    ext = ".rl"


class Rfc__Xml(Xml):
    """"""

    iana_mime = "application/rfc+xml"
    ext = ".rfcxml"


class Riscos(File):
    """"""

    iana_mime = "application/riscos"
    ext = None


class Rlmi__Xml(Xml):
    """"""

    iana_mime = "application/rlmi+xml"
    ext = None


class RlsServices__Xml(Xml):
    """"""

    iana_mime = "application/rls-services+xml"
    ext = ".rs"


class RpkiChecklist(File):
    """"""

    iana_mime = "application/rpki-checklist"
    ext = ".sig"


class RpkiGhostbusters(File):
    """"""

    iana_mime = "application/rpki-ghostbusters"
    ext = ".gbr"


class RpkiManifest(File):
    """"""

    iana_mime = "application/rpki-manifest"
    ext = ".mft"


class RpkiPublication(File):
    """"""

    iana_mime = "application/rpki-publication"
    ext = None


class RpkiRoa(File):
    """"""

    iana_mime = "application/rpki-roa"
    ext = ".roa"


class RpkiUpdown(File):
    """"""

    iana_mime = "application/rpki-updown"
    ext = None


class Rtf(WithMagicNumber, File):
    """"""

    iana_mime = "application/rtf"
    ext = ".rtf"
    magic_number = b"{\rtf"


class Rtploopback(File):
    """"""

    iana_mime = "application/rtploopback"
    ext = None


class Rtx(File):
    """"""

    iana_mime = "application/rtx"
    ext = None


class Samlassertion__Xml(Xml):
    """"""

    iana_mime = "application/samlassertion+xml"
    ext = None


class Samlmetadata__Xml(Xml):
    """"""

    iana_mime = "application/samlmetadata+xml"
    ext = None


class SarifExternalProperties__Json(Json):
    """"""

    iana_mime = "application/sarif-external-properties+json"
    ext = ".sarif-external-properties"
    alternative_exts = (".sarif-external-properties.json",)


class Sarif__Json(Json):
    """"""

    iana_mime = "application/sarif+json"
    ext = ".sarif"
    alternative_exts = (".sarif.json",)


class Sbe(File):
    """"""

    iana_mime = "application/sbe"
    ext = None


class Sbml__Xml(Xml):
    """"""

    iana_mime = "application/sbml+xml"
    ext = None


class Scaip__Xml(Xml):
    """"""

    iana_mime = "application/scaip+xml"
    ext = None


class Scim__Json(Json):
    """"""

    iana_mime = "application/scim+json"
    ext = ".scim"
    alternative_exts = (".scm",)


class ScvpCvRequest(File):
    """"""

    iana_mime = "application/scvp-cv-request"
    ext = ".SCQ"


class ScvpCvResponse(File):
    """"""

    iana_mime = "application/scvp-cv-response"
    ext = ".SCS"


class ScvpVpRequest(File):
    """"""

    iana_mime = "application/scvp-vp-request"
    ext = ".SPQ"


class ScvpVpResponse(File):
    """"""

    iana_mime = "application/scvp-vp-response"
    ext = ".SPP"


class Sdp(File):
    """"""

    iana_mime = "application/sdp"
    ext = ".sdp"


class Secevent__Jwt(File):
    """"""

    iana_mime = "application/secevent+jwt"
    ext = None


class SenmlEtch__Cbor(File):
    """"""

    iana_mime = "application/senml-etch+cbor"
    ext = ".senml-etchc"


class SenmlEtch__Json(Json):
    """"""

    iana_mime = "application/senml-etch+json"
    ext = ".senml-etchj"


class SenmlExi(File):
    """"""

    iana_mime = "application/senml-exi"
    ext = ".senmle"


class Senml__Cbor(File):
    """"""

    iana_mime = "application/senml+cbor"
    ext = ".senmlc"


class Senml__Json(Json):
    """"""

    iana_mime = "application/senml+json"
    ext = ".senml"


class Senml__Xml(Xml):
    """"""

    iana_mime = "application/senml+xml"
    ext = ".senmlx"


class SensmlExi(File):
    """"""

    iana_mime = "application/sensml-exi"
    ext = ".sensmle"


class Sensml__Cbor(File):
    """"""

    iana_mime = "application/sensml+cbor"
    ext = ".sensmlc"


class Sensml__Json(Json):
    """"""

    iana_mime = "application/sensml+json"
    ext = ".sensml"


class Sensml__Xml(Xml):
    """"""

    iana_mime = "application/sensml+xml"
    ext = ".sensmlx"


class SepExi(File):
    """"""

    iana_mime = "application/sep-exi"
    ext = None


class Sep__Xml(Xml):
    """"""

    iana_mime = "application/sep+xml"
    ext = None


class SessionInfo(File):
    """"""

    iana_mime = "application/session-info"
    ext = None


class SetPayment(File):
    """"""

    iana_mime = "application/set-payment"
    ext = None


class SetPaymentInitiation(File):
    """"""

    iana_mime = "application/set-payment-initiation"
    ext = None


class SetRegistration(File):
    """"""

    iana_mime = "application/set-registration"
    ext = None


class SetRegistrationInitiation(File):
    """"""

    iana_mime = "application/set-registration-initiation"
    ext = None


class Sgml(File):
    """"""

    iana_mime = "application/SGML"
    ext = None


class SgmlOpenCatalog(File):
    """"""

    iana_mime = "application/sgml-open-catalog"
    ext = None


class Shf__Xml(Xml):
    """"""

    iana_mime = "application/shf+xml"
    ext = ".shf"


class Sieve(File):
    """"""

    iana_mime = "application/sieve"
    ext = ".siv"
    alternative_exts = (".sieve",)


class SimpleFilter__Xml(Xml):
    """"""

    iana_mime = "application/simple-filter+xml"
    ext = ".cl"
    alternative_exts = (".xml",)


class SimpleMessageSummary(File):
    """"""

    iana_mime = "application/simple-message-summary"
    ext = None


class Simplesymbolcontainer(File):
    """"""

    iana_mime = "application/simpleSymbolContainer"
    ext = None


class Sipc(File):
    """TODO: To first verify that the file is HDF5 formatted, the data consumer
    must search for the HDF5 superblock. The superblock may begin at
    certain predefined offsets within the HDF5 file, allowing a block
    of unspecified content for users to place additional information
    at the beginning (and end) of the HDF5 file without limiting the
    HDF5 Library’s ability to manage the objects within the file
    itself. This feature was designed to accommodate wrapping an HDF5
    file in another file format or adding descriptive information to
    an HDF5 file without requiring the modification of the actual
    file’s information. The superblock is located by searching for the
    HDF5 format signature at byte offset 0, byte offset 512, and at
    successive locations in the file, each a multiple of two of the"""

    iana_mime = "application/sipc"
    ext = None


class Slate(File):
    """"""

    iana_mime = "application/slate"
    ext = None


class Smil__Xml(Xml):
    """"""

    iana_mime = "application/smil+xml"
    ext = None


class Smpte336m(File):
    """"""

    iana_mime = "application/smpte336m"
    ext = None


class Soap__Fastinfoset(File):
    """TODO: For details on the identification of a fast infoset document refer to the
    magic number section of the "application/fastinfoset" media type.
       The identification of a W3C SOAP message infoset serialized as a fast
    infoset document requires that the fast infoset document be parsed and that
    the properties of the element information item, corresponding to the root of
    the element tree, conform to the properties of the SOAP Envelope element
    information item specified in W3C SOAP 1.2, 5.1."""

    iana_mime = "application/soap+fastinfoset"
    ext = ".W3C"


class Soap__Xml(Xml):
    """"""

    iana_mime = "application/soap+xml"
    ext = ".SOAP"


class SparqlQuery(File):
    """TODO: A SPARQL query may have the string 'PREFIX' (case independent) near the beginning of the document."""

    iana_mime = "application/sparql-query"
    ext = ".rq"


class Spdx__Json(Json):
    """"""

    iana_mime = "application/spdx+json"
    ext = ".spdx.json"


class SparqlResults__Xml(Xml):
    """"""

    iana_mime = "application/sparql-results+xml"
    ext = ".srx"


class SpiritsEvent__Xml(Xml):
    """"""

    iana_mime = "application/spirits-event+xml"
    ext = None


class Sql(File):
    """"""

    iana_mime = "application/sql"
    ext = ".sql"


class Srgs(File):
    """"""

    iana_mime = "application/srgs"
    ext = None


class Srgs__Xml(Xml):
    """"""

    iana_mime = "application/srgs+xml"
    ext = None


class Sru__Xml(Xml):
    """"""

    iana_mime = "application/sru+xml"
    ext = ".sru"


class Ssml__Xml(Xml):
    """"""

    iana_mime = "application/ssml+xml"
    ext = None


class Stix__Json(Json):
    """"""

    iana_mime = "application/stix+json"
    ext = ".stix"


class Swid__Cbor(WithMagicNumber, File):
    """"""

    iana_mime = "application/swid+cbor"
    ext = ".coswid"
    magic_number = "53574944"


class Swid__Xml(Xml):
    """"""

    iana_mime = "application/swid+xml"
    ext = ".swidtag"


class TampApexUpdate(File):
    """"""

    iana_mime = "application/tamp-apex-update"
    ext = ".tau"


class TampApexUpdateConfirm(File):
    """"""

    iana_mime = "application/tamp-apex-update-confirm"
    ext = ".auc"


class TampCommunityUpdate(File):
    """"""

    iana_mime = "application/tamp-community-update"
    ext = ".tcu"


class TampCommunityUpdateConfirm(File):
    """"""

    iana_mime = "application/tamp-community-update-confirm"
    ext = ".cuc"


class TampError(File):
    """"""

    iana_mime = "application/tamp-error"
    ext = ".ter"


class TampSequenceAdjust(File):
    """"""

    iana_mime = "application/tamp-sequence-adjust"
    ext = ".tsa"


class TampSequenceAdjustConfirm(File):
    """"""

    iana_mime = "application/tamp-sequence-adjust-confirm"
    ext = ".sac"


class TampStatusQuery(File):
    """"""

    iana_mime = "application/tamp-status-query"
    ext = ".tsq"


class TampStatusResponse(File):
    """"""

    iana_mime = "application/tamp-status-response"
    ext = ".tsr"


class TampUpdate(File):
    """"""

    iana_mime = "application/tamp-update"
    ext = ".tur"


class TampUpdateConfirm(File):
    """"""

    iana_mime = "application/tamp-update-confirm"
    ext = ".tuc"


class Taxii__Json(Json):
    """"""

    iana_mime = "application/taxii+json"
    ext = None


class Td__Json(Json):
    """"""

    iana_mime = "application/td+json"
    ext = ".jsontd"


class Tei__Xml(Xml):
    """"""

    iana_mime = "application/tei+xml"
    ext = ".tei"
    alternative_exts = (".teiCorpus", ".odd")


class TetraIsi(File):
    """"""

    iana_mime = "application/TETRA_ISI"
    ext = None


class Thraud__Xml(Xml):
    """"""

    iana_mime = "application/thraud+xml"
    ext = ".tfi"


class TimestampQuery(File):
    """"""

    iana_mime = "application/timestamp-query"
    ext = None


class TimestampReply(File):
    """"""

    iana_mime = "application/timestamp-reply"
    ext = None


class TimestampedData(File):
    """"""

    iana_mime = "application/timestamped-data"
    ext = ".tsd"


class Tlsrpt__Gzip(File):
    """"""

    iana_mime = "application/tlsrpt+gzip"
    ext = None


class Tlsrpt__Json(Json):
    """"""

    iana_mime = "application/tlsrpt+json"
    ext = None


class Tm__Json(Json):
    """"""

    iana_mime = "application/tm+json"
    ext = ".jsontm"
    alternative_exts = (".tm.json", ".tm.jsonld")


class Tnauthlist(File):
    """"""

    iana_mime = "application/tnauthlist"
    ext = None


class TokenIntrospection__Jwt(File):
    """"""

    iana_mime = "application/token-introspection+jwt"
    ext = None


class TrickleIceSdpfrag(File):
    """"""

    iana_mime = "application/trickle-ice-sdpfrag"
    ext = None


class Trig(File):
    """"""

    iana_mime = "application/trig"
    ext = ".trig"


class Ttml__Xml(Xml):
    """"""

    iana_mime = "application/ttml+xml"
    ext = ".ttml"


class TveTrigger(File):
    """"""

    iana_mime = "application/tve-trigger"
    ext = None


class Tzif(WithMagicNumber, File):
    """"""

    iana_mime = "application/tzif"
    ext = None
    magic_number = "545a6966"


class TzifLeap(WithMagicNumber, File):
    """"""

    iana_mime = "application/tzif-leap"
    ext = None
    magic_number = "545a6966"


class Ulpfec(File):
    """"""

    iana_mime = "application/ulpfec"
    ext = None


class UrcGrpsheet__Xml(Xml):
    """"""

    iana_mime = "application/urc-grpsheet+xml"
    ext = ".gsheet"


class UrcRessheet__Xml(Xml):
    """"""

    iana_mime = "application/urc-ressheet+xml"
    ext = ".rsheet"


class UrcTargetdesc__Xml(Xml):
    """"""

    iana_mime = "application/urc-targetdesc+xml"
    ext = ".td"


class UrcUisocketdesc__Xml(Xml):
    """"""

    iana_mime = "application/urc-uisocketdesc+xml"
    ext = ".uis"


class Vcard__Json(Json):
    """"""

    iana_mime = "application/vcard+json"
    ext = None


class Vcard__Xml(Xml):
    """"""

    iana_mime = "application/vcard+xml"
    ext = None


class Vemmi(File):
    """"""

    iana_mime = "application/vemmi"
    ext = None


class Voicexml__Xml(Xml):
    """"""

    iana_mime = "application/voicexml+xml"
    ext = None


class VoucherCms__Json(Json):
    """"""

    iana_mime = "application/voucher-cms+json"
    ext = ".vcj"


class VqRtcpxr(File):
    """"""

    iana_mime = "application/vq-rtcpxr"
    ext = None


class Wasm(WithMagicNumber, File):
    """"""

    iana_mime = "application/wasm"
    ext = ".wasm"
    magic_number = "61736d"


class Watcherinfo__Xml(Xml):
    """"""

    iana_mime = "application/watcherinfo+xml"
    ext = ".wif"
    alternative_exts = (".xml",)


class WebpushOptions__Json(Json):
    """"""

    iana_mime = "application/webpush-options+json"
    ext = ".json"


class WhoisppQuery(File):
    """"""

    iana_mime = "application/whoispp-query"
    ext = None


class WhoisppResponse(File):
    """"""

    iana_mime = "application/whoispp-response"
    ext = None


class Widget(WithMagicNumber, File):
    """"""

    iana_mime = "application/widget"
    ext = ".wgt"
    magic_number = "504b0304"


class Wita(File):
    """"""

    iana_mime = "application/wita"
    ext = None


class Wordperfect5_1(File):
    """"""

    iana_mime = "application/wordperfect5.1"
    ext = None


class Wsdl__Xml(Xml):
    """"""

    iana_mime = "application/wsdl+xml"
    ext = ".wsdl"


class Wspolicy__Xml(Xml):
    """"""

    iana_mime = "application/wspolicy+xml"
    ext = ".wspolicy"


class PkiMessage(File):
    """"""

    iana_mime = "application/x-pki-message"
    ext = None


class WwwFormUrlencoded(File):
    """"""

    iana_mime = "application/x-www-form-urlencoded"
    ext = None


class X509CaCert(File):
    """"""

    iana_mime = "application/x-x509-ca-cert"
    ext = None


class X509CaRaCert(File):
    """"""

    iana_mime = "application/x-x509-ca-ra-cert"
    ext = None


class X509NextCaCert(File):
    """"""

    iana_mime = "application/x-x509-next-ca-cert"
    ext = None


class X400Bp(File):
    """"""

    iana_mime = "application/x400-bp"
    ext = None


class Xacml__Xml(Xml):
    """"""

    iana_mime = "application/xacml+xml"
    ext = None


class XcapAtt__Xml(Xml):
    """"""

    iana_mime = "application/xcap-att+xml"
    ext = ".xav"


class XcapCaps__Xml(Xml):
    """"""

    iana_mime = "application/xcap-caps+xml"
    ext = ".xca"


class XcapDiff__Xml(Xml):
    """"""

    iana_mime = "application/xcap-diff+xml"
    ext = ".xdf"


class XcapEl__Xml(Xml):
    """"""

    iana_mime = "application/xcap-el+xml"
    ext = ".xel"


class XcapError__Xml(Xml):
    """"""

    iana_mime = "application/xcap-error+xml"
    ext = ".xer"


class XcapNs__Xml(Xml):
    """"""

    iana_mime = "application/xcap-ns+xml"
    ext = ".xns"


class XconConferenceInfoDiff__Xml(Xml):
    """"""

    iana_mime = "application/xcon-conference-info-diff+xml"
    ext = ".xml"


class XconConferenceInfo__Xml(Xml):
    """"""

    iana_mime = "application/xcon-conference-info+xml"
    ext = ".xml"


class Xenc__Xml(Xml):
    """"""

    iana_mime = "application/xenc+xml"
    ext = ".xml"


class Xfdf(File):
    """"""

    iana_mime = "application/xfdf"
    ext = ".xfdf"


class Xhtml__Xml(Xml):
    """"""

    iana_mime = "application/xhtml+xml"
    ext = ".xhtml"
    alternative_exts = (".xht",)


class Xliff__Xml(Xml):
    """"""

    iana_mime = "application/xliff+xml"
    ext = ".xlf"


class XmlDtd(File):
    """"""

    iana_mime = "application/xml-dtd"
    ext = ".dtd"
    alternative_exts = (".mod",)


class XmlExternalParsedEntity(File):
    """"""

    iana_mime = "application/xml-external-parsed-entity"
    ext = ".ent"


class XmlPatch__Xml(Xml):
    """"""

    iana_mime = "application/xml-patch+xml"
    ext = None


class Xmpp__Xml(Xml):
    """"""

    iana_mime = "application/xmpp+xml"
    ext = None


class Xop__Xml(Xml):
    """"""

    iana_mime = "application/xop+xml"
    ext = ".XOP"


class Xslt__Xml(Xml):
    """"""

    iana_mime = "application/xslt+xml"
    ext = ".XSLT"
    alternative_exts = (".xsl", ".xslt")


class Xv__Xml(Xml):
    """"""

    iana_mime = "application/xv+xml"
    ext = ".mxml"
    alternative_exts = (".xhvml", ".xvml", ".xvm")


class Yang(File):
    """"""

    iana_mime = "application/yang"
    ext = ".yang"


class YangData__Cbor(File):
    """"""

    iana_mime = "application/yang-data+cbor"
    ext = None


class YangData__Json(Json):
    """"""

    iana_mime = "application/yang-data+json"
    ext = None


class YangData__Xml(Xml):
    """"""

    iana_mime = "application/yang-data+xml"
    ext = None


class YangPatch__Json(Json):
    """"""

    iana_mime = "application/yang-patch+json"
    ext = None


class YangPatch__Xml(Xml):
    """"""

    iana_mime = "application/yang-patch+xml"
    ext = None


class Yin__Xml(Xml):
    """"""

    iana_mime = "application/yin+xml"
    ext = ".yin"


class Zlib(WithMagicNumber, File):
    """TODO: first byte is usually 0x78 but can also be 0x08, 0x18, 0x28, 0x38, 0x48,
    0x58, or 0x68. The first two bytes, when interpreted as an unsigned 16-bit number
    in big-endian byte order, contain a value that is a multiple of 31."""

    iana_mime = "application/zlib"
    ext = None
    magic_number = "78"


class Zstd(WithMagicNumber, File):
    """"""

    iana_mime = "application/zstd"
    ext = ".zst"
    magic_number = "fd2fb528"
