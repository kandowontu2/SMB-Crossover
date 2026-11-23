"""Bind Prince's existing completed-update stamp to the native hot dispatcher."""

import json
from struct import pack

import compose_dkjr_sonic_dispatch_1123 as Shared
import compose_prince_lift_reach_1123 as Reach


H = Shared.H
PARENT = '5c89b9b727a6c718edccd873bbdff69409e4280c7e0db4e1c3c169304c6a84c9'
CANDIDATE = 'c1d57f50332ec4c96c49c909de45998032dba3c2ae22aa2e7821c97b26e76f7f'
SELECTOR = (0xA740, 127)
SELECTOR_RETURN = 0xA7D5
READ_EPOCH = 0xB06B
CANONICAL_ROW = 0xB0B0
READERS = 0xB08F
PRINCE_READER = 0xB0BF
NEXT_PUBLIC_ROW = 0xB0FE
MIRROR = bytes.fromhex('4cdca8')


def selector_source():
    once = Shared.Fit.once
    source = Shared.selector_source()
    source = once(source, ' lda FarHi\n cmp #$aa', ' ldy FarHi\n cpy #$aa')
    source = once(source, ' tax\n lda FarHi\n cmp #$b0', ' tax\n cpy #$b0')
    # Adding carry (X >= 4) before testing oddness admits 1, 3, 4 and 6.
    check = ''' cpx #4
 txa
 adc #0
 lsr
 bcc MiniFullCheck
 sty FarLo
 bcs MiniTry
 nop'''
    return once(source, ''' txa
 cmp #3
 beq MiniTry
 and #$fd
 cmp #4
 beq MiniTry''', check)


def selector():
    before = Shared.program()[2]
    after = Shared.M.assemble(selector_source(), dict(SELECTOR=SELECTOR))
    assert before['used']['SELECTOR'] == after['used']['SELECTOR'] == SELECTOR[1]
    for name in ('MiniFullCheck', 'MiniAuthorized', 'PrSharedCall', 'DkLocalNo', 'DkAuthNo', 'SourceBanks'):
        assert before['symbols'][name] == after['symbols'][name], name
    assert Shared.S.checked_branches(after) == Shared.S.checked_branches(before)
    return after


def readers(raw):
    # The original tail still rejects an unset or unequal epoch and returns
    # the same flags. Keep both Sonic continuation addresses byte-exact.
    base = Shared.M.R / 'tools/reference/dkjr_sonic_dispatch_1123.s'
    original = Shared.M.assemble(
        'ReadSonicEpoch=$da40\n' + base.read_text(encoding='ascii'), Shared.LAYOUT)
    epoch = original['symbols']['EpochLoaded']
    bad = original['symbols']['BadEpoch']
    bundle = dict(Reach.C.W.Symbols.bundle(), raw=raw)
    w = Reach.C.W.address
    fields = dict(EpochLoaded=epoch, BadEpoch=bad, PrinceEpoch=PRINCE_READER,
                  Engine=w(bundle, 'GameEngineSubroutine'),
                  Pause=w(bundle, 'GamePauseStatus'), Timer=w(bundle, 'TimerControl'))
    route = bytes((0x4C,)) + pack('<H', READERS)
    choose, _ = Reach.L.assemble('''
 cpx #38
 beq PrinceEpoch
 cpx #41
 lda $c8ff
 bcc EpochLoaded
 lda $c3f0
 jmp EpochLoaded
''', fields, READERS)
    prince, _ = Reach.L.assemble('''
 lda $5fff
 lsr
 bcc BadEpoch
 lda $01fa
 cmp #$83
 bne BadEpoch
 lda $01f9
 cmp #$52
 bne BadEpoch
 lda Engine
 cmp #8
 bne BadEpoch
 lda Pause
 and #1
 ora Timer
 bne BadEpoch
 lda $c0aa
 beq BadEpoch
 lda $c0a9
 jmp EpochLoaded
''', fields, PRINCE_READER)
    return route, choose, prince


def edits_for(raw):
    before = Shared.program()[2]
    after = selector()
    route, choose, prince = readers(raw)
    yield 65, SELECTOR[0], before['images']['SELECTOR'], after['images']['SELECTOR']
    yield 85, READ_EPOCH, bytes.fromhex('e029ad'), route
    for start, end, body in ((READERS, CANONICAL_ROW, choose),
                             (PRINCE_READER, NEXT_PUBLIC_ROW, prince)):
        cells, extra = divmod(end-start, len(MIRROR))
        assert not extra and len(body) <= cells * len(MIRROR)
        yield 85, start, (MIRROR * cells)[:len(body)], body


def apply(raw, edits):
    buf = bytearray(raw)
    for bank, pc, old, new in edits:
        at = Shared.S.off(bank, pc)
        assert len(old) == len(new) and buf[at:at + len(old)] == old, (bank, hex(pc))
        buf[at:at + len(new)] = new
    return bytes(buf)


def compose(raw):
    assert H(raw) == PARENT
    edits = tuple(edits_for(raw))
    result = apply(raw, edits)
    assert result[Shared.S.off(85, CANONICAL_ROW):Shared.S.off(85, CANONICAL_ROW)+3] == MIRROR
    assert result[Shared.S.off(85, 0xB0BC):Shared.S.off(85, 0xB0BC)+3] == MIRROR
    assert Reach.C.extract(result) == Reach.C.extract(raw)
    assert H(result) == CANDIDATE
    return result, [dict(bank=bank, pc=pc, old=old.hex(), new=new.hex())
                    for bank, pc, old, new in edits]


def inverse(image):
    assert H(image) == CANDIDATE
    parent = apply(image, ((bank, pc, new, old) for bank, pc, old, new in edits_for(image)))
    assert H(parent) == PARENT
    return parent


if __name__ == '__main__':
    from run_prince_oneup_lift_native_1123 import Timing

    parent = Timing.ROM.read_bytes()
    image, edits = compose(parent)
    print(json.dumps(dict(parent=H(parent), candidate=H(image), patches=edits), separators=(',', ':')))
