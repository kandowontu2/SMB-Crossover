"""Exercise the proposed Contra Force fast entry in detached and booted models."""

import argparse
from collections import Counter
import json
from unittest.mock import patch

from py65.devices.mpu6502 import MPU

from check_contra_force_fast_worker_1122 import assemble, COOKIE, registers, TAIL, worker_code
import check_contra_force_fixed_layout_1122 as Layout


Hud, offset = Layout.Hud, Layout.offset


START = 0xB020
ROUTER = 0xB08E
END = 0xB100
SLOW = 0xB0B6
NO_SERVICE = 0xB0E4
FAST = 0xDFA9
ORIGINAL_HASH = 'bca680209849a80d2e3901070954bba08c1805024eec17682047df941d032535'
GUARD = 0xBF47
ADMISSION = 0xBF94
RESTORE = 0xBFED
RETURN = 0xBF18
RETURN_SCOPED = 0xBF1C
RETURN_END = 0xBF49


def proposed_window(raw):
    assert Hud.H(raw) == Hud.CANDIDATE
    start = offset(87, START)
    original = raw[start:start + END - START]
    assert Hud.H(original) == ORIGINAL_HASH
    # Retain the public veneer addresses and the unavailable entry.
    prefix = original[:ROUTER - START]
    # A successful scope marker is only published for the live CF call.
    # CPY proves that C is already mapped to C2 and provides carry set for
    # the fast worker. The slow STX publishes the offset before it is used.
    body = assemble(ROUTER, '''
        PHP
        PHA
        TXA
        PHA
        TYA
        PHA
        LDA $6002
        LSR A
        BCC ${unavailable:04x}
        SBC #$0D
        CMP #$04
        BCS ${unavailable:04x}
        TAY
        LDA $016C
        ADC #$E0
        TAX
        LDA $01FA
        CMP #$84
        BNE ${slow:04x}
        CPY $7DA1
        BNE ${slow:04x}
        JMP $DFA9
    slow:
        STX $016A
        CPY #$03
        BNE ${common:04x}
        TXA
        AND #$B3
        CMP #$13
        BEQ ${unavailable:04x}
        LDA #$11
        CPX #$33
        BEQ ${cold:04x}
        LDA #$91
        CPX #$4E
        BEQ ${cold:04x}
        LDX #$AD
        SEC
    common:
        LDA #$99
        STA $016C
        LDA #$B7
        STA $016D
        LDA #$E0
        JSR $015A
        BCS ${target:04x}
    unavailable:
        CLC
    target:
        STA $0162
        PLA
        TAY
        PLA
        TAX
        PLA
        STA $016A
        BCC ${failed:04x}
        PLP
        JMP $015D
    failed:
        PLP
        CLC
        RTS
    cold:
        STA $016C
        LDA #$C8
        BNE ${target:04x}
    ''')
    assert len(prefix + body) == END - START == 224
    assert body[SLOW - ROUTER:SLOW - ROUTER + 3] == bytes.fromhex('8e6a01')
    assert body[NO_SERVICE - ROUTER:NO_SERVICE - ROUTER + 4] == bytes.fromhex('188d6201')
    return prefix + body


def check(raw):
    window = proposed_window(raw)
    mem = bytearray(65536)
    mem[START:END] = window
    cpu = MPU(memory=mem)
    samples = dict(fast=0, slow=0, unselected=0)
    for owner in (27, 29, 31, 33, 0, 2, 30, 32, 35, 255):
        for marked, c_map in ((False, 2), (False, 0xD0), (True, 2), (True, 0xD0)):
            # Production supplies the marker only for the authenticated owner.
            if marked and owner != 31:
                continue
            for service in range(36):
                mem[0x6002], mem[0x7DA1], mem[0x1FA] = owner, c_map, 0x84 if marked else 0x83
                mem[0x16A:0x16E] = bytes((0xB2, 0x00, 0x20 + 3 * service, 0xB0))
                cpu.pc, cpu.sp, cpu.a, cpu.x, cpu.y, cpu.p = START + 3 * service, 0xEF, 0xB2, 86, 37, 0xB1
                cpu.processorCycles = 0
                while cpu.pc not in (SLOW, FAST, NO_SERVICE):
                    assert cpu.processorCycles < 110, (owner, service, hex(cpu.pc))
                    cpu.step()
                expected = (FAST if marked and c_map == 2 else SLOW) if owner in (27, 29, 31, 33) else NO_SERVICE
                assert cpu.pc == expected
                assert cpu.sp == 0xEB and list(mem[0x1EC:0x1F0]) == [37, 86, 0xB2, 0xB1]
                assert mem[0x16A] == 0xB2
                if expected == FAST:
                    assert cpu.p & 1 and cpu.y == 2 and cpu.x == 3 * service
                    samples['fast'] += 1
                elif expected == SLOW:
                    assert cpu.y == (owner - 27) // 2 and cpu.x == 3 * service
                    cpu.step()
                    assert mem[0x16A] == 3 * service
                    samples['slow'] += 1
                else:
                    samples['unselected'] += 1
    return dict(bytes=len(window), SHA256=Hud.H(window), ingress=samples, admission=check_guard(raw),
                failure_next_bank_write_to_qualify=True, no_rom_mount=True)


