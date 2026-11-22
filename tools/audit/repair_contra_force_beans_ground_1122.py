"""Keep Beans' floor placements inside the existing source projectile plane.

The old image remains an exact input.  No ROM, receipt, or capture is written.
Run this source proof through run_bounded_build_v1.py, with an absent output.
"""

from hashlib import sha256
import json
from pathlib import Path
import re
from unittest.mock import patch


PARENT = 'a6d91e368657a0ee1458391542e98adafcec45991ebecbe4521a648513cfa4df'
CANDIDATE = '32eaf1786695d7ac1e69eb4957cc76dee011664e642710d02acc7ae624ca3ad1'
R = Path(__file__).resolve().parents[2]
ROM = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
CARRIER = 2006032
TAIL = CARRIER + 0x1FE0
GATE = CARRIER + 16384 + 0x1AA2
COOKIES = (573373, 642966)
OLD_COOKIE = bytes.fromhex('a71f0005ff0c57ddec18b1627a5cf6a5')
GATE_BEFORE = bytes.fromhex('0848a9d78decc2a9a48dedc2a9018deec268284c0bca')
# The original motion leaf still executes in RAM1.  Its sole phase-gate
# caller next reloads shot Y and compares it, replacing A/N/Z/C. X/Y and V
# remain unchanged. Only class3 kinds7/13 at exactlyY200 are normalized.
HELPER = bytes.fromhex(
    '20d7a4'       # BFE0 JSR original sub_0x008E29, RAM1:A4D7
    'ade0c2c903d015'  # source class must be Beans
    'bd82c3c907f004c90dd00a'  # placed bomb7 or mine13
    'bd68c3c9c8d003de68c3'    # exactly200 becomes199
    '60'
)
HELPER_SOURCE = '''
    JSR $A4D7
    LDA $C2E0
    CMP #$03
    BNE ${done:04x}
    LDA $C382,X
    CMP #$07
    BEQ ${placement:04x}
    CMP #$0D
    BNE ${done:04x}
placement:
    LDA $C368,X
    CMP #$C8
    BNE ${done:04x}
    DEC $C368,X
done:
    RTS
'''


def digest(raw):
    return sha256(raw).hexdigest()


def _compose(raw):
    assert isinstance(raw, bytes) and digest(raw) == PARENT
    assert len(HELPER) == 32 and raw[TAIL:TAIL + 32] == b'\xff' * 32
    assert raw[GATE:GATE + len(GATE_BEFORE)] == GATE_BEFORE
    assert all(raw[at:at + 16] == OLD_COOKIE for at in COOKIES)
    # This gate has exactly one direct caller in both complete A-code images.
    for bank, expected in ((1, []), (3, [0x3C3])):
        image = raw[CARRIER + (bank - 1) * 8192:CARRIER + bank * 8192]
        assert [m.start() for m in re.finditer(b'\x20\xa2\xba', image)] == expected
    assert raw[CARRIER + 16384 + 0x3C3:CARRIER + 16384 + 0x3D0] == bytes.fromhex(
        '20a2babd68c3c9c890034ce7a3')
    image = bytearray(raw)
    image[TAIL:TAIL + 32] = HELPER
    image[GATE + 3], image[GATE + 8] = 0xE0, 0xBF
    cookie = OLD_COOKIE[:4] + bytes.fromhex(digest(image[CARRIER:CARRIER + 24576]))[:12]
    for at in COOKIES:
        image[at:at + 16] = cookie
    return bytes(image)


def compose(raw):
    result = _compose(raw)
    assert CANDIDATE and digest(result) == CANDIDATE
    return result


def inverse(raw):
    assert isinstance(raw, bytes) and CANDIDATE and digest(raw) == CANDIDATE
    restored = bytearray(raw)
    assert restored[TAIL:TAIL + 32] == HELPER
    restored[TAIL:TAIL + 32] = b'\xff' * 32
    restored[GATE:GATE + len(GATE_BEFORE)] = GATE_BEFORE
    for at in COOKIES:
        restored[at:at + 16] = OLD_COOKIE
    restored = bytes(restored)
    assert digest(restored) == PARENT and compose(restored) == raw
    return restored


