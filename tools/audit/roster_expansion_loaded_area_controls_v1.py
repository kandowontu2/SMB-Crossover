"""Bounded CPU checks for loaded-scene versus future-pipe accommodation identity.

TimerControl=1 skips native allocation deliberately. This is not a native
platform-visibility, movement, PPU, or full-route qualification.
"""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from check_tmnt_render_oa import location


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    old, new = map(scoped_load, [args.baseline, args.rom])
    rows = []
    for char, mode, destination in itertools.product([0, 1, 5, 20, 21, 27, 28], [0, 1], [0x25, 0xc2]):
        pair = []
        for bundle in [old, new]:
            q = Arena(bundle, char)
            q.put(CrossoverBehaviorVersion=mode, WorldNumber=0, LevelNumber=0,
                  AreaType=1, AreaAddrsLOffset=5, AreaPointer=0x25, TimerControl=1)
            q.invoke('HpConfigure')
            before = [q.get(n) for n in ['HpCount', 'HpArea', 'HpValid']]
            q.put(AreaPointer=destination)
            q.invoke('HpSpawnAndTrack')
            after = [q.get(n) for n in ['HpCount', 'HpArea', 'HpValid']]
            pair.append([before, after])
        if char == 1:
            assert pair[1] == [[1, 0x25, 1], [1, 0x25, 1]]
        if char in [20, 21]:
            assert pair[1][1] == [1, 0x25, 1]
        if char >= 27:
            assert pair[1][1] == [0, 0x25, 1]
        if char == 1 and destination == 0xc2:
            assert pair[0] == [[1, 0x25, 1], [0, 0xc2, 1]]
        rows.append(dict(character=char, mode=mode, AreaPointer=destination,
                         old=pair[0], new=pair[1]))
    tables = ['HpDataKey', 'HpDataArea', 'HpDataXLo', 'HpDataXHi', 'HpDataY',
              'HpDataWidth', 'HpDataAxis', 'HpDataEasyGate', 'HpDataHardGate']
    for name in tables:
        assert (old['raw'][location(old, name):location(old, name)+34] ==
                new['raw'][location(new, name):location(new, name)+34]), name
    proof = dict(passed=True, scope=__doc__, cases=rows,
                 baseline_sha256=sha(args.baseline), ROM_sha256=sha(args.rom),
                 tool_sha256=sha(__file__), records=34,
                 unchanged_source_placement_tables=tables)
    args.output.write_text(json.dumps(proof, indent=2)+'\n')
    print(json.dumps(dict(passed=True, cases=len(rows), sha256=sha(args.output))))


if __name__ == '__main__':
    main()