def proposed_guard(raw):
    offset_in_rom = offset(69, GUARD)
    old = raw[offset_in_rom:offset_in_rom + 0xC000 - GUARD]
    assert old[0xBFF2 - GUARD:] == b'\xff' * 14
    assert old[0xBF7E - GUARD:0xBF80 - GUARD] == bytes.fromhex('d018')
    assert old[0xBF8E - GUARD:0xBF90 - GUARD] == bytes.fromhex('d008')
    prefix = bytearray(old[:0xBF8E - GUARD])
    prefix[0xBF7F - GUARD] = 0xBF90 - 0xBF80  # First differing cookie byte goes to CLC.
    prefix.extend(assemble(0xBF8E, '''
        BEQ $BF91
        CLC
        JMP $BFED
    '''))
    assert GUARD + len(prefix) == ADMISSION
    admission = assemble(ADMISSION, '''
        LDA $6002
        CMP #$1F
        BNE ${fallback:04x}
        JSR $BF47
        BCC ${fallback:04x}
        INC $01FA
        LDA #$02
        JMP $015A
    fallback:
        JMP $8798
    ''')
    available = 0xBFAD - ADMISSION
    assert len(admission) <= available
    prefix.extend(admission + b'\xff' * (available - len(admission)))
    prefix.extend(old[0xBFAD - GUARD:0xBFE1 - GUARD])  # Cookie and original retirement body.
    prefix.extend(assemble(0xBFE1, '''
        PHP
        PHA
        LDA $6002
        CMP #$1F
        BNE $BFBF
        PLA
        PLP
        RTS
    '''))
    assert GUARD + len(prefix) == RESTORE
    prefix.extend(assemble(RESTORE, '''
        PLA
        STA $7DA1
        STA $5116
        PLA
        TAX
        PLA
        BCC ${denied:04x}
        PLP
        SEC
        RTS
    denied:
        PLP
        CLC
        RTS
    '''))
    assert GUARD + len(prefix) == 0xBFFF
    return bytes(prefix) + b'\xff'


def check_guard(raw):
    code = proposed_guard(raw)
    mem = bytearray(65536)
    mem[GUARD:0xC000] = code
    cookie = mem[0xBFAD:0xBFBD]
    assert len(cookie) == 16 and cookie[:2] == bytes((0xA7, 0x1F))
    cpu = MPU(memory=mem)
    cases = dict(valid=0, rejected=0, foreign=0)
    for owner in (31, 0, 2, 33):
        for variant in range(4):
            for poison in (range(-1, 16) if owner == 31 else (-1,)):
                mem[0x6002], mem[0x5FE8], mem[0x7DA1], mem[0x5116] = owner, variant << 3, 0xD0, 0xD0
                mem[0xDFE0:0xDFF0] = cookie
                mem[0xDFE2] = variant
                if poison >= 0:
                    mem[0xDFE0 + poison] ^= 1
                mem[0x1F9:0x1FB] = bytes.fromhex('5283')
                mem[0x16C:0x16E] = ADMISSION.to_bytes(2, 'little')
                cpu.pc, cpu.sp, cpu.a, cpu.x, cpu.y, cpu.p = ADMISSION, 0xF5, 23, 71, 37, 0x31
                cpu.processorCycles = 0
                while cpu.pc not in (0x015A, 0x8798):
                    assert cpu.processorCycles < 800, (owner, variant, poison, hex(cpu.pc))
                    cpu.step()
                accepted = owner == 31 and poison < 0
                assert (cpu.pc == 0x015A) == accepted
                assert cpu.sp == 0xF5 and cpu.x == 71 and cpu.y == 37
                assert mem[0x7DA1] == mem[0x5116] == 0xD0
                assert mem[0x1F9] == 0x52 and mem[0x1FA] == (0x84 if accepted else 0x83)
                assert bytes(mem[0x16C:0x16E]) == ADMISSION.to_bytes(2, 'little')
                if accepted:
                    assert cpu.a == 2 and cpu.p & 1
                    cases['valid'] += 1
                else:
                    cases['rejected' if owner == 31 else 'foreign'] += 1
    return dict(bytes=len(code), SHA256=Hud.H(code), tests=cases,
                scope_lifetime_still_open=True)


