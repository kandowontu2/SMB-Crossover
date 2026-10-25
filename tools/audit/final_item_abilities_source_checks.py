"""Reproduce the narrow ROM84 enemy-floor control behind a rejected fixture."""
from pathlib import Path
import argparse
import hashlib
import json
from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load

ROM84 = '84e55b6d60da4be5550d823f88ee40a9b220dbef5a1e8dd21de3d69aa28cb328'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    assert sha(a.rom) == ROM84
    a.output.mkdir(parents=True, exist_ok=False)
    b = scoped_load(a.rom)
    offset = b['raw'][location(b, 'BlockBuffer_Y_Adder') + 0x15]
    assert offset == 24
    rows = []
    for initial, floor, expected in [(192, 208, 1), (184, 208, 0), (168, 192, 0)]:
        q = Arena(b, 12)
        q.put(Player_PageLoc=0, ScreenLeft_PageLoc=0, ScreenLeft_X_Pos=0,
              Enemy_Flag=1, Enemy_ID=6, Enemy_State=0, Enemy_X_Position=112,
              Enemy_PageLoc=0, Enemy_Y_Position=initial, Enemy_Y_HighPos=1,
              Enemy_X_Speed=0, Enemy_Y_Speed=0, Enemy_MovingDir=1, AreaType=1)
        for i in range(416):
            q.set('Block_Buffer_1', 0, i)
        for col in range(16):
            q.set('Block_Buffer_1', 0x54, ((floor-32)//16)*16+col)
        _, trace = q.invoke('EnemyToBGCollisionDet')
        row = dict(initial_canonical_y=initial, floor_y=floor,
                   result_y=q.get('Enemy_Y_Position'), result_state=q.get('Enemy_State'),
                   state_writes=[w for w in trace if w['address'] == address(b, 'Enemy_State')])
        assert (row['result_y'], row['result_state']) == (initial, expected)
        rows.append(row)
    result = dict(passed=True, ROM_sha256=ROM84, script_sha256=sha(Path(__file__)),
                  enemy_foot_offset=offset, controls=rows,
                  scope='Direct CPU control of original native enemy-floor admission. This explains invalid target staging and does not qualify gameplay or native PPU timing.')
    f = a.output / 'proof.json'
    f.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
