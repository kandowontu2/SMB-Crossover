"""Exercise the native item handler and authenticated Metal maturity policy."""
import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_metal_head_bridge_1112 as Head
import compose_metal_pickup_maturity_1112 as Compose

Flower, M = Head.Flower, Head.M


def actor(seed, slot, kind, state, *, overlap=True, status=0):
    model = Flower.pickup(seed, slot, kind, mature=state, native_status=status)
    M.put(model, Player_X_Position=80, Player_PageLoc=0, Player_Y_Position=176,
          Player_Y_HighPos=1, Player_Rel_XPos=80, Player_Rel_YPos=176,
          ScreenLeft_X_Pos=0, ScreenLeft_PageLoc=0, ScreenRight_X_Pos=255,
          ScreenRight_PageLoc=0, TimerControl=1, FrameCounter=1, Player_OffscreenBits=0)
    for name, value in dict(Enemy_X_Position=80 if overlap else 160,
                            Enemy_Y_Position=184, Enemy_BoundBoxCtrl=9,
                            Enemy_MovingDir=1).items():
        model[M.address(model.bundle, name) + slot] = value
    M.invoke(model, 'LmBoundingBoxGate', x=0, y=0)
    return model


def point(model, name):
    pc = M.address(model.bundle, name)
    return pc, ((M.location(model.bundle, name) - 16) // 8192) | 128


def lifecycle(parent, candidate):
    native = M.NesMPU
    counts = Counter()
    seen = Counter()
    points = {point(candidate, name): name for name in ('NrPickupCollision', 'HuMature',
        'PlayerEnemyCollision', 'PlayerCollisionCore', 'HandlePowerUpCollision', 'NrPickup', 'HuPickup')}
    points[(0xbfba, 3)] = 'MsMetalMaturity'

    class Trace(native):
        def step(self):
            if self.pc >= 0x8000:
                name = points.get((self.pc, self.memory.rawtags[(self.pc - 0x8000) // 8192]))
                if name: seen[name] += 1
            return native.step(self)

    M.NesMPU = Trace
    try:
        for slot, kind, state, overlap in product(range(6), range(4), (6, 16, 128, 129), (False, True)):
            model = actor(candidate, slot, kind, state, overlap=overlap, status=int(kind == 1))
            seen.clear()
            result = M.invoke(model, 'PowerUpObjHandler', x=slot, p=0x21)
            accepted = state >= 128 and overlap
            assert seen['NrPickupCollision'] == seen['HuMature'] == seen['MsMetalMaturity'] == 1, (slot, kind, state, seen)
            assert seen['PlayerEnemyCollision'] == int(state >= 128), (slot, kind, state, seen)
            box = M.address(model.bundle, 'BoundingBox_UL_Corner')
            assert seen['HandlePowerUpCollision'] == int(accepted), (slot, kind, state, overlap, seen, result,
                list(model[box:box + 4]), list(model[box + 4 * (slot + 1):box + 4 * (slot + 2)]))
            assert M.get(model, 'Enemy_Flag', slot) == int(not accepted), (slot, kind, state, overlap, seen)
            if kind < 2 and accepted:
                assert M.get(model, 'PlayerStatus') == kind + 1 and seen['HuPickup'] == 1
                assert model.ram[2][0x5d0 if kind == 0 else 0x718] == 0x80
                counts['actual_native_mushroom' if kind == 0 else 'actual_native_flower'] += 1
            elif kind < 2:
                assert M.get(model, 'PlayerStatus') == int(kind == 1)
                assert not model.ram[2][0x5d0 if kind == 0 else 0x718]
            counts['mature_overlap' if accepted else 'preserved_uncollectable_actor'] += 1
        original = actor(parent, 5, 0, 128)
        seen.clear()
        M.invoke(original, 'PowerUpObjHandler', x=5, p=0x21)
        assert seen['HuMature'] == 1 and not seen['PlayerEnemyCollision'] and not seen['HandlePowerUpCollision']
        assert M.get(original, 'Enemy_Flag', 5) == 1
    finally:
        M.NesMPU = native
    return dict(counts, real_parent_rejection=True)


def maturity_abi(parent, candidate):
    counts = Counter()
    for slot, state in product(range(6), range(256)):
        original, model = M.fork(parent), M.fork(candidate)
        at = M.address(model.bundle, 'Enemy_State') + slot
        original[at] = model[at] = state
        before = tuple(map(bytes, model.ram))
        p = (0x20, 0x61, 0xa4, 0x21)[state & 3]
        expected = M.invoke(original, 'HuMature', a=85, x=slot, y=91, p=p)
        result = M.invoke(model, 'HuMature', a=85, x=slot, y=91, p=p)
        assert (result['A'], result['X'], result['Y'], result['P']) == (
            85, slot, 91, expected['P'] & 0xfe | state >> 7), (slot, state, p, expected, result)
        assert tuple(map(bytes, model.ram)) == before
        counts['maturity_state_slot_AXYP_and_RAM'] += 1
    for byte in range(32):
        model = actor(candidate, 5, 0, 128)
        model.ram[2 + byte // 16][0x1fe0 + byte % 16] ^= 1
        before = tuple(map(bytes, model.ram))
        result = M.invoke(model, 'NrPickupCollision', x=5)
        assert not result['P'] & 1 and tuple(map(bytes, model.ram)) == before
        counts['header_byte_rejections'] += 1
    for owner, state in product((0, 1, 31, 32, 34, 36, 37, 38, 39, 40, 42), (0, 16, 128, 255)):
        old, new = M.fork(parent), M.fork(candidate)
        for model in (old, new):
            M.put(model, SelectedCharacter=owner)
            model[M.address(model.bundle, 'Enemy_State') + 5] = state
        a = M.invoke(old, 'NrPickupCollision', x=5)
        b = M.invoke(new, 'NrPickupCollision', x=5)
        assert all(a[key] == b[key] for key in ('A', 'X', 'Y', 'P'))
        counts['foreign_owner_pairs'] += 1
    return dict(counts)


def bridge_controls(parent, candidate):
    """Compare reachable services that use the compacted actor return."""
    counts = Counter()
    pure = ('HuGraphics', 'HuPortrait', 'HuWeapons', 'HuStatus', 'HuVisible',
            'HuBody', 'HuAdder', 'HuBox', 'HuFullBox', 'HuLivesPortrait',
            'HuMenuName', 'HuPrepare', 'HuRise', 'HuPrivate', 'HuFullPower',
            'HuColors', 'HuBounceOnly', 'HuHeadWithinOnly', 'HuUi',
            'HuStatusName', 'HuBounce', 'HuWorldColors', 'HuPowerup', 'HuVine')
    for name, p in product(pure, (0x20, 0x21, 0x64, 0xa1)):
        if name not in candidate.bundle['syms']:
            continue
        old, new = M.fork(parent), M.fork(candidate)
        a, b = (M.invoke(model, name, a=0, x=0, y=0, p=p) for model in (old, new))
        assert all(a[key] == b[key] for key in ('A', 'X', 'Y', 'P')), (name, p, a, b)
        assert bytes(old[:0x100]) == bytes(new[:0x100]), (name, p)
        assert bytes(old[0x200:0x800]) == bytes(new[0x200:0x800]), (name, p)
        for bank, spans in ((2, ((0, 0x144a), (0x144d, 0x1fe0))),
                            (3, ((0, 0x1fb2), (0x1fc0, 0x1fe0)))):
            assert all(old.ram[bank][lo:hi] == new.ram[bank][lo:hi] for lo, hi in spans), (name, p, bank)
        assert old.rawtags == new.rawtags and old.chr_latches == new.chr_latches, (name, p)
        counts['other_public_services_exact'] += 1
    return dict(counts)


def interrupts(candidate):
    native = M.NesMPU
    counts, points = Counter(), set()
    minimum = 255
    class Trace(native):
        def step(self):
            nonlocal minimum
            if 0xbfb2 <= self.pc <= 0xbfbd and self.memory.rawtags[1] == 3:
                point = (self.pc, self.sp, self.p & 4)
                if point not in points:
                    points.add(point)
                    for kind in ('IRQ', 'lagNMI'):
                        if kind == 'IRQ' and self.p & 4:
                            continue
                        clone = M.fork(self.memory)
                        cpu = native(memory=clone, pc=self.pc)
                        for field in ('a', 'x', 'y', 'p', 'sp'):
                            setattr(cpu, field, getattr(self, field))
                        minimum = min(minimum, Head.inject(cpu, native, kind))
                        counts[kind] += 1
            return native.step(self)
    M.NesMPU = Trace
    try:
        for kind, state in product((0, 1), (16, 128)):
            M.invoke(actor(candidate, 5, kind, state, status=int(kind == 1)),
                     'PowerUpObjHandler', x=5, p=0x21)
    finally:
        M.NesMPU = native
    assert counts['IRQ'] and counts['lagNMI'] and minimum >= 128
    return dict(cuts=dict(counts), instruction_SP_points=len(points), minimum_SP=minimum)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, default=Flower.NIGHTLY)
    parser.add_argument('--basic', action='store_true')
    parser.add_argument('--faults-only', action='store_true')
    parser.add_argument('--bridge-only', action='store_true')
    args = parser.parse_args()
    head, head_layout = Compose.Head.compose(args.rom.read_bytes())
    raw, layout = Compose.transform(head)
    assert Compose.transform(raw, True)[0] == head
    if args.faults_only:
        _, cold = Head.cold(raw, bytes.fromhex(layout['cookie']), cuts=True)
        faults = Head.readback_faults(raw, layout, ((2, 0xd44b, 0xba), (3, 0xbfba, 0xb5)))
        print('METAL_MATURITY_READBACK ' + json.dumps(dict(layout=layout, cold=cold, faults=faults),
              separators=(',', ':')), flush=True)
        return
    parent, _ = Head.cold(head, bytes.fromhex(head_layout['cookie']))
    candidate, cold = Head.cold(raw, bytes.fromhex(layout['cookie']))
    if args.bridge_only:
        print('METAL_MATURITY_BRIDGE ' + json.dumps(bridge_controls(parent, candidate), separators=(',', ':')), flush=True)
        return
    print('METAL_MATURITY_NATIVE ' + json.dumps(dict(layout=layout, cold=cold,
          lifecycle=lifecycle(parent, candidate)), separators=(',', ':')), flush=True)
    if not args.basic:
        print('METAL_MATURITY_ABI ' + json.dumps(maturity_abi(parent, candidate), separators=(',', ':')), flush=True)
        print('METAL_MATURITY_BRIDGE ' + json.dumps(bridge_controls(parent, candidate), separators=(',', ':')), flush=True)
        print('METAL_MATURITY_INTERRUPTS ' + json.dumps(interrupts(candidate), separators=(',', ':')), flush=True)
        print('METAL_MATURITY_UPGRADED_SHOTS ' + json.dumps(Flower.source_shots(candidate), separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()
