"""Qualify two fixed sweep clocks and their short-period target arithmetic."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_guest_expansion_negate4_1110 as Prior
from check_mini_audio_mixer_irq_1108_v2 import lag_path, sound_writes
from check_mini_funded_actor_1108_v3 import install, registers, run
from check_native_audio_dirty_clear_irq_1110 import resume_matches
from check_native_ground_token_index_1110 import exact_state


M, N, R, Sweep, V = Prior.M, Prior.N, Prior.R, Prior.Sweep, Prior.V
BASE = R / 'build/mini-shared-game-loop-tail-native-1110/candidate.nes'
PIN = '29aa4f8df07425dfe6dcdaaa431421c78347adbca5979c332edce69c79367cf5'
PROFILE = R / 'build/mini-29aa-nmi1505-1110/capture/timing.json'
ENTRY, END = Sweep.FLUSH, Sweep.CLOCK


class TimedMPU(N.NesMPU):
    # The bundled py65 table lists DEC abs as three cycles. The read-modify-
    # write takes six on the NES CPU, including the two writes to the bus.
    cycletime = list(N.NesMPU.cycletime)
    cycletime[0xCE] = 6


def linked(raw):
    image = M.bundle(raw)
    assert '''  lda #2
  sta GuestSweepTicks
Clock:
  jsr GuestExpansionSweepClock
  dec GuestSweepTicks
  bne Clock
''' in Sweep.SOURCE.read_text()
    assert 'sbc Delta                ; P - floor(P/16) - 1 is nonnegative.' in Prior.SOURCE.read_text()
    assert M.address(image, 'GuestSweepTicks') == 0x72FE
    assert M.address(image, 'GuestExpansionSweepClock') == END
    assert M.location(image, 'GuestExpansionFlush') == Prior.off(ENTRY)
    rows = (
        # JSR Clock twice, then publish the old exhausted count.
        (0xAB1C, 0xAB29, 'a9028dfe722028accefe72d0f8', '2028ac2028aca9008dfe72eaea'),
        # A = P>>4. Invert it and add P with C clear to match SBC with C clear.
        (0xAC12, 0xAC28, 'adf7724a4a4a4a8df972adf77218edf9728df972b860',
         'adf7724a4a4a4a49ff186df7728df972b860eaeaeaea'),
    )
    patches = []
    for lo, hi, old, new in rows:
        at = Prior.off(lo)
        assert len(bytes.fromhex(old)) == len(bytes.fromhex(new)) == hi - lo
        assert raw[at:at + hi - lo].hex() == old
        patches.append(dict(physical_PRG=29, CPU_half_open=[lo, hi], file_offset=at,
                            old_hex=old, new_hex=new))
    return install(raw, patches), patches


def mixer(before, after):
    images = [M.bundle(raw) for raw in (before, after)]
    machines = [Sweep.Mixer(image) for image in images]
    address = lambda name: M.address(images[0], name)
    savings = Counter()
    for control, divider, period, mask, dirty in product(range(256), (0, 1, 7),
                                                          (0, 7, 8, 15, 128, 255, 256, 2047, 65535),
                                                          (0, 1, 2, 3), (0, 7)):
        pair = []
        for m in machines:
            m.hw.clear()
            for name in ('GuestExpansionApu', 'GuestExpansionLast', 'GuestFxApu', 'GuestFxDirty'):
                at = address(name)
                m.mem[at:at + 8] = bytes((control + 17 * i) & 255 for i in range(8)) if name != 'GuestFxDirty' else bytes(8)
            at = address('GuestFxDirty')
            m.mem[at + 1:at + 4] = bytes((dirty & 1, dirty & 2, dirty & 4))
            m.mem[address('GuestMixMask')] = mask
            m.mem[address('GuestMixChanged')] = control & 3
            m.mem[Sweep.FIRST:Sweep.LAST] = bytes((period & 255, period >> 8, 0xa1, 0x65, control, divider, 0, 0xfd))
            cpu = TimedMPU(memory=m, pc=ENTRY)
            cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = 123, 21, 71, 0x21, 224
            cpu.stPushWord(0x5aff)
            hits = Counter()
            run(cpu, lambda z: z.pc == 0x5b00, lambda z: hits.update((z.pc,)))
            pair.append((registers(cpu), bytes(m.mem[m.lo:Sweep.LAST]), tuple(m.hw), hits[0xAC12], cpu.processorCycles))
        old, new = pair
        assert old[:-1] == new[:-1], (control, divider, period, mask, dirty)
        saved = old[-1] - new[-1]
        assert saved == 13 * (mask & 1) + 6 * new[-2], (control, divider, period, mask, dirty, saved, new[-2])
        savings[saved] += 1
    return dict(cases=sum(savings.values()), cycles_saved=dict(savings))


class Guard(V.Guard):
    def __getitem__(self, address):
        if self.irq_only and isinstance(address, int):
            assert not 0x72E7 <= address < 0x72FF, ('IRQ reads private mixer scratch', hex(address))
        return super().__getitem__(address)

    def __setitem__(self, address, value):
        if self.irq_only and isinstance(address, int):
            assert not 0x72E7 <= address < 0x72FF, ('IRQ writes private mixer scratch', hex(address))
        super().__setitem__(address, value)


def vectors(before, after):
    images = [M.bundle(raw) for raw in (before, after)]
    original = N.Bus
    N.Bus = Guard
    results, nested = [], Counter()
    try:
        for owner, flag, pulse in product((0, 2, 7, 25, 41), (0, 255), (0, 32)):
            pair, cuts = [], {}
            for side, image in enumerate(images):
                m = M.seed(image, owner)
                N.put(m, NmiDisable=flag, AreaMusicQueue=1, Square1SoundQueue=pulse, Square2SoundQueue=1,
                      NoiseSoundQueue=1, VRAM_Buffer_AddrCtrl=0, VRAM_Buffer1_Offset=0)
                lag, normal = lag_path(m)
                cpu = V.start(m)
                hits = Counter()

                def watch(z):
                    pc = z.pc
                    if pc in (lag, normal):
                        hits[pc] += 1
                    if m.rawtags[1] != 157:
                        return
                    if pc == ENTRY:
                        hits['flush'] += 1
                    key = side, pc, z.sp
                    if ENTRY <= pc < END and not z.p & 4 and key not in cuts:
                        cuts[key] = V.clone(z), tuple(m.writes)

                run(cpu, lambda z: (z.pc, z.sp) == (0x5B00, 214), watch)
                assert hits[lag] == int(flag == 255) and hits[normal] == int(flag == 0)
                pair.append((cpu, hits['flush']))
            (a, old), (b, new) = pair
            assert old == new
            V.same_end(a, b)
            exact_state(a.memory, b.memory)
            assert sound_writes(a.memory) == sound_writes(b.memory)
            for (side, _, _), (cut, prior) in cuts.items():
                V.interrupt(cut)
                resume_matches(cut, prior, pair[side][0])
                nested[flag] += 1
            saved = a.processorCycles - b.processorCycles
            assert saved >= 0 and (new or saved == 0)
            results.append(dict(owner=owner, NmiDisable=flag, pulse=pulse, calls=new, cycles_saved=saved))
    finally:
        N.Bus = original
    assert min(nested.values()) > 0
    return dict(cases=results, nested_IRQ=dict(nested))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R / 'build') and out != R / 'build'
    out.mkdir(exist_ok=True)
    dest = out / 'proof.json'
    assert not dest.exists()
    before = BASE.read_bytes()
    assert M.sha(before) == PIN
    trace = json.loads(PROFILE.read_text())
    assert trace['ROM_sha256'] == PIN and trace['nmi_sample']['frame'] == 1505
    after, patches = linked(before)
    foreground = mixer(before, after)
    print(f'Exact register/image/ordered output matches in {foreground["cases"]} mixer cases.', flush=True)
    owners = Prior.lifecycle(before, after)
    interrupts = vectors(before, after)
    refs = (Path(__file__), BASE, PROFILE, PROFILE.with_name('binding.json'), Sweep.SOURCE, Prior.SOURCE,
            Path(Prior.__file__), Path(Sweep.__file__), Path(V.__file__))
    proof = dict(passed=True, ROM_written=False, parent_SHA256=PIN, expected_memory_only_SHA256=M.sha(after),
                 patches=patches, foreground=foreground, lifecycle=owners, vectors=interrupts,
                 bindings={str(p.resolve()): M.sha(p.read_bytes()) for p in refs})
    dest.write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')
    print(f'Passed native mixer checks. Direct savings {foreground["cycles_saved"]}.', flush=True)


if __name__ == '__main__':
    main()