def return_code():
    # The generic service return always restores its caller's C map. The
    # enclosing mode tree can legitimately publish a new C map. Keep that
    # publication, restoring the saved map only if C still holds our RAM2.
    code = assemble(RETURN, '''
        PHP
        CLC
        BCC ${save:04x}
        PHP
        SEC
    save:
        PHA
        TXA
        PHA
        TSX
        BCC ${map:04x}
        LDA $7DA1
        CMP #$02
        BNE ${drop:04x}
    map:
        LDA $0104,X
        STA $7DA1
        STA $5116
    drop:
        LDA $0103,X
        STA $0104,X
        PLA
        TAX
        PLA
        PLP
        PLP
        RTS
    ''')
    assert code[RETURN_SCOPED - RETURN:RETURN_SCOPED - RETURN + 2] == bytes.fromhex('0838')
    assert len(code) < RETURN_END - RETURN
    return code.ljust(RETURN_END - RETURN, b'\xff')


def check_return():
    mem = bytearray(65536)
    mem[RETURN:RETURN_END] = return_code()
    cpu = MPU(memory=mem)
    count = 0
    for entry in (RETURN, RETURN_SCOPED):
        for incoming in (2, 0x8C, 0xD0):
            for published in (2, 0x8C, 0xD0, 0xE1):
                for depth in (0xA0, 0xF4):
                    for p in (0x30, 0x31, 0x34, 0xB0, 0xF1):
                        mem[0x7DA1] = mem[0x5116] = published
                        mem[0x101 + depth:0x104 + depth] = bytes((incoming, 0x64, 0x83))
                        cpu.pc, cpu.sp, cpu.a, cpu.x, cpu.y, cpu.p = entry, depth, 21, 31, 41, p
                        cpu.processorCycles = 0
                        while cpu.pc != 0x8365:
                            assert cpu.processorCycles < 100, (entry, incoming, published, depth, p)
                            cpu.step()
                        expect = incoming if entry == RETURN or published == 2 else published
                        assert (cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp) == (21, 31, 41, p, depth + 3)
                        assert mem[0x7DA1] == mem[0x5116] == expect
                        count += 1
    return count


def candidate_image(parent):
    image = bytearray(Layout.fixed_layout(parent, via_farcall=True))
    address = offset(126, Layout.SLOT)
    assert image[address:address + 2] == bytes.fromhex('a9f2')
    image[address + 1] = ADMISSION & 255
    guard_at = offset(69, GUARD)
    image[guard_at:guard_at + 185] = proposed_guard(parent)
    router_at = offset(87, START)
    image[router_at:router_at + END - START] = proposed_window(parent)
    wrapper = assemble(0xBF94, '''
        LDA $7DA1
        PHA
        LDA #$02
        STA $7DA1
        STA $5116
        JSR $8798
        DEC $01FA
        JMP $BF1C
    ''')
    assert len(wrapper) == 21
    tail = bytes.fromhex('4ce4b0') + wrapper + worker_code(FAST)
    assert len(tail) == COOKIE - TAIL == 79
    payload_at = Layout.Current.P.CHR + 935 * 1024
    tail_at = payload_at + 8192 + TAIL
    assert image[tail_at:tail_at + len(tail)] == b'\xff' * len(tail)
    image[tail_at:tail_at + len(tail)] = tail
    return_at = payload_at + 8192 + (RETURN & 8191)
    original_return = bytes.fromhex('08488a489848babd05018da17d8d1651bd04019d0501bd0301'
                                    '9d0401bd02019d0301bd01019d0201e89a68a868aa682860')
    assert image[return_at:return_at + len(original_return)] == original_return
    image[return_at:return_at + len(original_return)] = return_code()
    digest = Hud.H(image[payload_at:payload_at + 24 * 1024])
    cookie = bytes.fromhex('a71f0005') + bytes.fromhex(digest)[:12]
    for at in (573373, 642966):
        assert parent[at:at + 16] == bytes.fromhex('a71f00053a7d2d9a77d5accd30e79766')
        image[at:at + 16] = cookie
    return bytes(image), tail, cookie


