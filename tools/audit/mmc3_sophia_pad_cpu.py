"""Check the compact same-bank capacity helper and untouched friction code."""
from pathlib import Path
import argparse
import hashlib
import json
from check_tmnt_render_oa import Memory, address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load as load
from verify_native_relocation import NesMPU

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    args.output.mkdir(exist_ok=False)
    b, old = load(args.rom), load(args.baseline)
    start = location(b, 'SophiaTripletAdmission')
    assert (start-16)//8192 == 6
    assert address(b, 'AvHomeFriction') == address(old, 'AvHomeFriction')
    first, previous = location(b, 'AvHomeFriction'), location(old, 'AvHomeFriction')
    before, after = old['raw'][previous:previous+90], b['raw'][first:first+90]
    span = start-first
    assert span == 34 and after[:span] == before[:span] and after[span+24:] == before[span+24:]
    assert before[span:span+24] == bytes([234])*24
    rows = []
    for mask in range(1024):
        for occupied_missile in [False, True]:
            m = Memory(b)
            m.page(1, 6)
            m[address(b, 'AvType')] = 44
            actual_missile = False
            for i in range(10):
                typ = 6 if mask & (1 << i) else 0
                if occupied_missile and typ and not actual_missile:
                    typ, actual_missile = 44, True
                m[address(b, 'RgShotType')+i] = typ
            m.writes = []
            c = NesMPU(memory=m, pc=address(b, 'SophiaTripletAdmission'))
            c.sp = 0xfd
            c.stPushWord(0x5aff)
            for _ in range(400):
                if c.pc == 0x5b00:
                    break
                assert 0xa000 <= c.pc < 0xc000
                c.step()
            else:
                raise AssertionError(('same-bank helper timeout', mask))
            assert c.sp == 0xfd
            free = 10-mask.bit_count()
            allowed = free >= 3 and not actual_missile
            assert (m[address(b, 'AvCount')] == 0) == allowed
            # This function needs no mapper: the real code and table remain in A6.
            assert not any(0x4000 <= a < 0x6000 for a, _ in m.writes)
            assert all(a < 0x200 or a == address(b, 'AvCount') for a, _ in m.writes)
            rows.append(dict(mask=mask, missile=actual_missile, admitted=allowed))
    q = dict(passed=True, adopted=False, goal_complete=False, ROM_sha256=sha(args.rom),
             baseline_ROM_sha256=sha(args.baseline), helper_cases=len(rows),
             old_friction_prefix_suffix_exact=True, replaced_unreachable_NOPS=24,
             all_helper_fetches_same_bank=True, no_mapper_IO=True,
             scope='Actual linked helper CPU admission across every occupancy mask with and without a carried missile. Explicit same-bank CPU model, no native mapper/interrupt/volley/PPU or complete oversized-ROM qualification.')
    (args.output / 'proof.json').write_text(json.dumps(q, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(q, indent=2))


if __name__ == '__main__':
    main()
