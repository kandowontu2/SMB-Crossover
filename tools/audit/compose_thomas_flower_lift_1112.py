"""Compose and qualify Thomas's authored-flower vertical platform in memory."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from unittest.mock import patch

import check_thomas_powerups_current_1112 as Thomas
import check_helper_camera_admission_1110_v1 as Cam
import check_sonic_native_effects_vectors_1110 as Vectors
from check_thomas_powerup_progression_1110 import Asm


R, N, W = Thomas.W.R, Thomas.N, Thomas.W
SOURCE = R/'tools/reference/thomas_flower_lift_1112.s'
START = Cam.TH_CHR
COOKIE = 702649
LEFT = 1200
ORIGINAL = Cam.TH_LEFTS
KERNEL_END = 6144
TABLE = 0xb5d2
SPANS = {
    'LIFT_REFS': (0xb2dd, bytes.fromhex('b95cb338ed1f078503b962b3ed1d07305cc9019058d05fa503c920b059')),
    'SEEN_REF': (0xb2d5, bytes.fromhex('3968b3')),
    'CONSTRUCT_REFS': (0xb314, bytes.fromhex('b95cb39576b962b3955d')),
    'PUBLISH_REF': (0xb32f, bytes.fromhex('1968b3')),
    'MARK_REF': (0xb34d, bytes.fromhex('1968b3')),
    'LIMIT': (0xb354, bytes.fromhex('c006')),
    'LIFT_TABLE': (TABLE, bytes.fromhex('207cb58d2ac8207cb58d2bc8a000208eb58d2cc8a0')),
}


def proposal(raw):
    old = raw[START:START+KERNEL_END]
    assert sha256(old).hexdigest() == Thomas.KERNEL
    tail, state = Cam.TH_KERNEL.read_bytes()[KERNEL_END:], Cam.TH_STATE.read_bytes()
    assert len(tail) == 2048 and len(state) == 8192
    assert raw[START+KERNEL_END:START+8192] == state[4096:6144]
    old_cookie = raw[COOKIE:COOKIE+16]
    assert old_cookie == bytes.fromhex('a70a4002')+sha256(old+tail+state).digest()[:12]
    # The table lies in the already retired 91-byte Thomas lab query helper,
    # after the 32-byte maturity/update reuse and before the live art anchor.
    # Confirm no installed direct branch table or JSR/JMP reaches this tail.
    retired = old[TABLE-0xa000:0xb60d-0xa000]
    assert retired == bytes.fromhex('207cb58d2ac8207cb58d2bc8a000208eb58d2cc8a00320a0b58d2dc868850a68850968850868850768850668850568850468850368a868aa682860')
    for i in range(len(old)-2):
        if old[i] in (0x20, 0x4c):
            assert not TABLE <= int.from_bytes(old[i+1:i+3], 'little') < 0xb60d
    names = ('ScreenLeft_X_Pos', 'ScreenLeft_PageLoc', 'R0', 'Enemy_X_Position', 'Enemy_PageLoc')
    symbols = W.Symbols.bundle()
    fields = {name: W.address(symbols, name) for name in names}
    fields.update(ThomasLiftMark=0xb34a, ThomasLiftNext=0xb353)
    declarations = ''.join(f'{name}=${value:04x}\n' for name, value in fields.items())
    linked = Asm.assemble(declarations+SOURCE.read_text(encoding='ascii'),
                          {name: (pc, len(body)) for name, (pc, body) in SPANS.items()})
    kernel, edits = bytearray(old), []
    for name, (pc, prior) in SPANS.items():
        off = pc-0xa000
        body = linked['images'][name]
        assert len(body) == len(prior) and old[off:off+len(prior)] == prior, name
        kernel[off:off+len(prior)] = body
        edits.append((START+off, prior, body))
    cookie = bytes.fromhex('a70a4003')+sha256(bytes(kernel)+tail+state).digest()[:12]
    result = bytearray(raw)
    result[START:START+KERNEL_END] = kernel
    result[COOKIE:COOKIE+16] = cookie
    edits.append((COOKIE, old_cookie, cookie))
    return bytes(result), dict(edits=edits, cookie=cookie, kernel=bytes(kernel),
                               source_SHA256=sha256(SOURCE.read_bytes()).hexdigest())


def manager(model):
    trial = Cclone(model)
    trial.raw_page(1, 3)
    trial.raw_page(2, 2)
    N.put(trial, CurrentBank=3, CurrentBankC=2, TimerControl=0, AreaAddrsLOffset=5,
          DisableScreenFlag=0, Mirror_PPUMASK=30, OperMode_Task=3, GameEngineSubroutine=8, ObjectOffset=4)
    for slot in range(6):
        Cam.slot_write(trial, 'Enemy_Flag', slot, 0)
    return trial


Cclone = Thomas.C.L.clone


def matrix(old, trial):
    before, after = manager(old), manager(trial)
    counts = Counter()
    for index, left in enumerate((*ORIGINAL, LEFT)):
        for relative, occupied in product((255, 256, 270, 287, 288, 320), (0, 5, 6)):
            sources = (before, after) if index < len(ORIGINAL) else (after,)
            results = []
            for seed in sources:
                model = Cclone(seed)
                model.ram[2][0x838] = (0x7f if seed is after else 0x3f) ^ (1 << index)
                Cam.fill_actors(model, occupied)
                Cam.geometry(model, left-relative, left-20)
                Cam.call(model, Cam.TH_TICK)
                expected = 256 <= relative <= 287 and occupied < 6
                assert Cam.lift_slots(model) == ({5: (left, 192, 0)} if expected else {})
                assert bool(model.ram[2][0x838] & (1 << index)) == (expected or relative < 256)
                assert N.get(model, 'ObjectOffset') == 4
                results.append((Cam.lift_slots(model), [Thomas.actor(model, i) for i in range(6)]))
                if index == len(ORIGINAL) and expected:
                    Cam.platform_carries(model, 5, LEFT)
                    counts['new_platform_carry'] += 1
            if len(results) == 2:
                assert results[0] == results[1], (index, relative, occupied)
                counts['existing_placements_match'] += 1
            else:
                counts['new_placement_boundaries'] += 1
    for world, level, area, timer in ((1, 0, 5, 0), (0, 1, 5, 0), (0, 0, 4, 0), (0, 0, 5, 255)):
        model = Cclone(after)
        Cam.geometry(model, LEFT-287, LEFT-20)
        N.put(model, WorldNumber=world, LevelNumber=level, AreaAddrsLOffset=area, TimerControl=timer)
        Cam.call(model, Cam.TH_TICK)
        assert not Cam.lift_slots(model) and model.ram[2][0x838] == 0
        counts['other_stage_or_frozen_reject'] += 1
    return dict(counts)


def foreign(old, trial):
    cases = Counter()
    service = W.address(trial.bundle, 'ThServiceVeneers')
    assert service == 0xb400
    target = 0x016c
    stop = (0x5b00, 224)
    for owner, alternates in ((0, 0), (10, 0), (10, 4), (13, 0), (22, 0), (24, 0), (34, 0)):
        outcomes = []
        for source in (old, trial):
            m = Cclone(source)
            N.put(m, SelectedCharacter=owner, FmAlts=alternates, NmiDisable=255)
            Cam.geometry(m, LEFT-287, LEFT-20)
            start = (bytes(m[0:0x100]), bytes(m[0x200:0x800]), tuple(bytes(r) for r in m.ram))
            m[target], m[target+1] = service & 255, service >> 8
            cpu = N.NesMPU(memory=m, pc=W.address(m.bundle, 'FarCallCommon'))
            cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = 213, 4, 91, 0x31, 224
            cpu.stPushWord(0x5aff)
            Thomas.C.L.finish(m, cpu, stop)
            assert not cpu.p & 1 and not any(a['x'] == LEFT for a in
                       (Thomas.actor(m, i) for i in range(6)) if a['flag'])
            assert tuple(bytes(r) for r in m.ram) == start[2]
            outcomes.append((cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp, bytes(m[0:0x100]),
                             bytes(m[0x200:0x800]), tuple(m.rawtags)))
        assert outcomes[0] == outcomes[1], (owner, alternates)
        cases['foreign_owner_or_Ryu_family_alternate_pairs'] += 1
    return dict(cases)


def vectors(trial):
    irq = Vectors.ISR
    irq.DEEPEST = None
    irq.PATHS.clear()
    reaches, cuts = set(), Counter()
    stop = (Cam.STOP, 232)

    def live(m, c):
        # The busy NMI may update the ordinary audio RAM and consume queues.
        # Compare the gameplay fields, live stack, mapper and both owner pages.
        return (irq.regs(c), bytes(m[3:11]), bytes(m[0x15a:0x17b]),
                bytes(m[0x101+c.sp:0x200]), bytes(m[0x0d:0xe2]), bytes(m[0xe6:0xff]),
                bytes(m[0x200:0x4a0]), bytes(m[0x566:0x571]),
                tuple(bytes(r) for r in m.ram), tuple(m.rawtags))

    def watch(m, c):
        pc = c.pc
        if m.rawtags[1] != 3 or pc in reaches or not any(pc0 <= pc < pc0+len(old)
                                                       for pc0, old in SPANS.values()):
            return
        reaches.add(pc)
        a, b = Vectors.clone(m, c)
        irq.finish(a, b, stop)
        for kind in ('NMI', 'IRQ'):
            q, d = Vectors.clone(m, c)
            initial = live(q, d)
            assert irq.isr(q, d, kind, stop) == 'returned'
            changed = [(i, [(j, x, y) for j, (x, y) in enumerate(zip(left, right)) if x != y][:12])
                       for i, (left, right) in enumerate(zip(initial, live(q, d))) if left != right and i != 8]
            assert live(q, d) == initial, (kind, hex(pc), changed)
            irq.finish(q, d, stop)
            assert live(q, d) == live(a, b), (kind, hex(pc), 'continuation')
            cuts[kind] += 1

    with patch.object(irq, 'regs', side_effect=lambda c: (c.pc, c.a, c.x, c.y, c.p & 0xef, c.sp)), \
            patch.object(irq, 'clone', side_effect=Vectors.clone):
        for rel, occupied in ((255, 0), (256, 0), (287, 5), (288, 0), (320, 6)):
            m = manager(trial)
            Cam.geometry(m, LEFT-rel, LEFT-20)
            Cam.fill_actors(m, occupied)
            N.put(m, NmiDisable=255)
            m.ram[2][0x838] = 0x3f
            cpu = Cam.cpu_at(m, Cam.TH_TICK, 232, 0x21, x=4)
            irq.finish(m, cpu, stop, watch)
        assert irq.DEEPEST is not None
        m, c, entry, resume = irq.DEEPEST
        q, d = Vectors.clone(m, c)
        a, b = Vectors.clone(m, c)
        initial = live(q, d)
        assert irq.isr(q, d, 'IRQ') == 'returned' and live(q, d) == initial
        for target in ((entry[0], entry[-1]), resume):
            irq.finish(q, d, target)
            irq.finish(a, b, target)
            assert live(q, d) == live(a, b)
    assert cuts['NMI'] == cuts['IRQ'] >= 16, [hex(pc) for pc in sorted(reaches)]
    return dict(cuts=dict(cuts), nested_IRQ=1, deepest_parent_SP=c.sp)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--route', action='store_true')
    args = parser.parse_args()
    raw = Thomas.C.ROM.read_bytes()
    image, info = proposal(raw)
    opening, old = Thomas.cold(raw)
    _, trial = Thomas.cold(image, expected=sha256(image).hexdigest(), kernel=info['kernel'], cookie=info['cookie'])
    print(json.dumps(dict(candidate_SHA256=sha256(image).hexdigest(), source_SHA256=info['source_SHA256'],
                          cookie=info['cookie'].hex(), opening=opening, matrix=matrix(old, trial),
                          foreign=foreign(old, trial), interrupts=vectors(trial), output_files=0)), flush=True)
    if args.route:
        result = Thomas.route(trial, 3600, flower_lift=True)
        print(json.dumps(result), flush=True)
        assert result['passed']


if __name__ == '__main__':
    main()
