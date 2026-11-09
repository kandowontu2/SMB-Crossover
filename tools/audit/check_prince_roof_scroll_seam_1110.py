"""Trace the Prince roof regression and test an edge-selector repair in memory."""

import argparse
from collections import Counter
import csv
from itertools import product
import json
from pathlib import Path

from prepare_prince_roof_jump_1110_v2 import Current, I, N, P, R, ROM, Stage, terrain
from check_prince_run_support_funded_irq_1110 import Async


NATIVE = R / 'build/prince-run-support-v2-1110/native/capture'
ROOF = NATIVE.parent.parent / 'roof-jump-plan.json'
START, END = 0xaa44, 0xaa52
OLD = bytes.fromhex('8503a0000ab007c8a5032920f01c')
# Preserve GetXOffscreenBits' Y on the negative/sentinel lane. The clear-bit
# lane still supplies Y=1 for its right-edge test. All existing targets stay.
NEW = bytes.fromhex('85030ab009a001a5032920f01dea')
EDGE, EXIT = 0xaa52, 0xaa6e
PLAYER_X, PLAYER_PAGE = 0x75, 0x5c
X_CLAMP, PAGE_CLAMP = 0xaa59, 0xaa60


def native():
    outcome = Current.read(NATIVE / 'third-pipe.json')
    assert not outcome['passed'] and outcome['ROM_sha256'] == Stage.PIN
    with (NATIVE / 'source-phases.csv').open(newline='') as file:
        observations = []
        for row in csv.DictReader(file):
            if 1243 <= int(row['wrappers']) <= 1255 and row['event'] in (
                    'controls', 'phase0-call', 'original-advance-return'):
                observations.append(dict(event=row['event'], Main=int(row['wrappers']),
                                         x=int(row['world_x']), pose=int(row['source_frame']),
                                         sole=int(row['physical_foot'])))
    assert any((p['Main'], p['event'], p['x'], p['pose']) == (1245, 'original-advance-return', 772, 40)
               for p in observations)
    assert any(p['x'] == 533 and p['pose'] == 40 for p in observations)
    return observations


def patch(bundle):
    assert len(OLD) == len(NEW) == END - START
    assert I.address(bundle, 'KeepOnscr') == EDGE and I.address(bundle, 'InitPlatScrl') == EXIT
    assert I.address(bundle, 'ScrollHandler') == 0xa9d4 and I.address(bundle, 'GetXOffscreenBits') == 0x8b1a
    at = I.location(bundle, 'KeepOnscr') - len(OLD)
    assert at == 16 + 8192 + START - 0xa000
    raw = bundle['raw']
    assert raw[at:at+len(OLD)] == OLD
    fixed = raw[:at] + NEW + raw[at+len(OLD):]
    return dict(bundle, raw=fixed), dict(offset=at, physical_PRG=1, CPU_half_open=[START, END],
                                        preimage=OLD.hex(), replacement=NEW.hex())


def layout(m, left, x, *, owner=38, lock=0, side=0, scroll=5, buttons=1, platform=0):
    right = (left + 255) & 0xffff
    x &= 0xffff
    N.put(m, ScreenLeft_X_Pos=left & 255, ScreenLeft_PageLoc=left >> 8,
          ScreenRight_X_Pos=right & 255, ScreenRight_PageLoc=right >> 8,
          Player_X_Position=x & 255, Player_PageLoc=x >> 8,
          Player_Pos_ForScroll=(x - left) & 255, ScrollLock=lock, SideCollisionTimer=side,
          Player_X_Scroll=scroll & 255, SelectedCharacter=owner, Left_Right_Buttons=buttons,
          Platform_X_Scroll=platform & 255, Player_X_Speed=0x17, ScrollThirtyTwo=13,
          Mirror_PPUCTRL=0xa0, ScrollAmount=0x79, HorizontalScroll=left & 255)


def xcamera(m):
    return tuple(N.get(m, stem + '_X_Pos') + 256 * N.get(m, stem + '_PageLoc')
                 for stem in ('ScreenLeft', 'ScreenRight'))


def record(m):
    return dict(Current.row(m, 0), left=xcamera(m)[0], right=xcamera(m)[1],
                scroll=N.get(m, 'Player_X_Scroll'), relative=m[0x75a], bits=m[3])


