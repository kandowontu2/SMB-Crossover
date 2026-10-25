"""Differential the actual shared native duration entry through its CPX rejoin."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from check_tmnt_render_oa import load, Memory, address
from verify_native_relocation import NesMPU

PATTERN = bytes((i*73+29)&255 if not 0x5114 <= i <= 0x5117 else 0
                for i in range(0x8000))


def execute(bundle, count, delta, channel, flags, owned=None):
    m = Memory(bundle); m.page(1, 123); m.page(2, 124)
    list.__setitem__(m, slice(0,0x8000), PATTERN)
    # Original RAM layout is relocated; entry A and incoming Z deliberately
    # vary independently because 8CFB calls this shared entry directly.
    ram = address(bundle, 'TnAudioRam'); zp = address(bundle, 'TnAudioZp')
    m[ram+0x10+channel] = delta; m[zp+2] = 0x93
    m.writes = []
    c = NesMPU(memory=m, pc=0xac75)
    c.a = count; c.x = channel; c.y = (count * 11 + delta) & 255
    c.p = flags; c.sp = 0xfd
    for _ in range(10000):
        if c.pc == 0xac8e: break
        c.step()
    else: raise AssertionError(('timeout', count, delta, channel, flags, hex(c.pc)))
    # Discarded call-stack bytes are not live state. A newly declared native
    # temporary, if present, is checked for ownership separately below.
    state = bytearray(m[:0x8000]); state[0x100:0x200] = bytes(256)
    if owned is not None: state[owned] = 0
    writes = [(at, value) for at, value in m.writes
              if not 0x100 <= at < 0x200 and at != owned]
    assert all(at in [zp+2, ram+4+channel, owned] or 0x100 <= at < 0x200
               for at, _ in m.writes), m.writes
    return ((c.a, c.x, c.y, c.p & 0xcf, c.sp), bytes(state),
            writes, m.banks, c.processorCycles)


def main():
    p = argparse.ArgumentParser(); p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    old, new = load(a.baseline), load(a.rom)
    owned = address(new, 'TnDurationY') if 'TnDurationY' in new['syms'] else None
    if owned is not None: assert owned == address(new, 'TnAudioRam')+0xb0
    rows = []; seen = set()
    cases = itertools.chain(
        itertools.product(range(256), [0,1,2,3,7,15,16,31,63,64,127,128,129,255], [0,5], [0x30,0x32,0x79,0x7f]),
        itertools.product([0,1,2,7,127,128,254,255], range(256), range(6), [0x30,0x76]))
    for count, delta, channel, flags in cases:
        key = (count, delta, channel, flags)
        if key in seen: continue
        seen.add(key)
        x = execute(old, *key, owned); y = execute(new, *key, owned)
        # Counter write ordering differs in a shortcut, but the complete RAM,
        # final registers/flags/SP and hardware/mapping state must be exact.
        assert x[:2] == y[:2] and x[3] == y[3], (key, x[0], y[0],
            [(hex(i), x[1][i], y[1][i]) for i in range(0x8000) if x[1][i] != y[1][i]][:12])
        rows.append(dict(count=count, delta=delta, channel=channel, flags=flags,
                         old_cycles=x[4], new_cycles=y[4]))
    proof = dict(passed=True, ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),
        baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(), cases=len(rows),
        cycles_saved=[min(r['old_cycles']-r['new_cycles'] for r in rows),
                      max(r['old_cycles']-r['new_cycles'] for r in rows)],
        owned_temporary=owned,
        scope='Actual AC75 shared entry to AC8E after original STA length/CPX2; all counts, all base deltas in edge-count matrix, all six channels, independent incoming Z including count0/Z0 256-loop case, overflow C/V, D/I flags. Exact A/X/Y/meaningfulP/SP and complete application RAM except discarded stack and explicitly declared native temporary. No hardware writes or bank changes permitted. No interrupt/native timing claim.')
    (a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof,indent=2))


if __name__ == '__main__': main()
