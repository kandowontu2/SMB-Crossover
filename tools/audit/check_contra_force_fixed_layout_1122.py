"""Qualify the fixed-bank call space for a future Contra Force dispatcher.

The test image calls the existing mode tree and jumps over the reserved
space. It is built in memory and is never installed as a nightly.
"""

from collections import Counter
import json
from unittest.mock import patch

import compose_rogue_hud_scene_dirty_cb95_1116 as Hud
import current_contra_force_readonly_9826_1116 as Current


N, W, Frames = Current.N, Current.W, Current.Frames
MAIN = 0x82D9
PAUSE = 0x8356
GRAPHICS = 0x8369
END = 0x837B  # The following Mario fireball entry stays at this address.
NEW_PAUSE = 0x8359
NEW_GRAPHICS = 0x836B
SLOT = 0x8344
SLOT_LENGTH = 15
SAFE_A = 0x016A
INTERRUPT_SAFE_A = 0x7279
RNG = bytes.fromhex('ada007290285034da1074a4aa200a0077ea007e888d0f9')
OLD_FIXED_SHA = '7691d0dc57393348bcd6ade38bc74c9e4d35388a729a2fe8b2c3824d488f5b44'


def offset(bank, pc):
    return 16 + 8192 * bank + (pc & 8191)


def fixed_layout(parent):
    assert Hud.H(parent) == Hud.CANDIDATE
    begin, end = offset(126, MAIN), offset(126, END)
    code = parent[begin:end]
    assert Hud.H(code[:PAUSE - MAIN]) == OLD_FIXED_SHA
    assert code[PAUSE - MAIN:GRAPHICS - MAIN].hex() == '8d6a01a9008d6c01a9b48d6d01a9bf4c5a01ea'
    assert code[GRAPHICS - MAIN:].hex() == 'a9348d6c01a9bf8d6d01a9ca205a0160eaea'

    def original(first, last):
        return code[first - MAIN:last - MAIN]

    initial = bytearray(original(MAIN, 0x82F3))
    assert initial[5:8] == bytes.fromhex('205683')
    initial[6] = NEW_PAUSE & 255
    # Skip the old score call's incoming A store. The score leaf loads its
    # own accumulator before use. The paired replay below checks the lifetime.
    timers_and_score = bytearray(original(0x8313, 0x834D))
    branch = 0x8326 - 0x8313
    assert timers_and_score[branch:branch + 2] == bytes.fromhex('b028')
    timers_and_score[branch + 1] += SLOT_LENGTH - 3
    offset_in_proc = len(initial) + len(RNG) + len(timers_and_score)
    assert MAIN + offset_in_proc == SLOT
    after_slot = SLOT + SLOT_LENGTH
    # Equivalent call with padding skipped. A dispatcher can use all 15 bytes.
    slot = bytes((0x20, 0x98, 0x87, 0x4C, after_slot & 255, after_slot >> 8)) + bytes((0xEA,)) * 9
    tail = original(0x8350, 0x8352) + bytes((0x4C, NEW_PAUSE & 255, NEW_PAUSE >> 8, 0x60))
    assert after_slot + len(tail) == NEW_PAUSE
    pause = original(PAUSE, GRAPHICS - 1)
    assert NEW_PAUSE + len(pause) == NEW_GRAPHICS
    graphics = original(GRAPHICS, END - 2)
    new_code = b''.join((initial, RNG, timers_and_score, slot, tail, pause, graphics))
    assert begin + len(new_code) == end
    pointer = offset(4, 0xA000)
    assert parent[pointer:pointer + 3] == bytes.fromhex('206983')
    image = bytearray(parent)
    image[begin:end] = new_code
    image[pointer + 1] = NEW_GRAPHICS & 255
    return bytes(image)


def backing(m, raw):
    m.bundle = dict(m.bundle, raw=raw)
    for slot, tag in enumerate(m.rawtags):
        if tag & 128:
            m.raw_page(slot, tag)
    return m


def compare(old, new, allow_backup=False):
    # $0100..$017A contains live variables and the self-modifying farcall
    # helper. The top two live caller bytes also remain comparable.
    native = [*range(0x17B), *range(0x1FE, 0x800), *range(0x5C00, 0x8000)]
    differences = {a: [old[a], new[a]] for a in native if old[a] != new[a]}
    assert differences.keys() <= ({INTERRUPT_SAFE_A} if allow_backup else set()), differences
    assert tuple(map(bytes, old.ram)) == tuple(map(bytes, new.ram))
    assert old.rawtags == new.rawtags and old.chr_latches == new.chr_latches
    assert old.vram == new.vram and old.ppuctrl == new.ppuctrl
    return differences


