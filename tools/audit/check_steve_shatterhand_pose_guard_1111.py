"""Check the fixed PRG96 lift pose guard through actual host callers in memory."""

from collections import Counter
from itertools import product
import json
from unittest.mock import patch

import check_steve_shatterhand_live_1111 as Stage
import check_steve_shatterhand_pose_live_1111 as Pose


C, H, N, W = Pose.Live.C, Pose.Live.H, Pose.Live.N, Pose.Live.W
SOURCE = H.ROOT / 'tools/reference/steve_shatterhand_pose_guard_1111.s'
MARKER = 0xa8
GRAPHICS = 0xa202
GATE = 0xc040
OLD_GRAPHICS = bytes.fromhex(
    'ad045cd0034c17a22904d0034c17a2a9008de10660a200a51ed0034c22a2a203'
    'ad055cd0034c4aa2ae0d5ce00af0034c39a2a2034c64a2ad055ca204c906b003'
    '4c64a2a2054c64a2a51ef0034c64a2a546d0034c64a2ad035c4a4a2903aabd67a2aa4c76a2'
)
FIELDS = ('JnHurt', 'JnAttack', 'JnWeapon', 'JnClock', 'Player_State',
          'Player_X_Speed', 'ObjectMetasprite')


def link(raw):
    bundle = W.Symbols.bundle()
    fields = {name: W.address(bundle, name) for name in FIELDS}
    fields['PoseCookieMarker'] = MARKER
    assert GRAPHICS + len(OLD_GRAPHICS) == 0xa267
    assert raw[C.offset(96, 0xa267):C.offset(96, 0xa26b)] == b'\x00\x01\x02\x01'
    linked = H.assemble(Pose.Live.bindings(fields) + SOURCE.read_text(),
                        {'POSE_GRAPHICS': (GRAPHICS, len(OLD_GRAPHICS)),
                         'POSE_ROM_GATE': (GATE, 14)})
    guard = linked['symbols']['StevePoseReady']
    assert guard == 0xa23f
    edits = []
    for at, old, key in ((C.offset(96, GRAPHICS), OLD_GRAPHICS, 'POSE_GRAPHICS'),
                         (C.offset(97, GATE), b'\xc1'*14, 'POSE_ROM_GATE')):
        assert raw[at:at+len(old)] == old, hex(at)
        edits.append((at, old, linked['images'][key].ljust(len(old), b'\xea')))
    assert len(linked['images']['POSE_GRAPHICS']) - (guard - GRAPHICS) == 38
    return tuple(edits), linked


def selector_parity(raw, candidate):
    keys = (*FIELDS[:-1], 'Player_Rel_XPos', 'Player_SprAttrib')
    bundle = W.Symbols.bundle()
    at = {key: W.address(bundle, key) for key in (*keys, 'Player_Pos_ForScroll', 'ObjectMetasprite')}
    before, after = [C.Common.blank(dict(bundle, raw=image)) for image in (raw, candidate)]
    for m in (before, after):
        m.raw_page(1, 0xe0)

    def run(m, values):
        for key, value in zip(keys, (*values, 49, 255), strict=True):
            m[at[key]] = value
        m[at['ObjectMetasprite']] = 49
        cpu = N.NesMPU(memory=m, pc=0xa1f4)
        cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = (83, 71, 109, 0x21, 224)
        cpu.stPushWord(0x5aff)
        for _ in range(50):
            if cpu.pc in (0x5b00, 0xa276):
                break
            assert m[cpu.pc]
            cpu.step()
        else:
            raise AssertionError(('JnGraphics instruction bound', hex(cpu.pc)))
        common = (cpu.pc, cpu.x, cpu.y, cpu.sp, m[at['Player_Pos_ForScroll']],
                  m[at['Player_SprAttrib']], m[at['ObjectMetasprite']])
        return common if cpu.pc == 0xa276 else (*common, cpu.a, cpu.p)

    cases = product((0, 1, 4, 0x84), (0, 1, 5, 6, 0xff), (0, 10, 11), (0, 4, 8, 12),
                    range(4), (0, 0xff))
    count = 0
    for values in cases:
        original = run(before, values)
        assert run(after, values) == original, (values, original)
        count += 1
    return count


def proposal(raw):
    candidate, info = Pose.proposal(raw)
    edits, linked = link(raw)
    assert all(candidate[at:at+len(new)] == new for at, _, new in edits)
    assert info['cookie'][0] == MARKER and info['pose_worker'][0xcf] == 0x8a
    return candidate, info, linked['symbols']['StevePoseReady']


