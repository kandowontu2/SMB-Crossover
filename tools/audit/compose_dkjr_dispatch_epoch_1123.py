"""Build and exercise an in-memory DK Jr. dispatch optimization."""

from hashlib import sha256
import json

import measure_dkjr_shared_epoch_fit_1114 as Fit
import profile_dkjr_shared_dispatch_1123 as Profile
from check_dkjr_powerups_current_1113 import CHR, PAGES
from compose_sonic_original_motion_1122 import ROM


COOKIE = 534485
MAIN = 0xD65E
MAIN_SIZE = 73
MAIN_FILE = CHR + PAGES[10]*1024 + 0x25E
OLD_MAIN = bytes.fromhex(
    '20c1bf9042a5758dfbc8a5bd8dfcc82040d22040b99030a57538edfbc88d01070a0a0a0a8546'
    'a5bd38edfcc8858ead6bc0c901f00cc902f004a902d006a903d002a900851e38601860')

NEW_MAIN = '''
.segment "MAIN"
    jsr $bfc1
    bcc Failed
    lda $75
    sta $c8fb
    lda $bd
    sta $c8fc
    jsr $d240
    jsr $b940
    bcc Failed
    ; The caller has authenticated both work banks before running our motor.
    ; Publish this update's stamp only after the real score/motor work succeeds.
    lda $0e
    sta $c8ff
    lda $75
    sec
    sbc $c8fb
    sta $0701
    asl a
    asl a
    asl a
    asl a
    sta $46
    lda $bd
    sec
    sbc $c8fc
    sta $8e
    ; Keep the three native player states and the original return flags.
    lda $c06b
    eor #1
    beq ProjectState
    cmp #3
    beq ProjectState
    lda #2
ProjectState:
    ora #0
    sta $1e
    sec
    rts
Failed:
    clc
    rts
'''


def h(raw):
    return sha256(raw).hexdigest()


def offset(bank, pc):
    return 16 + bank*8192 + (pc & 8191)


def packet(raw):
    return b''.join(raw[CHR+page*1024:CHR+(page+1)*1024] for page in PAGES)


def proposal(raw):
    assert h(raw) == Profile.PIN
    assert len(OLD_MAIN) == MAIN_SIZE and raw[MAIN_FILE:MAIN_FILE+MAIN_SIZE] == OLD_MAIN
    images = []
    old_helper = Fit.A(Fit.OLD_HELPER, Fit.HELPER_LAYOUT)['images']
    # The caller branches on zero to reject an unset stamp. Leave Z from the
    # load of the actual stamp rather than the comparison of the owner ID.
    helper = Fit.once(Fit.NEW_HELPER, ''' lda DkEpoch
 cpx #40
 beq EpochReturn
 lda MiniEpoch
EpochReturn:
 rts''', ''' cpx #40
 bne MiniStamp
 lda DkEpoch
 rts
MiniStamp:
 lda MiniEpoch
 rts''')
    new_helper = Fit.A(helper, Fit.HELPER_LAYOUT)['images']
    for section, (pc, size) in Fit.HELPER_LAYOUT.items():
        images.append((offset(85, pc), old_helper[section].ljust(size, b'\xff'),
                       new_helper[section].ljust(size, b'\xff')))

    changed = Fit.once(Fit.OLD_SELECTOR, ' cmp #4\n beq MiniTry',
                       ' adc #1\n lsr\n cmp #2\n beq MiniTry')
    # For both tables, unsigned underflow wraps past the existing upper bound.
    for base in ('8c', '88'):
        changed = Fit.once(changed, f' sbc #${base}\n bcc DkLocalNo', f' sbc #${base}')
    selector = {'SELECTOR': (0xA740, 127)}
    before = Fit.A(Fit.OLD_SELECTOR, selector)
    after = Fit.A(changed, selector)
    images.append((offset(65, 0xA740), before['images']['SELECTOR'],
                   after['images']['SELECTOR'].ljust(127, b'\xea')))

    def checked(symbols):
        return bytes((0x90, (symbols['MiniFullCheck']-0xA7D7)&255,
                      0xB0, (symbols['MiniAuthorized']-0xA7D9)&255))

    images.append((offset(65, 0xA7D5), checked(before['symbols']), checked(after['symbols'])))
    main = Fit.A(NEW_MAIN, {'MAIN': (MAIN, MAIN_SIZE)})['images']['MAIN']
    images.append((MAIN_FILE, OLD_MAIN, main.ljust(MAIN_SIZE, b'\xea')))
    candidate = bytearray(raw)
    cookie = b'\xa7\x28\x01' + sha256(packet(raw)).digest()[:13]
    assert raw[COOKIE:COOKIE+16] == cookie and raw.count(cookie) == 1
    for start, old, new in images:
        assert len(new) == len(old) and raw[start:start+len(old)] == old, start
        candidate[start:start+len(old)] = new
    new_cookie = cookie[:3] + sha256(packet(candidate)).digest()[:13]
    candidate[COOKIE:COOKIE+16] = new_cookie
    spans = [(start, len(old)) for start, old, _ in images] + [(COOKIE, len(cookie))]
    assert sum(length for _, length in spans) == len({start+i for start, length in spans for i in range(length)})
    return bytes(candidate), spans


def compare(a, b):
    native = (*range(0x17B), *range(0x1FE, 0x800), *range(0x5C00, 0x8000))
    changes = [hex(i) for i in native if a[i] != b[i]]
    assert not changes, changes
    assert a.rawtags == b.rawtags and a.chr_latches == b.chr_latches
    assert a.vram == b.vram and a.ppuctrl == b.ppuctrl
    for bank, (old, new) in enumerate(zip(a.ram, b.ram, strict=True)):
        allowed = set(range(0x1FE0, 0x1FF0)) if bank in (2, 3) else set()
        if bank == 2:
            allowed.update(range(MAIN & 8191, (MAIN & 8191)+MAIN_SIZE))
            allowed.add(0x8FF)
        changes = [hex(i) for i, (x, y) in enumerate(zip(old, new, strict=True)) if x != y and i not in allowed]
        assert not changes, (bank, changes)


def verify(parent, candidate):
    a, b = (Profile.boot(raw) for raw in (parent, candidate))
    phases = {}
    for name, pad, count in (('idle', 0, 32), ('walk', 1, 48), ('jump', 0x81, 16), ('land', 0, 26)):
        ta, tb = Profile.DispatchTrace(a), Profile.DispatchTrace(b)
        old_cycles = new_cycles = 0
        for _ in range(count):
            old_cycles += Profile.Opening.main_step(a, pad, ta)[0]
            new_cycles += Profile.Opening.main_step(b, pad, tb)[0]
            compare(a, b)
        phases[name] = dict(updates=count, x=Profile.Opening.position(b),
                            parent_cycles=old_cycles, candidate_cycles=new_cycles,
                            cycles_saved_per_update=(old_cycles-new_cycles)/count,
                            full_header_checks=[ta.full_calls, tb.full_calls])
    assert phases['idle']['cycles_saved_per_update'] > 4500
    return phases


def main():
    parent = ROM.read_bytes()
    candidate, spans = proposal(parent)
    print('DK DISPATCH CANDIDATE '+json.dumps(dict(SHA256=h(candidate), spans=spans)), flush=True)
    result = dict(parent=h(parent), candidate=h(candidate), matched=verify(parent, candidate), output_files=0)
    result['receipt_SHA256'] = h(json.dumps(result, sort_keys=True).encode())
    print('DK DISPATCH '+json.dumps(result, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