def normalize_payload(comparable, reference):
    for first, last in ((TAIL, COOKIE + 16), (RETURN & 8191, RETURN_END & 8191)):
        comparable.ram[2][first:last] = reference.ram[2][first:last]


def position(m):
    get = Layout.N.get
    return tuple(get(m, name) for name in ('OperMode', 'OperMode_Task', 'GameEngineSubroutine',
                                          'Player_PageLoc', 'Player_X_Position', 'Player_Y_Position',
                                          'PlayerStatus', 'NumberofLives', 'FrameCounter'))


def cold_menu(bundle, name, slot, inputs, selects):
    n, w = Layout.N, Layout.Current.W
    with patch.object(n, 'Bus', w.ControllerBus):
        model = w.UI.seed(bundle, 0)
    for buttons in inputs:
        w.UI.key(model, buttons)
    assert n.get(model, 'CrossoverMenuIndex') == slot
    for _ in range(selects):
        w.UI.key(model, 32)
    assert w.UI.menu_name(model)[0] == name
    if slot == 30:
        assert n.get(model, 'SelectedCharacter') == 31
        assert (n.get(model, 'FmGroups') >> 3) & 3 == selects
    assert not any(model.ram[2][COOKIE:COOKIE + 16]), 'Boot fixture must start unloaded'
    start = w.UI.key(model, 16)
    n.invoke(model, 'NativeRareGameMenuRoutineCore::ChkContinue',
             a=start['A'], x=start['X'], y=start['Y'], p=start['P'])
    n.invoke(model, 'PauseRoutine', a=0)
    return model


