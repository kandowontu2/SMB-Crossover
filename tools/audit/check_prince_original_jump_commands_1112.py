"""Read-only donor CPU animation comparison; no gameplay or ROM mutations."""
import json
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R/'tools/reference'))
import prince_original_cpu_1101_v1 as P


def main():
    seed = (R/'build/prince-actor-1101-v1/state-899.bin').read_bytes()
    assert len(seed) == 2048
    results = []
    for action in (3, 4, 14):
        c = P.machine()
        c.memory.switch(5)
        list.__setitem__(c.memory, slice(0, 2048), seed)
        c.memory[0x69] = 0
        c.memory[0x615] = 0
        c.memory[0x616] = 0
        c.memory[0x611] = 128
        P.call(c, 0x8730, a=action, x=31, y=0, p=0x21)
        points, seen = [], set()
        for _ in range(512):
            pointer = c.memory[0x613] | c.memory[0x614] << 8
            if pointer in seen:
                break
            seen.add(pointer)
            c.memory[0x69] = 0
            c.memory[0x2c] = 0
            c.a, c.x, c.y, c.p = 85, 0, 0, 0x20
            c.sp = 0xfd
            c.stPushWord(0x5ffe)
            c.pc = 0xf158
            P.until(c, 0xf1a2, limit=6000)
            points.append(dict(pose=c.memory[0x617], y=c.memory[0x611]))
        else:
            raise AssertionError(('Unbounded original animation', action, hex(pointer), points[:8]))
        results.append(dict(action=action, points=points,
                            minY=min(p['y'] for p in points)))
    assert results[0]['minY'] == 122, results[0]
    print(json.dumps(dict(donor_SHA256=P.SHA, original_commands=results,
                         scope='Original animation instructions only, no terrain or host projection',
                         output_files=0)))


if __name__ == '__main__':
    main()