def cold(parent):
    symbols = Current.bindings(Hud.inverse(parent))
    actual = dict(symbols, bundle=dict(symbols['bundle'], raw=parent))
    with patch.object(Current.P, 'bindings', lambda raw: actual):
        return Current.P.cold(parent)


def warm_pairs(seed, parent, candidate):
    a, b = (backing(N.fork(seed), raw) for raw in (parent, candidate))
    compared = Counter()
    for name, pad, count in (('idle', 0, 8), ('walk', 1, 8), ('pause', 16, 1), ('paused', 0, 4)):
        for _ in range(count):
            for m in (a, b):
                m.controller_pad = pad
                Frames.frame(m, whole_pass=True)
            compare(a, b)
            compared[name] += 1
    return dict(compared)


def interrupt_pairs(seed, parent, candidate):
    base = N.NesMPU
    # The first two sites bracket the removed STA; the third is the game call.
    cuts = ((0x8310, 0x830A), (0x831F, 0x8316), (0x834D, SLOT))
    results = []
    for locations in cuts:
        for kind in ('IRQ', 'NMI'):
            rows, models, returns = [], [], []
            for raw, at in zip((parent, candidate), locations, strict=True):
                model = backing(N.fork(seed), raw)
                # Make the removed store observable. The warm fixture's
                # zero seed otherwise gives the same accumulator on both
                # paths. These are only the two RNG feedback inputs.
                model[0x7A0], model[0x7A1] = 0x20, 0xB6
                class CPU(base):
                    def step(self):
                        if self.pc == at and not rows:
                            before = (self.pc, self.sp, self.a, self.x, self.y, self.p | 48)
                            latch = self.memory[SAFE_A]
                            assert self.memory[0x139] & 128, 'Real foreground is busy'
                            self.nmi() if kind == 'NMI' else self.irq()
                            delivered = self.pc != before[0]
                            low = self.sp
                            for _ in range(10000):
                                if (self.pc, self.sp) == before[:2]:
                                    break
                                assert self.memory[self.pc], (kind, hex(self.pc), 'BRK')
                                base.step(self)
                                low = min(low, self.sp)
                            else:
                                raise AssertionError('Interrupt failed to return')
                            assert (self.pc, self.sp, self.a, self.x, self.y, self.p | 48) == before
                            assert self.memory[SAFE_A] == latch
                            rows.append(dict(pc=at, kind=kind, delivered=delivered,
                                             A=self.a, safe_a=latch, saved_a=self.memory[INTERRUPT_SAFE_A], min_sp=low))
                        return base.step(self)
                with patch.object(N, 'NesMPU', CPU):
                    ret = N.invoke(model, 'GameLoop', a=0, x=0, y=0, p=0x31)
                assert len(rows) == 1, (kind, hex(at))
                results.append(rows.pop())
                models.append(model)
                returns.append({k: v for k, v in ret.items() if k != 'CPU'})
            assert returns[0] == returns[1]
            differences = compare(*models, allow_backup=kind == 'NMI')
            if differences:
                assert differences[INTERRUPT_SAFE_A] == [r['saved_a'] for r in results[-2:]]
            if locations[0] == 0x8310:
                assert [r['A'] for r in results[-2:]] == [2, 0xB6 >> 2]
            elif locations[0] == 0x831F:
                assert [r['safe_a'] for r in results[-2:]] == [2, 0]
    return results


def main():
    parent = Hud.ROM.read_bytes()
    candidate = fixed_layout(parent)
    seed = cold(parent)
    for _ in range(4):
        seed.controller_pad = 0
        Frames.frame(seed, whole_pass=True)
    print('WARM ' + json.dumps(warm_pairs(seed, parent, candidate)), flush=True)
    interrupts = interrupt_pairs(seed, parent, candidate)
    print('RESULT ' + json.dumps(dict(parent=Hud.H(parent), fixed_layout_test_image=Hud.H(candidate),
        slot=hex(SLOT), bytes=SLOT_LENGTH, pause=hex(NEW_PAUSE), graphics=hex(NEW_GRAPHICS),
        interrupts=interrupts, interrupt_fixture_rng_input=[0x20, 0xB6], installed=False, generated_files=0)), flush=True)


if __name__ == '__main__':
    main()
