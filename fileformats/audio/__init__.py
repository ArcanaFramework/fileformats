from ..core import __version__
from fileformats.generic import File
from fileformats.core.mixin import WithMagicNumber


class Audio(File):
    "Base class for audio file formats"
    binary = True
    iana_mime = None


# Compressed formats
class Mpeg(Audio):
    ext = ".mp3"
    alternate_exts = (".mp1", ".mp2")
    iana_mime = "audio/mpeg"


class Mp4(WithMagicNumber, Audio):
    ext = ".mp4"
    iana_mime = "audio/mp4"
    magic_number = "6674797069736F6D"


class Aac(Audio):
    ext = ".aac"
    alternate_exts = (".adts", ".loas", ".ass")
    iana_mime = "audio/aac"


class Wav(Audio):
    ext = ".wav"
    iana_mime = "audio/wav"


class _1d_interleaved_parityfec(Audio):
    """"""

    iana_mime = "audio/1d-interleaved-parityfec"
    ext = None


class _32kadpcm(Audio):
    """"""

    iana_mime = "audio/32kadpcm"
    ext = ".726"


class _3gpp(Audio):
    """TODO: None.  However, the file-type box
    must occur first in the file, and
    MUST contain a 3GPP brand in its
    compatible brands list."""

    iana_mime = "audio/3gpp"
    ext = ".3gp"
    alternative_exts = (".3gpp",)


class _3gpp2(Audio):
    """TODO: None.  However, the file-type box must occur first in the file,
    and MUST contain a 3GPP2 brand in its compatible brands list."""

    iana_mime = "audio/3gpp2"
    ext = None


class Ac3(WithMagicNumber, Audio):
    """"""

    iana_mime = "audio/ac3"
    ext = None
    magic_number = "b77"


class Amr(Audio):
    """"""

    iana_mime = "audio/AMR"
    ext = ".amr"
    alternative_exts = (".AMR",)


class AmrWb(Audio):
    """"""

    iana_mime = "audio/AMR-WB"
    ext = ".awb"
    alternative_exts = (".AWB",)


class AmrWb__(Audio):
    """"""

    iana_mime = "audio/amr-wb+"
    ext = None


class Aptx(Audio):
    """"""

    iana_mime = "audio/aptx"
    ext = None


class Asc(Audio):
    """"""

    iana_mime = "audio/asc"
    ext = None


class AtracAdvancedLossless(Audio):
    """"""

    iana_mime = "audio/ATRAC-ADVANCED-LOSSLESS"
    ext = ".aal"
    alternative_exts = (".aa3", ".omg")


class AtracX(Audio):
    """"""

    iana_mime = "audio/ATRAC-X"
    ext = ".atx"
    alternative_exts = (".aa3", ".omg")


class Atrac3(Audio):
    """"""

    iana_mime = "audio/ATRAC3"
    ext = ".at3"
    alternative_exts = (".aa3", ".omg")


class Basic(Audio):
    """"""

    iana_mime = "audio/basic"
    ext = None


class Bv16(Audio):
    """"""

    iana_mime = "audio/BV16"
    ext = None


class Bv32(Audio):
    """"""

    iana_mime = "audio/BV32"
    ext = None


class Clearmode(Audio):
    """"""

    iana_mime = "audio/clearmode"
    ext = None


class Cn(Audio):
    """"""

    iana_mime = "audio/CN"
    ext = None


class Dat12(Audio):
    """"""

    iana_mime = "audio/DAT12"
    ext = None


class Dls(WithMagicNumber, Audio):
    """"""

    iana_mime = "audio/dls"
    ext = ".dls"
    magic_number = "444c5320"
    magic_number_offset = 8


class DsrEs201108(Audio):
    """"""

    iana_mime = "audio/dsr-es201108"
    ext = None


class DsrEs202050(Audio):
    """"""

    iana_mime = "audio/dsr-es202050"
    ext = None


class DsrEs202211(Audio):
    """"""

    iana_mime = "audio/dsr-es202211"
    ext = None


class DsrEs202212(Audio):
    """"""

    iana_mime = "audio/dsr-es202212"
    ext = None


class Dv(Audio):
    """"""

    iana_mime = "audio/DV"
    ext = None


class Dvi4(Audio):
    """"""

    iana_mime = "audio/DVI4"
    ext = None


class Eac3(WithMagicNumber, Audio):
    """"""

    iana_mime = "audio/eac3"
    ext = None
    magic_number = "b77"


class Encaprtp(Audio):
    """"""

    iana_mime = "audio/encaprtp"
    ext = None


class Evrc(WithMagicNumber, Audio):
    """"""

    iana_mime = "audio/EVRC"
    ext = ".evc"
    alternative_exts = ("EVC",)
    magic_number = b"#!EVRC\n"


class EvrcQcp(WithMagicNumber, Audio):
    """"""

    iana_mime = "audio/EVRC-QCP"
    ext = ".qcp"
    alternative_exts = (".QCP",)
    magic_number = b"RIFF"


