"""Skip Prince's side dispatch only after his native epoch check succeeds."""

import compose_prince_epoch_current_1123 as Epoch
import compose_sonic_side_forward_1123 as Layout


CORRECTED = 'c85cde8f6944b803b57897835ec800667a3d1e08e8a6cdea8aa43e9510ca3171'
SOURCE = '''
ForeignSource=$bed8
DkForward=$bfa4
NativeReturningSide=$bf90

.segment "HOOK"
 jmp OwnerSide

.segment "TAIL"
OwnerSide:
 cmp #38
 bne CheckDK
 txa
 pha
 ; The stock BEA2 entry has already set FarLo=B0. Switch FarHi so
 ; this call reaches epoch mirror B0B0 in physical bank 85.
 lda #$b0
 sta $016d
 lda #$d5
 jsr $015a
 pla
 tax
 bcc Legacy
 jmp NativeReturningSide
CheckDK:
 cmp #40
 beq DkForward
Legacy:
 jmp ForeignSource
'''


def side_edits():
    hook, start, end = Layout.HOOK, Layout.START, Layout.END
    program = Layout.M.assemble(SOURCE, dict(HOOK=(hook, len(Layout.OLD)), TAIL=(start, end-start)))
    for name, pc, previous, pad in (('HOOK', hook, Layout.OLD, b'\xea'),
                                    ('TAIL', start, bytes(end-start), b'\0')):
        data = program['images'][name].ljust(len(previous), pad)
        assert len(data) == len(previous)
        yield 33, pc, previous, data


def compose(raw):
    assert Epoch.H(raw) == Epoch.PARENT
    base, inherited = Epoch.compose(raw)
    for pc, signature in ((0xBEA2, '08a9b08d6c01a9bf8d6d01ad0260'),
                          (0xBF90, '68284c8b95')):
        off = Layout.off(33, pc)
        data = bytes.fromhex(signature)
        assert base[off:off + len(data)] == data
    edits = tuple(side_edits())
    result = Epoch.apply(base, edits)
    assert Epoch.H(result) == CORRECTED
    return result, inherited + [dict(bank=bank, pc=pc, old=old.hex(), new=new.hex())
                                for bank, pc, old, new in edits]


def inverse(image):
    assert Epoch.H(image) == CORRECTED
    before_side = Epoch.apply(image, ((bank, pc, new, old) for bank, pc, old, new in side_edits()))
    return Epoch.inverse(before_side)