def trajectory(base, fixed, seed):
    e, m, labels = P.Q.first8(base, seed)

    def tiles(left):
        def tile(x, y):
            if y >= 208:
                return 0x54
            if not left <= x < left + 32 or y < 144:
                return 0
            return (0x12 if y < 160 else 0x14) + int(x >= left + 16)
        return tile

    terrain(m, tiles(192))
    previous_pose, controls, ref = None, [], None
    for epoch in range(320):
        s = Current.row(m, epoch)
        assert s['engine'] == 8 and s['hp'] == 5 and s['lives'] == 2
        pad = 1 if epoch < 77 or epoch >= 217 else 0 if epoch < 113 else 8
        if epoch in (257, 258):
            pad = 129
        if epoch >= 257 and s['frame'] != previous_pose:
            controls.append(s)
            previous_pose = s['frame']
        if s['action'] == 4 and s['frame'] == 39 and m.ram[2][0xa6] & 3 == 1:
            ref = s
            break
        m.controller_pad = pad
        N.put(m, SavedJoypad1Bits=pad, SavedJoypadBits=pad)
        e['run'](m, 'GameLoop', labels)
    assert ref is not None, (controls[-8:], m.ram[2][0xa6])
    # Replay the identical donor animation phase with the real native start X,
    # authored third-pipe map and a right edge that reconstructs the native snap.
    # The native V2 capture does not include the actual camera position.
    traces = {}
    cpu = N.NesMPU
    watches = {START, EDGE, X_CLAMP, PAGE_CLAMP, 0xc383, 0xc3a9}
    for name, bundle in [('original', base), ('proposed', fixed)]:
        q = N.fork(m)
        q.bundle = bundle
        for slot, tag in enumerate(q.rawtags):
            if tag & 128:
                q.raw_page(slot, tag)
        terrain(q, tiles(224))
        layout(q, 533, 772, scroll=0)
        rows = []
        updates = []

        class Trace(cpu):
            def step(self):
                if self.memory is not q:
                    return super().step()
                pc, tag = self.pc, q.rawtags[(self.pc - 0x8000) // 8192] if self.pc >= 0x8000 else None
                before = (q[PLAYER_X], q[PLAYER_PAGE])
                watch = pc in watches and tag in (129, 2)
                registers = self.a, self.x, self.y, self.p
                result = super().step()
                after = (q[PLAYER_X], q[PLAYER_PAGE])
                if watch or before != after:
                    rows.append(dict(update=update, PC=pc, bank=tag, registers=registers, before=list(before),
                                     after=list(after), **record(q)))
                return result

        N.NesMPU = Trace
        try:
            initial = record(q)
            for update in range(4):
                q.controller_pad = 1
                N.put(q, SavedJoypad1Bits=1, SavedJoypadBits=1)
                pre = N.fork(q)
                e['run'](q, 'GameLoop', labels)
                updates.append(record(q))
                if q.ram[2][0x617] == 40:
                    break
            traces[name] = dict(initial=initial, result=record(q), writes=rows, updates=updates)
        finally:
            N.NesMPU = cpu
        if name == 'proposed':
            # Follow the real donor cadence without further rebasing. The real
            # stage's Goombas are not part of this isolated geometry fixture.
            flight = []
            for update in range(72):
                q.controller_pad = 1
                N.put(q, SavedJoypad1Bits=1, SavedJoypadBits=1)
                e['run'](q, 'GameLoop', labels)
                row = record(q)
                if not flight or flight[-1]['frame'] != row['frame']:
                    flight.append(row)
                if row['x'] >= 784 and row['y'] == 176 and row['native_state'] == 0:
                    break
            traces[name]['unseeded_remaining_flight'] = flight
            traces[name]['continuation'] = record(q)
    return dict(control_reference=ref, ordinary_pose_trace=controls, actual_GameLoop=traces), pre, e, labels


def direct(before, after):
    # The leaf doesn't access hardware registers. The stock camera computation
    # and the shared packed-X helper execute directly from the exact PRG windows.
    seeds = [N.Bus(b) for b in (before, after)]
    cpus = []
    for m in seeds:
        m.raw_page(1, 129)
        cpus.append(N.NesMPU(memory=m))
    comparisons = Counter()
    domain = set(product((0, 1, 127, 255), (0, 1, 15, 32, 127, 244, 255),
                         range(-60, 320), ('normal', 'lock', 'side'), (38,), (1,), (0,)))
    domain.update(product((0, 1, 127, 255), (0, 127, 255),
                          (-61, -1, 0, 7, 79, 80, 111, 112, 223, 231, 232, 239, 240, 247,
                           248, 254, 255, 256, 257, 263, 271, 287, 319),
                          ('normal', 'lock', 'side'), (0, 38, 41), (1, 2), (-5, 0, 5)))
    for left_page, low, relative, gate, owner, buttons, platform in sorted(domain):
        left = 256 * left_page + low
        initial_x = (left + relative) & 0xffff
        observed = []
        for c in cpus:
            m = c.memory
            m.writes.clear()
            m[3:11] = [0x71, 0x23, 0x56, 0xb2, 0x19, 0x8a, 0x77, 0x82]
            layout(m, left, initial_x, owner=owner, lock=int(gate == 'lock'), side=int(gate == 'side'),
                   scroll=5 if relative >= 0 else -5, buttons=buttons, platform=platform)
            m[0x0f] = 8
            m.writes.clear()
            c.pc, c.sp, c.a, c.x, c.y, c.p = 0xa9d4, 224, 0x71, 7, 51, 0x61
            c.stPushWord(0x5aff)
            edge, low_y, bits = None, None, None
            for _ in range(240):
                if c.pc == 0x5b00:
                    break
                if c.pc == START:
                    low_y, bits = c.y, c.a
                if c.pc == EDGE:
                    edge = c.y
                assert m[c.pc] != 0, hex(c.pc)
                c.step()
            assert c.pc == 0x5b00 and c.sp == 224
            observed.append(dict(edge=edge, rawY=low_y, bits=bits, camera=xcamera(m),
                                 x=m[PLAYER_X] + 256*m[PLAYER_PAGE], speed=N.get(m, 'Player_X_Speed'),
                                 scratch=tuple(m[3:11]), regs=(c.a,c.x,c.y,c.p,c.sp), writes=m.writes[:]))
        a, b = observed
        assert all(a[k] == b[k] for k in ('rawY', 'bits', 'camera', 'scratch'))
        assert a['rawY'] in (0, 1, 255)
        if a['bits'] & 128 and a['rawY'] == 1:
            assert a['bits'] == 255 and a['edge'] == 0 and b['edge'] == 1
            assert a['x'] == a['camera'][0] and b['x'] == ((a['camera'][1] - 16) & 0xffff)
            assert 0 < ((initial_x - a['camera'][1]) & 0xffff) < 128
            assert (a['speed'], b['speed']) == ((0x17, 0) if buttons == 1 else (0, 0x17))
            fields = {PLAYER_X, PLAYER_PAGE, I.address(before, 'Player_X_Speed')}
            assert [p for p in a['writes'] if p[0] not in fields] == [p for p in b['writes'] if p[0] not in fields]
            comparisons['beyond_right_correct_edge'] += 1
        else:
            assert a == b, (left, relative, gate, owner, buttons, a, b)
            comparisons['unchanged'] += 1
            comparisons['unchanged_left_clamp' if a['edge'] == 0 else
                        'unchanged_right_clamp' if a['edge'] == 1 else 'unchanged_no_clamp'] += 1
    return comparisons


def vectors(seed, e, labels):
    N.put(seed, NmiDisable=255)
    # This is the reconstructed failing update's real stack and carries the
    # exact positive right-side sentinel through the changed bank 1 code.
    roof = Async.stress('genuine GameLoop reconstructed pose39 to pose40', seed,
                        lambda m: e['run'](m, 'GameLoop', labels)['regs'],
                        [(129, START, EXIT + 6)])
    views = [roof]
    for name, rel in (('left clamp', -5), ('ordinary right clamp', 252), ('interior', 112)):
        q = N.fork(seed)
        layout(q, 0x01fa, 0x01fa + rel, owner=0, lock=1)
        # Model the steady stock camera path. The source-backed Prince seed
        # carries a pending guest CHR reload that owner 0's FF handler would
        # legitimately publish. The real Prince GameLoop case keeps it live.
        N.put(q, ReloadCHRBank=0)
        def leaf(m):
            result = N.invoke(m, 'ScrollHandler', p=0x61)
            # Py65 RTI exposes the stack B marker in P. The 2A03 has no B latch.
            return result['A'], result['X'], result['Y'], result['P'] & 0xef
        views.append(Async.stress(name, q, leaf, [(129, 0xa9d4, EXIT + 6)]))
    return views


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--trace-only', action='store_true')
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(R / 'build') and not (output / 'proof.json').exists()
    output.mkdir(exist_ok=True)
    old, _, _ = Current.current()
    raw = ROM.read_bytes()
    assert P.sha(raw) == Stage.PIN
    base = dict(old, raw=raw)
    fixed, span = patch(base)
    seed, _ = P.Q.C.C.cold(base, 38)
    original = native()
    route, stack_seed, e, labels = trajectory(base, fixed, seed)
    (output / 'trace.json').write_text(json.dumps(dict(native=original, reconstructed=route), indent=2)+'\n')
    for k, row in route['actual_GameLoop'].items():
        print(k, row['initial'], row['result'], flush=True)
        print([(hex(w['PC']),w['bank'],w['before'],w['after'],w['source_x'],w['bits'],w['registers'][2])
               for w in row['writes']], flush=True)
    if args.trace_only:
        return
    assert route['actual_GameLoop']['original']['result']['x'] == 533
    assert route['actual_GameLoop']['proposed']['result']['x'] == 772
    a, b = (route['actual_GameLoop'][k] for k in ('original', 'proposed'))
    for o, side in ((a, 0), (b, 1)):
        projected, = [w for w in o['writes'] if w['PC'] == 0xc3a9 and w['source_x'] == 804]
        assert projected['x'] == 796
        raw, = [w for w in o['writes'] if w['PC'] == START and w['source_x'] == 804]
        assert (raw['registers'][0], raw['registers'][2], raw['relative']) == (255, 1, 7)
        clamp, = [w for w in o['writes'] if w['PC'] == PAGE_CLAMP]
        assert clamp['registers'][2] == side and clamp['x'] == o['result']['x']
        assert (o['result']['y'], o['result']['foot'], o['result']['frame']) == (111, 143, 40)
    landing = b['continuation']
    assert (landing['x'], landing['y'], landing['native_state'], landing['hp'], landing['lives']) == (795, 176, 0, 5, 2)
    scope = direct(base, fixed)
    print(json.dumps(scope), flush=True)
    irqs = vectors(stack_seed, e, labels)
    q = dict(passed=True, ROM_written=False, Mesen_run=False, parent_SHA256=Stage.PIN,
             expected_memory_only_SHA256=P.sha(fixed['raw']), patches=[span], direct=scope, vectors=irqs,
             direct_vector_P_comparison='Ignore only the non-latched B stack marker. Original leaf IRQ comparison '
                                        'reported P=23 vs P=33 (hex); all hardware flags remain exact.',
             stock_vector_setup='Stock steady-state leaf starts with ReloadCHRBank=0. An earlier raw0 leaf reused '
                                'Prince\'s pending reload and the genuine FF handler published CHR as specified in '
                                'reset.s. Genuine Prince GameLoop vectors keep the live publication state.',
             scope='Explicit reconstructed camera/terrain CPU inputs. Native V2 shows the same regression but did not record '
                   'camera or the bus writer. The proposal keeps right-edge clamping and can still restrict speed. '
                   'No actual stage crossing, enemy contact change, or native writer capture claimed.',
             bindings={str(p.resolve().relative_to(R)):P.sha(p.read_bytes()) for p in
                       (Path(__file__), ROM, ROOF, NATIVE/'third-pipe.json', NATIVE/'source-phases.csv',
                        R/'src/player.s', R/'src/common.s', R/'src/vic_adapter.s',
                        Path(Async.__file__), output/'trace.json')})
    (output/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(irqs), flush=True)


if __name__ == '__main__':
    main()
