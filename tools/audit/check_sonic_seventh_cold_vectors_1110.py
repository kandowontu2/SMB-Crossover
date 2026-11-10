"""Run real MMC5 vectors at the reached seventh cold owner's changed code.

No output tree or ROM is written. Forced-blank NMI and unmasked IRQ return
through their actual handlers, retaining PPU cursor, private RAM and ABI.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

import check_sonic_seventh_cold_owner_1110 as S
import check_getsu_owner_vectors_1110 as V

R, O, N = S.R, S.O, S.N


def clone(c):
    n = O.NesMPU(memory=S.slim_fork(c.memory), pc=c.pc)
    n.a, n.x, n.y, n.p, n.sp = c.a, c.x, c.y, c.p, c.sp
    return n


def qualify(trial, packet):
    spans = ((251, 0xaf40, 0xb000), (251, 0xb9d6, 0xba00),
             (193, 0xae00, 0xb013), (193, 0xabc9, 0xabd5),
             (219, 0xb1ba, 0xb1fc), (2, 0xd25e, 0xd25e + len(packet['startup']['image'])))
    counts, minimum, resumed = Counter(), 224, 0
    # Owner37 covers the compact multidescriptor worker,38 its compressed
    # constructor/finalizer,40 the moved copier,41 existing typed startup,
    # and43 the new seven-row startup and committed-header phases.
    for owner in (37, 38, 40, 41, 43):
        print('Actual cold vectors owner', owner, flush=True)
        m = O.blank(trial); O.scene(m, owner)
        c = V.entry(m)
        points, consumed = set(), set()
        for _ in range(4_000_000):
            if c.pc == V.STOP:
                break
            tag = m.rawtags[(c.pc - 0x8000) // 8192] if c.pc >= 0x8000 else m.rawtags[1]
            used = 0x15a <= c.pc < 0x17b or any(tag == bank and lo <= c.pc < hi for bank, lo, hi in spans)
            if used:
                phase = m.ram[2][0x1fe0], m.ram[3][0x1fe0]
                # Distinguish each seven-page startup row without exploding
                # a fixture into individual PPUDATA bytes. R2 is the actual
                # immutable-startup row counter, not a guessed game timer.
                row = m[5] if tag == 2 and c.pc >= 0xd25e else None
                key = tag, c.pc, c.sp, c.p & 4, phase, row
                if key not in points:
                    points.add(key); O.clear_logs(m)
                    for kind in ('FF', 'IRQ') if not c.p & 4 else ('FF',):
                        minimum = min(minimum, V.interrupt(clone(c), kind))
                        counts[owner, kind] += 1
                    # Also resume the original trace across each actual
                    # mapper/header/boot boundary, rather than only clones.
                    boundary = (tag, c.pc, phase, row)
                    if c.pc in (0xaf40, 0xb9d6, 0xae8c, 0xd25e) and boundary not in consumed:
                        consumed.add(boundary)
                        minimum = min(minimum, V.interrupt(c, 'FF'))
                        resumed += 1
            V.step(c)
        else:
            raise AssertionError(('Full cold bound', owner, hex(c.pc)))
        assert c.p & 1 and c.sp == 224 and len(points) > 100
        if owner == 43:
            S.sonic_owned(m, packet)
        assert counts[owner, 'FF'] and counts[owner, 'IRQ']
        print('Owner cuts', owner, {k: v for (o, k), v in counts.items() if o == owner}, flush=True)
    return dict(actual_cuts={f'{o}/{k}': v for (o, k), v in sorted(counts.items())},
                minimum_SP=minimum, full_cold_resumed_vectors=resumed,
                scope='One cut per mapped PC/SP/I/header-phase and each Sonic startup row. Actual forced-blank NMI and unmasked hardware IRQ; no native gameplay or ordinary-frame interrupt claim.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    assert args.output.resolve().is_relative_to(R / 'build') and not args.output.exists()
    image, _, packet, _, _, _ = S.proposal(S.C.ROM.read_bytes())
    trial = S.C.Current.W.bundle(image)
    result = qualify(trial, packet)
    assert not args.output.exists()
    print(json.dumps(dict(passed=True, source_only=True, outputs_written=0, ROM_written=False,
                          source_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),
                          in_memory_SHA256=sha256(image).hexdigest(), vectors=result), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
