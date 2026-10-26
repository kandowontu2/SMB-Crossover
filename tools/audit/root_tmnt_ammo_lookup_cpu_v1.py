"""Compare complete assembled turtle ammo HUD calls, including queue guards."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json

from check_tmnt_render_oa import load, Memory, address
from verify_native_relocation import NesMPU
from tmnt_native_storage_driver import ROOT, sha


def execute(bundle, cfg):
    m = Memory(bundle)
    for i in range(8):
        m[address(bundle, 'R' + str(i))] = (73 * i + 29) & 255
    start = address(bundle, 'VRAM_Buffer1')
    for i in range(84):
        m[start + i] = (73 * i + 29) & 255
    seed = {'TnGearSelected': cfg.get('gear', 1), 'TnVariant': cfg.get('variant', 0),
            'TnHudSelected': cfg.get('hud_selected', 1), 'TnHudAmmo': cfg.get('cached', 255),
            'VRAM_Buffer1_Offset': cfg.get('queue', 0)}
    for name, value in seed.items():
        m[address(bundle, name)] = value
    for i in range(4):
        m[address(bundle, 'TnEquipment') + i] = cfg.get('equipment', 2)
        m[address(bundle, 'TnAmmo') + i] = cfg.get('ammo', 99)
    m[510], m[511] = 255, 126
    c = NesMPU(memory=m)
    c.pc, c.a, c.x, c.y, c.p, c.sp = address(bundle, 'TnAmmoHud'), 85, 3, cfg.get('Y', 7), cfg.get('flags', 0x60), 253
    m.writes = []
    for _ in range(5000):
        if c.pc == 0x7f00:
            break
        c.step()
    else:
        raise AssertionError(('Timeout', cfg, hex(c.pc)))
    # Only the discarded upper stack changes; every ordinary RAM byte, five
    # SMC sites, bank state and ordered VRAM/OAM/hardware writes are retained.
    state = (c.a, c.x, c.y, c.p & 207, c.sp,
             bytes(m[:0x1a0]) + bytes(m[0x200:0x8000]), tuple(m.banks))
    writes = [(at, value) for at, value in m.writes
              if start <= at < start + 0x100 or 0x2000 <= at < 0x5c00]
    return state, writes, c.processorCycles


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['baseline', 'candidate', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    old, new = load(a.baseline), load(a.candidate)
    rows = []
    def check(tag, cfg):
        before, after = execute(old, cfg), execute(new, cfg)
        assert before[:2] == after[:2], (tag, cfg, before[0][:5], after[0][:5], before[1], after[1])
        rows.append({'tag': tag, 'cfg': cfg, 'baseline_cycles': before[2],
                     'candidate_cycles': after[2], 'delta': after[2] - before[2]})
    flags = [0x20 | (n & 15) | ((n & 16) << 2) | ((n & 32) << 2) for n in range(64)]
    assert len(set(flags)) == 64
    for ammo, variant, queue, y in itertools.product(range(256), range(4), [0, 77, 78, 255], [0, 255]):
        check('all-byte-ammo', dict(ammo=ammo, variant=variant, queue=queue, Y=y,
              cached=ammo ^ 255, flags=flags[(ammo + variant + queue + y) % 64]))
    for ammo, flag, variant, queue in itertools.product([0, 9, 10, 99, 100, 199, 200, 255], flags, range(4), [0, 77]):
        check('all-caller-flags', dict(ammo=ammo, flags=flag, variant=variant, queue=queue, cached=ammo ^ 255))
    for y in range(256):
        check('all-caller-Y', dict(Y=y, ammo=y, cached=y ^ 255, flags=flags[y % 64]))
    for gear, equipment, queue, cache_match in itertools.product([0, 1], range(5), range(256), [False, True]):
        selected = int(bool(gear and equipment))
        ammo = 99 if selected else 0
        check('queue-and-clean-controls', dict(gear=gear, equipment=equipment, ammo=99, queue=queue,
              cached=ammo if cache_match else ammo ^ 255, hud_selected=selected,
              flags=flags[(gear + equipment + queue) % 64]))
    groups = {}
    for tag in sorted({row['tag'] for row in rows}):
        ds = [row['delta'] for row in rows if row['tag'] == tag]
        groups[tag] = {'cases': len(ds), 'min_delta': min(ds), 'max_delta': max(ds), 'total_delta': sum(ds)}
    representatives = []
    for ammo in [0, 9, 10, 19, 20, 50, 90, 98, 99, 100, 199, 200, 255]:
        before, after = execute(old, {'ammo': ammo, 'cached': ammo ^ 255}), execute(new, {'ammo': ammo, 'cached': ammo ^ 255})
        representatives.append({'ammo': ammo, 'baseline_cycles': before[2], 'candidate_cycles': after[2], 'delta': after[2] - before[2]})
    (a.output / 'cases.json').write_text(json.dumps(rows, separators=(',', ':')) + '\n')
    proof = dict(passed=True, source_only=True, native_run=False, accepted=False,
                 baseline_ROM_sha256=sha(a.baseline), candidate_ROM_sha256=sha(a.candidate),
                 cases=len(rows), grouped=groups, representatives=representatives,
                 exact_complete_final_AXYP_SP_RAM_SMC_banks_ordered_VRAM_hardware=True,
                 omitted_memory='Only discarded upper CPU stack01A0..01FF',
                 checker_sha256=sha(Path(__file__)),
                 limitations='Arranged component CPU calls. Includes all256 ammo values/queue offsets/Y and all64 physical caller flags, with full final-call state. No native draw-deadline, interrupt, global cadence or deployment claim.')
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof), flush=True)


if __name__ == '__main__':
    main()