def watch(guard, counts):
    def observe(m, cpu):
        tag_a, tag_c = m.rawtags[1:3]
        if (tag_a, cpu.pc) == (0xe0, guard):
            counts['guard'] += 1
        if (tag_c, cpu.pc) == (2, 0xcecf):
            counts['worker'] += 1
        if (tag_a, cpu.pc) == (0xe0, 0xa281):
            assert tag_c == 0xe1 and cpu.a in (0xc4, 0xd8, 0xdc)
            assert cpu.y == (2 if cpu.a == 0xc4 else 0)
            counts['stock'] += 1

    return observe


def opening(candidate, info, guard, fault=None):
    m = Stage.Scene.menu(dict(W.Symbols.bundle(), raw=candidate), 2)
    counts = Counter()
    visit = watch(guard, counts)
    verify = info['late_loader']['symbols']['SteveLateVerify']
    if isinstance(fault, tuple):
        m.corrupt_at = fault

    def observe(m, cpu):
        if isinstance(fault, int) and m.rawtags[2] == 2 and cpu.pc == verify and m[4] == fault >> 8:
            m.corrupt_at = (2, fault - 0xc000)
        visit(m, cpu)

    for update in range(16):
        C.Game.frame(m, observe)
        if counts['guard']:
            break
    assert counts['stock'] == counts['guard'] > 0, (fault, counts)
    headers = C.Common.headers(m)
    if fault is None:
        assert counts['worker'] == counts['guard'] and headers == (info['cookie'],)*2
    else:
        assert not counts['worker'] and all(header[0] == 0 for header in headers), (fault, counts, headers)
    return dict(update=update, **counts)


def stale_routes(raw, candidate, info, guard):
    with patch.object(N, 'Bus', W.ControllerBus):
        menu = W.UI.seed(dict(W.Symbols.bundle(), raw=candidate), 15)
    menu[0x5c8d] = 1
    for bank in (2, 3):
        menu.ram[bank][0x1fe0:0x1ff0] = info['cookie']
    for _ in range(2):
        W.UI.key(menu, 32)
    assert menu[0x730b] & 0x60 == 0x40 and menu[0x5c8d] == 1 and not menu[0x771]
    counts = Counter()
    C.Vector.call(menu, 'JnPortrait', observe=watch(guard, counts), x=0)
    assert counts == {'stock': 1}, counts

    warm, _ = Stage.opening(raw, 2)
    previous = C.Common.headers(warm)
    assert all(cookie[0] == 0xa7 for cookie in previous)
    warm.bundle = dict(warm.bundle, raw=candidate)
    for window, tag in enumerate(warm.rawtags):
        warm.raw_page(window, tag)
    counters = {}
    for label, markers, signature in (
            ('installed_a7', previous, None),
            ('foreign_raw2', (previous[0], info['cookie']), None),
            ('foreign_raw3', (info['cookie'], previous[1]), None),
            ('wrong_resident_entry', (info['cookie'],)*2, 0),
    ):
        m = C.Vector.clone(warm)
        for bank, header in zip((2, 3), markers, strict=True):
            m.ram[bank][0x1fe0:0x1ff0] = header
        if signature is not None:
            m.ram[2][0xecf] = signature
        counts = Counter()
        C.Vector.call(m, 'JnPortrait', observe=watch(guard, counts), x=0)
        assert counts == {'guard': 1, 'stock': 1}, (label, counts)
        counters[label] = dict(counts)
    return dict(menu={'stock': 1}, **counters)


def main():
    raw = Pose.A.D.HOST.read_bytes()
    candidate, info, guard = proposal(raw)
    print(json.dumps(dict(candidate=C.digest(candidate), selector_parity=selector_parity(raw, candidate),
                          guard=f'{guard:04x}', cookie=info['cookie'].hex(), outputs=0)), flush=True)
    print(json.dumps(dict(ordinary=opening(candidate, info, guard),
                          stale=stale_routes(raw, candidate, info, guard))), flush=True)
    faults = (0xce00, 0xcfff, 0xd000, 0xd3ff, 0xd400, 0xd77f, 0xd780, 0xd7ff,
              (3, 0x1c00), (2, 0x1a80))
    for fault in faults:
        print(json.dumps(dict(fault=fault, result=opening(candidate, info, guard, fault))), flush=True)


if __name__ == '__main__':
    main()