def metadata(raw):
    candidate = compose(raw)
    spans = ((TAIL, 32), (GATE, len(GATE_BEFORE)), *((at, 16) for at in COOKIES))
    allowed = {i for at, size in spans for i in range(at, at + size)}
    changes = {i for i, (a, b) in enumerate(zip(raw, candidate, strict=True)) if a != b}
    assert changes <= allowed and inverse(candidate) == raw
    return dict(parent_SHA256=PARENT, candidate_SHA256=CANDIDATE,
                changed_bytes=len(changes), owned_bytes=len(allowed),
                exact_inverse=True, unaffected_ROM_bytes_identical=True,
                helper=dict(bank=1, pc=0xBFE0, bytes=len(HELPER)),
                gate=dict(bank=3, pc=0xBAA2, sole_caller=0xA3C3),
                spans=[dict(offset=at, before=raw[at:at + size].hex(),
                            after=candidate[at:at + size].hex()) for at, size in spans],
                ROM_files_written=0, native=False)


def proof(raw):
    import check_contra_force_combined_palette_1122 as Combined
    from check_contra_force_fast_route_1122 import compare

    F, L, N, W = Combined.Fast, Combined.Layout, Combined.Layout.N, Combined.Current.W
    assert F.assemble(0xBFE0, HELPER_SOURCE) == HELPER
    candidate = compose(raw)
    parent = Combined.comparison_base(raw)
    bundle = Combined.Current.bindings(F.Hud.inverse(parent))['bundle']
    syms = dict(bundle['syms'])
    syms['PauseRoutine'] = dict(syms['PauseRoutine'], val=hex(L.NEW_PAUSE))
    addr = lambda name: W.address(bundle, name)
    labels = {n: int(v, 16) for v, n in re.findall(
        r'al ([0-9A-Fa-f]+) \.(\w+)',
        (R / 'build/contra-force-projectile-contact-1031-v3/kernel/runtime.lbl').read_text())}
    # The delivered work-marker renderer moved this seam five bytes. Match
    # its complete borrowed-pointer prefix, rather than using the old label.
    record_prefix = bytes.fromhex('68a868aaa50348a5044886038404')
    code3 = raw[CARRIER + 16384:CARRIER + 24576]
    records = [m.start() for m in re.finditer(re.escape(record_prefix), code3)]
    assert records == [0x14FB]
    record_ready = 0xA000 + records[0] + len(record_prefix)
    assert record_ready == 0xB509 and code3[0x1509:0x150C] == bytes.fromhex('adde06')
    out = dict(metadata=metadata(raw), cold=[], unchanged=[], lanes=[], contacts=[],
               fixture_scope='Exact image cold menu/loading; later component gear/NPC/air setups disclosed. No natural-acquisition or Mesen claim.')

    def setv(m, **values):
        for name, value in values.items():
            m[addr(name)] = value

    def tick(m, pad):
        m.controller_pad = pad
        L.Frames.frame(m, whole_pass=True)

    def equal(a, b, label):
        q = N.fork(b)
        q.ram[1][0x1FE0:0x2000] = a.ram[1][0x1FE0:0x2000]
        q.ram[3][0x1AA2:0x1AA2 + len(GATE_BEFORE)] = a.ram[3][0x1AA2:0x1AA2 + len(GATE_BEFORE)]
        q.ram[2][0x1FE0:0x1FF0] = a.ram[2][0x1FE0:0x1FF0]
        compare(a, q, label, repair_death=True, repair_pickup=True)

    seeds = {}
    for variant, name in enumerate(('BURNS', 'SMITH', 'IRON', 'BEANS')):
        models = []
        for image in (raw, candidate):
            b = dict(bundle, raw=image, syms=syms)
            m = F.cold_menu(b, name, 30, [4] * 3 + [1] * 6, variant)
            for age in range(700):
                if F.position(m)[:3] == (1, 3, 8):
                    break
                m.controller_pad = 0
                L.Frames.frame(m, cold=True)
            else:
                raise AssertionError(('Cold bound', name))
            assert bytes(m.ram[1][0x1FE0:0x2000]) == image[TAIL:TAIL + 32]
            assert bytes(m.ram[3][0x1AA2:0x1AA2 + len(GATE_BEFORE)]) == image[GATE:GATE + len(GATE_BEFORE)]
            cookie = image[COOKIES[0]:COOKIES[0] + 16]
            assert bytes(m.ram[2][0x1FE0:0x1FF0]) == cookie[:2] + bytes((variant,)) + cookie[3:]
            for _ in range(4):
                tick(m, 0)
            models.append(m)
        equal(*models, ('Cold', name))
        seeds[variant] = models
        out['cold'].append(dict(variant=variant, cookies_loaded=True, actual_helper_loaded=True))
        print('COLD ' + name, flush=True)
        for tier in range(3):
            pair = [N.fork(m) for m in models]
            for m in pair:
                setv(m, PlayerStatus=tier)
                m.ram[2][0x7F + variant] = 0x10 | tier
                if variant == 3 and tier:
                    # An airborne placement stays outside the floor-only correction.
                    setv(m, Player_Y_Position=96, Player_State=1)
                    m.ram[2][0x4AA] |= 0x40
                    m.ram[2][0x4B4], m.ram[2][0x4D2] = 16, 0
            for age, pad in enumerate([0] * 4 + [64, 64] + [0] * 18):
                for m in pair:
                    tick(m, pad)
                equal(*pair, ('Unchanged', name, tier, age))
            out['unchanged'].append(dict(variant=variant, tier=tier, updates=24,
                                        airborne=variant == 3 and tier > 0))

    def component(tier, fixed, target=False):
        m = N.fork(seeds[3][int(fixed)])
        setv(m, PlayerStatus=tier)
        m.ram[2][0x82] = 0x10 | tier
        if target:
            for name, value in dict(Enemy_Flag=1, Enemy_ID=6, Enemy_State=0,
                                    Enemy_X_Position=96, Enemy_PageLoc=0,
                                    Enemy_Y_Position=176, Enemy_Y_HighPos=1).items():
                m[addr(name)] = value
            N.invoke(m, 'InitGoomba', x=0)
            # Let native gravity settle the initialized NPC. Eight updates
            # was an unqualified timing assumption, not a floor-state test.
            for settle in range(48):
                if N.get(m, 'Enemy_Y_Position') == 184:
                    break
                tick(m, 0)
            assert N.get(m, 'Enemy_Y_Position') == 184, ('Stock floor settling',
                N.get(m, 'Enemy_X_Position'), N.get(m, 'Enemy_Y_Position'))
        trace = dict(fixed=fixed, tier=tier, transitions=[], renders=[], hits=[],
                     allocations=[], retirements=[])
        frame = 0
        base_cpu = N.NesMPU

        class CPU(base_cpu):
            def step(self):
                tag = m.rawtags[(self.pc - 0x8000) // 8192] if self.pc >= 0x8000 else None
                if (tag, self.pc) == (1, 0xA0BA):
                    trace['allocations'].append(dict(update=frame, slot=self.y, kind=self.a,
                        x=m.ram[2][0x34E + self.y], y=m.ram[2][0x368 + self.y]))
                if (tag, self.pc) == (3, 0xA3E7):
                    if len(trace['retirements']) < 8:
                        trace['retirements'].append(dict(update=frame, kind=m.ram[2][0x382 + self.x],
                                                        y=m.ram[2][0x368 + self.x]))
                if (tag, self.pc) == (3, 0xB7F9):
                    shot, foe = m.ram[2][0x2FC], m.ram[2][0x2FD]
                    radius = m.ram[2][0x420 + shot]
                    radii = list(m.ram[2][(labels['tbl_F94A'] & 8191) + 2 * radius:
                                           (labels['tbl_F94A'] & 8191) + 2 * radius + 2])
                    trace['hits'].append(dict(update=frame, shot=shot,
                        shot_kind=m.ram[2][0x382 + shot], shot_y=m.ram[2][0x368 + shot],
                        radius_index=radius, radii=radii,
                        enemy=foe, enemy_x=N.get(m, 'Enemy_X_Position', foe),
                        enemy_y=N.get(m, 'Enemy_Y_Position', foe)))
                if (tag, self.pc) == (3, record_ready):
                    slot = m.ram[2][0x2F1]
                    if 10 <= slot < 22:
                        row = dict(update=frame, kind=m.ram[2][0x382 + slot],
                                   frame=m.ram[2][0x31A + slot],
                                   x=m.ram[2][0x34E + slot] + N.get(m, 'ScreenLeft_X_Pos'),
                                   y=m.ram[2][0x368 + slot],
                                   renderer_x=m.ram[2][0x2F3], renderer_y=m.ram[2][0x2F5])
                        if not trace['renders'] or any(row[k] != trace['renders'][-1][k]
                                                      for k in ('kind', 'frame', 'y')):
                            if len(trace['renders']) < 16:
                                trace['renders'].append(row)
                super().step()

        last = None
        with patch.object(N, 'NesMPU', CPU):
            for frame in range(320 if not target else 96):
                tick(m, 64 if frame == 1 else 0)
                live = [(i, m.ram[2][0x382 + i], m.ram[2][0x368 + i])
                        for i in range(10, 22) if m.ram[2][0x382 + i]]
                kinds = sorted({row[1] for row in live})
                if kinds != last:
                    trace['transitions'].append(dict(update=frame, kinds=kinds,
                                                     positions=[list(row) for row in live]))
                    last = kinds
                if trace['hits']:
                    assert N.get(m, 'Enemy_State') & 32
                    assert N.get(m, 'FloateyNum_Control') == 1
                    break
        trace['living_at_end'] = bool(last)
        trace['player_y'] = N.get(m, 'Player_Y_Position')
        trace['health_scope'] = 'No health/ability acquisition result inferred from component setup'
        return trace

    for tier in (1, 2):
        old, fixed = (component(tier, flag) for flag in (False, True))
        print('LANE ' + json.dumps(dict(tier=tier, old=old, fixed=fixed)), flush=True)
        assert old['retirements'] and not old['living_at_end']
        expected = 13 if tier == 1 else 7
        explosion = 26 if tier == 1 else 10
        assert old['allocations'] and old['allocations'][0]['kind'] == expected
        assert any(q['y'] == 200 for q in old['retirements'])
        assert any(expected in q['kinds'] for q in fixed['transitions'])
        assert any(explosion in q['kinds'] for q in fixed['transitions'])
        assert not fixed['living_at_end'] and not fixed['hits']
        assert fixed['renders'] and fixed['renders'][0]['y'] in (199, 200)
        assert any(q['y'] == 199 for q in fixed['renders'])
        out['lanes'].extend((old, fixed))
        old_hit, fixed_hit = (component(tier, flag, True) for flag in (False, True))
        assert not old_hit['hits'] and fixed_hit['hits']
        assert fixed_hit['hits'][0]['shot_y'] == 199 and fixed_hit['hits'][0]['enemy_y'] == 184
        out['contacts'].extend((old_hit, fixed_hit))
        print('BEANS LANE/CONTACT tier' + str(tier), flush=True)
    out.update(passed=True, native=False, outputs=0)
    return out


if __name__ == '__main__':
    installed = ROM.read_bytes()
    assert digest(installed) in (PARENT, CANDIDATE), 'Require the exact old or delivered new nightly'
    report = proof(inverse(installed) if digest(installed) == CANDIDATE else installed)
    encoded = json.dumps(report, sort_keys=True, separators=(',', ':'))
    print('BEANS_GROUND ' + encoded, flush=True)
    print('RECEIPT_SHA256 ' + digest(encoded.encode()), flush=True)
