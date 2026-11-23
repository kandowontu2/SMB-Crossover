"""Private exact6201 rectangle-read hoist; same261B envelope, memory only.

The virtual descriptor pointer is constant within one DkRectCommon call.
Resolve it once after saving X/Y, preserving the existing native predicate,
all head/score addresses and every helper. No RAM/carrier allocation.
"""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import compose_dkjr_head_bridge_1113 as Head
import profile_dkjr_empty_current_1123 as Profile

H = lambda data: sha256(data).hexdigest()
PIN = Profile.PIN


def prelude(raw):
    b = dict(Profile.W.Symbols.bundle(), raw=raw)
    names = ('MTileAttribute', 'BlockBounceTimer', 'GuestHurtTicks', 'TimerControl')
    values = {n: Profile.W.address(b, n) for n in names}
    values.update(ScreenLeftX=Profile.W.address(b, 'ScreenLeft_X_Pos'),
        ScreenLeftPage=Profile.W.address(b, 'ScreenLeft_PageLoc'),
        HeadX=Head.HEAD_X, HeadPage=Head.HEAD_PAGE, HeadTop=Head.HEAD_TOP,
        R2=5, R6=9, R7=10, SafecallA=0x16a, FarTarget=0x16c, FarCall=0x15a,
        RectPredicate=Head.RECT_END, HeadReturn=0xaf02, NativeAddScore=0xbb37,
        NativeHeadEffect=Profile.W.address(b, 'NativeRarePlayerHeadCollisionCore'),
        NativeHeadBank=(Profile.W.location(b, 'NativeRarePlayerHeadCollisionCore')-16)//8192 | 128)
    definitions = 'R0=$03\nObjectOffset=$0d\nDigitModifier=$0131\nScoreAmount=$c8f9\n'
    return definitions+''.join(f'{n}=${v:x}\n' for n,v in values.items())


def once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)


def chunks(pc, data):
    cursor, offset = 0, Head.offset(pc)
    while cursor < len(data):
        page, within = divmod(offset+cursor, 1024)
        size = min(1024-within, len(data)-cursor)
        yield Head.Base.CHR+Head.Base.PAGES[page]*1024+within, data[cursor:cursor+size]
        cursor += size


@lru_cache(maxsize=1)
def program(raw):
    assert H(raw) == PIN
    source = Head.SOURCE.read_text()
    assert H(Head.SOURCE.read_bytes()) == '578f7e97b70bc36739cdbeb95750fb6d0a4a3733b106332a1abc56b9ff4e3eb8'
    definitions = prelude(raw)
    old = Head.assemble(definitions+source, Head.LAYOUT)
    body = Head.payload(raw)
    for role, (pc, size) in Head.LAYOUT.items():
        assert body[Head.offset(pc):Head.offset(pc)+size] == old['images'][role].ljust(size, b'\xea'), role
    # Only these three internal JSR sites enter the old reader. The fixed
    # external entry is DkRectCommon; the predicate is a separate pure leaf.
    reader = old['symbols']['RectRead']
    assert body[:8192].count(b'\x20'+reader.to_bytes(2, 'little')) == 3
    assert body[:8192].count(b'\x4c'+reader.to_bytes(2, 'little')) == 0
    mapping = '''    lda $c002
    sta RectReadCell+1
    lda $c003
    cmp #8
    bcs RectReadROM
    ora #$c0
RectReadROM:
    sta RectReadCell+2
'''
    old_reader = 'RectRead:\n    php\n    pha\n'+mapping+'    pla\n    plp\n'
    source = once(source, old_reader, 'RectRead:\n')
    source = once(source, '    ldy #0\n    lda $c00f\n', mapping+'    ldy #0\n    lda $c00f\n')
    short = Head.assemble(definitions+source, Head.LAYOUT)
    # Source-owned four bytes keep every accepted-head and flush entry fixed.
    assert old['symbols']['DkAcceptHead']-short['symbols']['DkAcceptHead'] == 4
    source = once(source, 'DkRectCompactEnd:', '    .byte $ea,$ea,$ea,$ea\nDkRectCompactEnd:')
    new = Head.assemble(definitions+source, Head.LAYOUT)
    assert new['used'] == old['used']
    for name in ('DkRectCommon', 'DkAcceptHead', 'DkHeadFlush', 'DkScoreFlush', 'OriginalFall'):
        assert new['symbols'][name] == old['symbols'][name], name
    for role in ('SCORE', 'HEAD_HOOK'):
        assert new['images'][role] == old['images'][role], role
    begin = old['symbols']['DkAcceptHead']-Head.RECT_START
    assert new['images']['RECT'][begin:] == old['images']['RECT'][begin:]
    return old, new, source


def compose(raw):
    old, new, source = program(raw)
    result = bytearray(raw)
    before, after = old['images']['RECT'], new['images']['RECT']
    spans = []
    for (at, a), (other, b) in zip(chunks(Head.RECT_START, before), chunks(Head.RECT_START, after), strict=True):
        assert at == other and raw[at:at+len(a)] == a and len(a) == len(b)
        result[at:at+len(b)] = b
        spans.append(dict(file=at, size=len(a), old_SHA256=H(a), new_SHA256=H(b)))
    old_cookie = raw[Head.Base.COOKIE_AT:Head.Base.COOKIE_AT+16]
    assert old_cookie == b'\xa7\x28\x01'+sha256(Head.payload(raw)).digest()[:13]
    cookie = b'\xa7\x28\x01'+sha256(Head.payload(result)).digest()[:13]
    result[Head.Base.COOKIE_AT:Head.Base.COOKIE_AT+16] = cookie
    image = bytes(result)
    assert inverse(image) == raw
    return image, dict(parent_SHA256=PIN, candidate_SHA256=H(image),
        source_SHA256=H(source.encode()), composer_SHA256=H(Path(__file__).read_bytes()),
        spans=spans, RECT=[Head.RECT_START, Head.RECT_END], used=new['used'],
        old_reader=old['symbols']['RectRead'], new_reader=new['symbols']['RectRead'],
        old_cell=old['symbols']['RectReadCell'], new_cell=new['symbols']['RectReadCell'],
        head_entries_fixed=True, head_flush_score_hook_exact=True,
        all_helpers_original_jump_and_dispatch_exact=True, new_capacity=0, new_RAM=0,
        cookie=cookie.hex(), ROM_writes=0, physical_cadence_qualified=False)


def inverse(image):
    # Strict full-image parent round trip authenticates the supplied candidate.
    parent = bytearray(image)
    raw = Profile.Old.ROM.read_bytes()
    assert H(raw) == PIN
    old, _, _ = program(raw)
    for at, data in chunks(Head.RECT_START, old['images']['RECT']):
        parent[at:at+len(data)] = data
    parent[Head.Base.COOKIE_AT:Head.Base.COOKIE_AT+16] = raw[Head.Base.COOKIE_AT:Head.Base.COOKIE_AT+16]
    assert bytes(parent) == raw
    return bytes(parent)