def interrupt_scope(original, candidate):
    # Fire the real handler at paired gameplay boundaries. A busy NMI still
    # updates audio and other interrupt state, so the control also needs it.
    n, frames = Layout.N, Layout.Frames
    cuts = (
        ((254, 0x8798), (197, 0xBFA3), 'marked before mapping', 0x84),
        ((254, 0x8798), (2, 0xBF9D), 'between mapper writes', 0x84),
        ((215, 0xB0A9), (215, 0xB0A7), 'public service gate', 0x84),
        ((215, 0xB0A9), (2, FAST), 'fast service entry', 0x84),
        ((2, 0xCA0B), (2, 0xCA0B), 'worker transport', 0x84),
        ((254, 0x8350), (2, 0xBFA3), 'native tree returned', 0x84),
        ((254, 0x8350), (2, RETURN_SCOPED), 'scope returned', 0x83),
        ((254, 0x8350), (2, 0xBF3E), 'return status restored', 0x83),
    )

    def run_cut(seed, at, label, kind, expected_marker=None):
        bank, address = at
        model = n.fork(seed)
        model.controller_pad = 0
        sample = []
        mode_entered = False
        retirement_entered = False

        def compare_cut(m, cpu):
            nonlocal mode_entered, retirement_entered
            if sample or cpu.pc < 0x8000:
                return
            location = (m.rawtags[(cpu.pc - 0x8000) // 8192], cpu.pc)
            if location == (254, 0x8798):
                mode_entered = True
            if location == (2, RETURN_SCOPED):
                retirement_entered = True
            if location != (bank, address):
                return
            if address in (0xB0A9, 0xCA0B) and not mode_entered:
                return
            if expected_marker is not None and m[0x1FA] != expected_marker:
                return
            if address == 0xBF3E and not retirement_entered:
                return
            state = registers(cpu)
            params = bytes(m[0x15A:0x17B])
            assert m[0x139] & 128, (label, 'Expected busy foreground')
            cpu.nmi() if kind == 'NMI' else cpu.irq()
            delivered = (cpu.pc, cpu.sp) != (address, state[-1])
            lowest_sp = cpu.sp
            for _ in range(10000):
                if (cpu.pc, cpu.sp) == (address, state[-1]):
                    break
                assert m[cpu.pc], (kind, label, hex(cpu.pc), 'BRK')
                cpu.step()
                lowest_sp = min(lowest_sp, cpu.sp)
            else:
                raise AssertionError((kind, label, 'Interrupt did not return'))
            assert state == registers(cpu), (kind, label, state, registers(cpu))
            assert expected_marker is None or m[0x1FA] == expected_marker
            assert bytes(m[0x15A:0x17B]) == params, (kind, label, 'Farcall parameters changed')
            assert lowest_sp >= 0x7B and delivered, (kind, label, lowest_sp, delivered)
            sample.append(dict(site=label, kind=kind, delivered=delivered, lowest_sp=lowest_sp))

        frames.frame(model, observe=compare_cut, whole_pass=True)
        assert len(sample) == 1, (label, kind, at, 'Cut was not reached')
        return model, sample[0]

    results = []
    for old_at, new_at, label, marker in cuts:
        for kind in ('IRQ', 'NMI'):
            before, a = run_cut(original, old_at, label, kind)
            after, b = run_cut(candidate, new_at, label, kind, marker)
            normalize_payload(after, before)
            try:
                Layout.compare(before, after, allow_backup=kind == 'NMI')
            except AssertionError as error:
                raise AssertionError((label, kind, a, b, error)) from error
            results.append(b)
            print('INTERRUPT ' + json.dumps(b), flush=True)
    print('INTERRUPTS ' + json.dumps(dict(cases=len(results),
                                          lowest_sp=min(row['lowest_sp'] for row in results))), flush=True)


def cold_candidate(parent, picks, *, interrupts=False):
    raw, tail, cookie = candidate_image(parent)
    bundle = Layout.Current.bindings(Hud.inverse(parent))['bundle']
    old = dict(bundle, raw=parent)
    symbols = dict(bundle['syms'])
    pause = symbols['PauseRoutine']
    assert int(pause['val'], 0) == Layout.PAUSE
    symbols['PauseRoutine'] = dict(pause, val=hex(Layout.NEW_PAUSE))
    new = dict(bundle, raw=raw, syms=symbols)
    print('IMAGE ' + Hud.H(raw), flush=True)
    for name, slot, inputs, selects in picks:
        original, candidate = (cold_menu(b, name, slot, inputs, selects) for b in (old, new))
        sites = Counter()
        services = Counter()

        def trace(m, cpu):
            if cpu.pc < 0x8000:
                return
            owner = m.rawtags[(cpu.pc - 0x8000) // 8192]
            if (owner, cpu.pc) == (197, ADMISSION):
                assert cpu.sp == 0xF5 and bytes(m[0x1F9:0x1FB]) == bytes.fromhex('5283')
                sites['admission'] += 1
            elif (owner, cpu.pc) == (197, 0xBFA8):
                sites['fallback'] += 1
            elif (owner, cpu.pc) == (2, FAST):
                assert m[0x1FA] == 0x84 and m[0x6002] == 31 and m[0x7DA1] == 2
                sites['fast'] += 1
                services['fast', cpu.x // 3, m[0x7DA1]] += 1
            elif (owner, cpu.pc) == (215, SLOW):
                services['slow', cpu.x // 3, m[0x7DA1]] += 1
                sites['slow'] += 1
            elif (owner, cpu.pc) == (254, Layout.SLOT + Layout.SLOT_LENGTH):
                assert m[0x1FA] == 0x83
                sites['return'] += 1

        for epoch in range(700):
            state = position(original)
            assert position(candidate) == state, (name, epoch, state, position(candidate))
            if state[:3] == (1, 3, 8):
                break
            for m in (original, candidate):
                m.controller_pad = 0
                Layout.Frames.frame(m, observe=trace if m is candidate else None, cold=True)
        else:
            raise AssertionError(('Cold stage entry bound', name, state))
        if slot == 30:
            assert sites['fallback'], 'Cold calls must reach the ordinary route before loading RAM2'
            assert bytes(candidate.ram[2][TAIL:COOKIE]) == tail
            variant_cookie = cookie[:2] + bytes((selects,)) + cookie[3:]
            assert bytes(candidate.ram[2][COOKIE:COOKIE + 16]) == variant_cookie
        else:
            assert not sites['fast']
            assert not any(candidate.ram[2][COOKIE:COOKIE + 16])

        def compare_models():
            comparable = Layout.N.fork(candidate)
            normalize_payload(comparable, original)
            Layout.compare(original, comparable)

        print('COLD ' + json.dumps(dict(character=name, epochs=epoch, state=state,
                                       sites=sites, services=[(*key, count) for key, count in services.items()],
                                       c_maps=[m[0x7DA1] for m in (original, candidate)])), flush=True)
        compare_models()
        if interrupts and name == 'BURNS':
            interrupt_scope(original, candidate)
        for phase, buttons in (('idle', 0), ('walk', 1), ('pause', 16), ('paused', 0)):
            sites.clear()
            services.clear()
            original.controller_pad = candidate.controller_pad = buttons
            before = Layout.Frames.frame(original, whole_pass=True)
            after = Layout.Frames.frame(candidate, observe=trace, whole_pass=True)
            print('PLAY ' + json.dumps(dict(character=name, phase=phase, original=before,
                                           candidate=after, sites=sites,
                                           services=[(*key, count) for key, count in services.items()])),
                  flush=True)
            compare_models()
            if phase == 'paused':
                assert Layout.N.get(candidate, 'GamePauseStatus') & 1
            if slot == 30 and phase in ('idle', 'walk'):
                assert sites['fast'] and sites['admission'] == sites['return'] == 1
            if slot != 30:
                assert not sites['fast'] and sites['fallback'] == sites['admission']


def warm_candidate(parent):
    """Exercise the exact assembled path from an already-loaded Burns stage."""
    raw, tail, cookie = candidate_image(parent)
    print('IMAGE ' + json.dumps(dict(SHA256=Hud.H(raw), tail=Hud.H(tail), cookie=cookie.hex())), flush=True)
    seed = Layout.cold(parent)
    for _ in range(4):
        Layout.Frames.frame(seed, whole_pass=True)
    original = Layout.N.fork(seed)
    candidate = Layout.backing(Layout.N.fork(seed), raw)
    # Explicit warm fixture: install the exact new loader payload and header
    # in the already-loaded RAM2 image. Cold loader tests are separate.
    candidate.ram[2][TAIL:COOKIE] = tail
    candidate.ram[2][COOKIE:COOKIE + 16] = cookie
    candidate.ram[2][RETURN & 8191:RETURN_END & 8191] = return_code()
    for phase, pad in (('idle', 0), ('walk', 1)):
        original.controller_pad = candidate.controller_pad = pad
        scopes = Counter()

        def trace(m, cpu):
            if cpu.pc < 0x8000:
                return
            owner = m.rawtags[(cpu.pc - 0x8000) // 8192]
            if (owner, cpu.pc) == (197, ADMISSION):
                assert cpu.sp == 0xF5 and bytes(m[0x1F9:0x1FB]) == bytes.fromhex('5283')
                scopes['admission'] += 1
            elif (owner, cpu.pc) == (2, FAST):
                assert m[0x1FA] == 0x84 and m[0x6002] == 31 and m[0x7DA1] == 2
                scopes['fast'] += 1
            elif (owner, cpu.pc) == (215, SLOW):
                scopes['slow'] += 1
            elif (owner, cpu.pc) == (254, Layout.SLOT + Layout.SLOT_LENGTH):
                assert m[0x1FA] == 0x83, 'Restore the live return marker before unwinding'
                scopes['return'] += 1

        before = Layout.Frames.frame(original, whole_pass=True)
        after = Layout.Frames.frame(candidate, observe=trace, whole_pass=True)
        print('WARM ' + json.dumps(dict(phase=phase, original=before, candidate=after, sites=scopes)), flush=True)
        assert scopes['admission'] == scopes['return'] == 1
        assert scopes['fast'] > 0 and scopes['fast'] + scopes['slow'] == 14
        compare = Layout.N.fork(candidate)
        normalize_payload(compare, original)
        Layout.compare(original, compare)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--warm', action='store_true')
    parser.add_argument('--cold', nargs='+', choices=('Burns', 'Smith', 'Iron', 'Beans', 'Mario'))
    parser.add_argument('--interrupts', action='store_true', help='Exercise the real handlers after Burns boots.')
    args = parser.parse_args()
    if args.interrupts and 'Burns' not in (args.cold or []):
        parser.error('--interrupts requires --cold Burns')
    parent = Hud.ROM.read_bytes()
    print(json.dumps(dict(check(parent), return_checks=check_return()), sort_keys=True), flush=True)
    if args.warm:
        warm_candidate(parent)
    if args.cold:
        names = ('Burns', 'Smith', 'Iron', 'Beans')
        picks = [(name.upper(), 30, [4] * 3 + [1] * 6, names.index(name))
                 if name in names else ('MARIO', 0, (), 0) for name in args.cold]
        cold_candidate(parent, picks, interrupts=args.interrupts)