class Evrc0(Audio):
    """"""

    iana_mime = "audio/EVRC0"
    ext = None


class Evrc1(Audio):
    """"""

    iana_mime = "audio/EVRC1"
    ext = None


class Evrcb(WithMagicNumber, Audio):
    """"""

    iana_mime = "audio/EVRCB"
    ext = ".evb"
    alternative_exts = (".EVB",)
    magic_number = b"#!EVRC-B\n"


class Evrcb0(Audio):
    """"""

    iana_mime = "audio/EVRCB0"
    ext = None


class Evrcb1(Audio):
    """"""

    iana_mime = "audio/EVRCB1"
    ext = None


class Evrcnw(WithMagicNumber, Audio):
    """"""

    iana_mime = "audio/EVRCNW"
    ext = ".enw"
    alternative_exts = (".ENW",)
    magic_number = b"#!EVRCNW\n"


class Evrcnw0(Audio):
    """"""

    iana_mime = "audio/EVRCNW0"
    ext = None


class Evrcnw1(Audio):
    """"""

    iana_mime = "audio/EVRCNW1"
    ext = None


class Evrcwb(WithMagicNumber, Audio):
    """"""

    iana_mime = "audio/EVRCWB"
    ext = ".evw"
    alternative_exts = (".EVW",)
    magic_number = b"#!EVCWB\n"


class Evrcwb0(Audio):
    """"""

    iana_mime = "audio/EVRCWB0"
    ext = None


class Evrcwb1(Audio):
    """"""

    iana_mime = "audio/EVRCWB1"
    ext = None


class Evs(Audio):
    """"""

    iana_mime = "audio/EVS"
    ext = ".3gp"
    alternative_exts = (".3gpp",)


class Flexfec(Audio):
    """"""

    iana_mime = "audio/flexfec"
    ext = None


class Fwdred(Audio):
    """"""

    iana_mime = "audio/fwdred"
    ext = None


class G711_0(WithMagicNumber, Audio):
    """TODO: #!G7110A\n or #!G7110M\n (for A-law or MU-law
    encodings respectively, see Section 6)."""

    iana_mime = "audio/G711-0"
    ext = None
    magic_number = b"#!G7110A\n"


class G719(Audio):
    """"""

    iana_mime = "audio/G719"
    ext = None


class G7221(Audio):
    """"""

    iana_mime = "audio/G7221"
    ext = None


class G722(Audio):
    """"""

    iana_mime = "audio/G722"
    ext = None


class G723(Audio):
    """"""

    iana_mime = "audio/G723"
    ext = None


class G726_16(Audio):
    """"""

    iana_mime = "audio/G726-16"
    ext = None


class G726_24(Audio):
    """"""

    iana_mime = "audio/G726-24"
    ext = None


class G726_32(Audio):
    """"""

    iana_mime = "audio/G726-32"
    ext = None


class G726_40(Audio):
    """"""

    iana_mime = "audio/G726-40"
    ext = None


class G728(Audio):
    """"""

    iana_mime = "audio/G728"
    ext = None


class G729(Audio):
    """"""

    iana_mime = "audio/G729"
    ext = None


class G7291(Audio):
    """"""

    iana_mime = "audio/G7291"
    ext = None


class G729d(Audio):
    """"""

    iana_mime = "audio/G729D"
    ext = None


class G729e(Audio):
    """"""

    iana_mime = "audio/G729E"
    ext = None


class Gsm(Audio):
    """"""

    iana_mime = "audio/GSM"
    ext = None


class GsmEfr(Audio):
    """"""

    iana_mime = "audio/GSM-EFR"
    ext = None


class GsmHr_08(Audio):
    """"""

    iana_mime = "audio/GSM-HR-08"
    ext = None


class Ilbc(Audio):
    """"""

    iana_mime = "audio/iLBC"
    ext = ".lbc"
    alternative_exts = (".LBC",)


class IpMrV2___5(Audio):
    """"""

    iana_mime = "audio/ip-mr_v2.5"
    ext = None


class L8(Audio):
    """"""

    iana_mime = "audio/L8"
    ext = None


class L16(Audio):
    """"""

    iana_mime = "audio/L16"
    ext = ".WAV"
    alternative_exts = (".L16",)


class L20(Audio):
    """"""

    iana_mime = "audio/L20"
    ext = None


class L24(Audio):
    """"""

    iana_mime = "audio/L24"
    ext = None


class Lpc(Audio):
    """"""

    iana_mime = "audio/LPC"
    ext = None


class Melp(Audio):
    """"""

    iana_mime = "audio/MELP"
    ext = None


class Melp600(Audio):
    """"""

    iana_mime = "audio/MELP600"
    ext = None


class Melp1200(Audio):
    """"""

    iana_mime = "audio/MELP1200"
    ext = None


class Melp2400(Audio):
    """"""

    iana_mime = "audio/MELP2400"
    ext = None


class Mhas(Audio):
    """TODO: Receivers can search for the following syncword within the binary data stream: mpeghAudioStreamPacket() 0xC001A5 (24bit sequence)."""

    iana_mime = "audio/mhas"
    ext = ".mhas"


class MobileXmf(Audio):
    """"""

    iana_mime = "audio/mobile-xmf"
    ext = ".mxmf"


class Mpa(Audio):
    """"""

    iana_mime = "audio/MPA"
    ext = None


class Mp4a_latm(Audio):
    """"""

    iana_mime = "audio/MP4A-LATM"
    ext = None


class MpaRobust(Audio):
    """"""

    iana_mime = "audio/mpa-robust"
    ext = None


class Mpeg4_generic(Audio):
    """"""

    iana_mime = "audio/mpeg4-generic"
    ext = None


class Ogg(WithMagicNumber, Audio):
    """"""

    iana_mime = "audio/ogg"
    ext = ".oga"
    alternative_exts = (".ogg", ".spx", ".opus")
    magic_number = b"OggS"


class Opus(Audio):
    """"""

    iana_mime = "audio/opus"
    ext = None


class Parityfec(Audio):
    """"""

    iana_mime = "audio/parityfec"
    ext = None


class Pcma(Audio):
    """"""

    iana_mime = "audio/PCMA"
    ext = None


class PcmaWb(Audio):
    """"""

    iana_mime = "audio/PCMA-WB"
    ext = None


class Pcmu(Audio):
    """"""

    iana_mime = "audio/PCMU"
    ext = None


class PcmuWb(Audio):
    """"""

    iana_mime = "audio/PCMU-WB"
    ext = None


class Prs_Sid(WithMagicNumber, Audio):
    """TODO: first 4 bytes are 0x50534944 - "PSID" or 0x52534944 - "RSID\" """

    iana_mime = "audio/prs.sid"
    ext = ".sid"
    alternative_exts = (".psid",)
    magic_number = b"PSID"


class Qcelp(Audio):
    """"""

    iana_mime = "audio/QCELP"
    ext = None


class Raptorfec(Audio):
    """"""

    iana_mime = "audio/raptorfec"
    ext = None


class Red(Audio):
    """"""

    iana_mime = "audio/RED"
    ext = None


class RtpEncAescm128(Audio):
    """"""

    iana_mime = "audio/rtp-enc-aescm128"
    ext = None


class Rtploopback(Audio):
    """"""

    iana_mime = "audio/rtploopback"
    ext = None


class RtpMidi(Audio):
    """"""

    iana_mime = "audio/rtp-midi"
    ext = None


class Rtx(Audio):
    """"""

    iana_mime = "audio/rtx"
    ext = None


class Scip(Audio):
    """"""

    iana_mime = "audio/scip"
    ext = None


class Smv(WithMagicNumber, Audio):
    """"""

    iana_mime = "audio/SMV"
    ext = ".smv"
    alternative_exts = (".SMV",)
    magic_number = b"#!SMV\n"


class Smv0(Audio):
    """"""

    iana_mime = "audio/SMV0"
    ext = None


class SmvQcp(WithMagicNumber, Audio):
    """"""

    iana_mime = "audio/SMV-QCP"
    ext = ".qcp"
    alternative_exts = (".QCP",)
    magic_number = b"RIFF"


class Sofa(WithMagicNumber, Audio):
    """TODO: as with HDF5"""

    iana_mime = "audio/sofa"
    ext = ".sofa"
    magic_number = "894844460d0a1a0a"


class SpMidi(Audio):
    """"""

    iana_mime = "audio/sp-midi"
    ext = ".mid"


class Speex(Audio):
    """"""

    iana_mime = "audio/speex"
    ext = None


class T140c(Audio):
    """"""

    iana_mime = "audio/t140c"
    ext = None


class T38(Audio):
    """"""

    iana_mime = "audio/t38"
    ext = None


class TelephoneEvent(Audio):
    """"""

    iana_mime = "audio/telephone-event"
    ext = None


class TetraAcelp(Audio):
    """"""

    iana_mime = "audio/TETRA_ACELP"
    ext = None


class TetraAcelpBb(Audio):
    """"""

    iana_mime = "audio/TETRA_ACELP_BB"
    ext = None


class Tone(Audio):
    """"""

    iana_mime = "audio/tone"
    ext = None


class Tsvcis(Audio):
    """"""

    iana_mime = "audio/TSVCIS"
    ext = None


class Uemclip(Audio):
    """"""

    iana_mime = "audio/UEMCLIP"
    ext = None


class Ulpfec(Audio):
    """"""

    iana_mime = "audio/ulpfec"
    ext = None


class Usac(Audio):
    """"""

    iana_mime = "audio/usac"
    ext = ".loas"
    alternative_exts = (".xhe",)


class Vdvi(Audio):
    """"""

    iana_mime = "audio/VDVI"
    ext = None


class VmrWb(Audio):
    """"""

    iana_mime = "audio/VMR-WB"
    ext = None


class Vorbis(Audio):
    """"""

    iana_mime = "audio/vorbis"
    ext = None


class VorbisConfig(Audio):
    """"""

    iana_mime = "audio/vorbis-config"
    ext = None
