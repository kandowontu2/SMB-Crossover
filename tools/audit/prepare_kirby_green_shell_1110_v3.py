"""Bind the unchanged green-shell replay to the linked shell motion and box."""

import argparse
import itertools
import json
from pathlib import Path
import sys

from check_tmnt_render_oa import Memory
from prepare_kirby_contacts_current_1108_v1 import plain
import prepare_kirby_first_inhale_1110 as V1
from prepare_kirby_green_shell_1110_v2 import once
from verify_native_relocation import NesMPU


PRIOR = V1.R / 'build/kirby-green-shell-1110-v2'
READY = '412304d99fe67e7adf5933fa5add00b9842a3976711202b69967b0006459e380'
LINKED = V1.AUTHORITY.with_name('kirby_weapons.s')
BOX_SOURCE = V1.R / 'tools/reference/kirby_shell_contact_1101_v1.inc'


def overlap(box, ex, ey, sx, sy):
    left, top, right, bottom = box
    return sx + 7 >= ex + left and sx - 8 <= ex + right and sy + 7 >= ey + top and sy - 8 <= ey + bottom


def exercise(source, boxes, observed, speed):
    def call(name, **fields):
        m = Memory(source)
        m.page(1, 74)
        for name_, val in fields.items():
            m[V1.address(source, name_)] = val
        cpu = NesMPU(memory=m, pc=V1.address(source, name))
        cpu.sp = 0xe0
        cpu.p = 0x30
        cpu.stPushWord(0x5aff)
        for _ in range(800):
            if cpu.pc == 0x5b00:
                assert cpu.sp == 0xe0
                return m, cpu
            assert m[cpu.pc] != 0, hex(cpu.pc)
            cpu.step()
        raise AssertionError(('CPU step cap', name, hex(cpu.pc)))

    for copy, facing in itertools.product((2, 3), (1, 2)):
        m, _ = call('KbWeapons::CopyAttack', KbCopy=copy, PlayerFacingDir=facing,
                    Player_X_Position=0x40, Player_PageLoc=6, Player_Y_Position=176)
        speed_signed = speed if facing == 1 else -speed
        expected = dict(KbShotType=3, KbShotKind=copy, KbShotVXHi=speed_signed & 255, KbShotVXLo=0,
                        KbShotX=0x50 if facing == 1 else 0x40, KbShotPage=6, KbShotY=196, KbShotAge=0)
        assert {n: m[V1.address(source, n)] for n in expected} == expected

    def actual(ctrl, high, ex, ey, sx, sy):
        _, cpu = call('KbShellEnemyContact', Enemy_BoundBoxCtrl=ctrl, Enemy_Y_HighPos=high,
                      Enemy_X_Position=ex & 255, Enemy_PageLoc=ex >> 8, Enemy_Y_Position=ey,
                      KbShotX=sx & 255, KbShotPage=sx >> 8, KbShotY=sy, KbSavedSlot=0)
        assert cpu.x == 0
        return bool(cpu.p & 1)

    checked = 0
    for ctrl, (left, top, right, bottom) in enumerate(boxes):
        ex, ey = 0x1fe, 184
        for xoff, yoff in itertools.product((left - 8, left - 7, right + 8, right + 9),
                                             (top - 8, top - 7, bottom + 8, bottom + 9)):
            sx, sy = ex + xoff, ey + yoff
            assert actual(ctrl, 1, ex, ey, sx, sy) == overlap(boxes[ctrl], ex, ey, sx, sy)
            checked += 1
    t, p = observed['target'], observed['shell']
    assert actual(9, 1, t['x'], t['y'], p['x'], p['y'])
    assert not actual(9, 0, t['x'], t['y'], p['x'], p['y'])
    assert not actual(12, 1, t['x'], t['y'], p['x'], p['y'])
    return dict(copy_launch_cases=4, native_rectangle_boundary_cases=checked,
                observed_contact_C1=True, observed_hidden_or_invalid_C0=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    ready, controller = (PRIOR / name for name in ('ready.json', 'controller.lua'))
    binding, result = (PRIOR / 'capture' / name for name in ('binding.json', 'result.json'))
    assert V1.sha(ready) == READY
    prior = json.loads(ready.read_text())
    for path, digest in prior['bindings'].items():
        assert V1.sha(path) == digest, path
    assert json.loads(binding.read_text()) == dict(ROM_sha256=V1.PIN, ready_sha256=READY, exit_code=1)
    negative = json.loads(result.read_text())
    observed = negative['shell_contact']
    assert not negative['passed'] and negative['reason'] == 'unqualified-green-shell-hit'
    assert [k for k, v in observed['v1_predicates'].items() if not v] == ['dy_within12', 'vx4']
    assert observed['target_class'] == 'intended-goomba' and observed['dy'] == 14
    assert negative['native_defeat_return']['target']['state'] == 34

    source, target = map(V1.scoped_load, (V1.AUTHORITY, V1.ROM))
    raw = target['raw']
    spans = {}

    def exact(label, size):
        at = V1.location(source, label)
        data = raw[at:at + size]
        assert data == source['raw'][at:at + size], label
        spans[label] = dict(pc=V1.address(source, label), physical_offset=at, bytes=data.hex())
        return data

    speed_data = exact('KickedShellXSpdData', 2)
    assert speed_data == bytes.fromhex('30d0')
    speed = speed_data[0] >> 4
    speed_leaf = exact('KbWeapons::ShellSpeed', 17)
    assert speed_leaf[:2] == bytes((0xa9, speed)) and speed_leaf[9:11] == bytes((0xa9, 256 - speed))
    assert 'ShellSpeed:' in LINKED.read_text() and 'jsr KbShellEnemyContact' in LINKED.read_text()
    call = exact('KbWeapons::ShellContact', 11)
    adapter = V1.address(source, 'KbShellEnemyContact')
    assert call[:3] == bytes((0x20, adapter & 255, adapter >> 8))
    exact('KbShellEnemyContact', 163)
    data = exact('BoundBoxCtrlData', 48)
    boxes = [list(data[i:i + 4]) for i in range(0, len(data), 4)]
    assert boxes[9] == [3, 14, 13, 20]
    source['raw'] = raw
    cpu = exercise(source, boxes, observed, speed)
    probes = negative['projectile_probes']
    assert [p['shell']['age'] for p in probes] == list(range(1, 7))
    origin = negative['actual_ground_copy_attack']['player']['x'] + 16
    assert all(p['shell']['vx_hi'] == speed and p['shell']['vx_lo'] == 0 and
               p['shell']['x'] == origin + speed * p['shell']['age'] for p in probes)

    sys.path.insert(0, str(V1.LUA_DEPS))
    from lupa.lua54 import LuaRuntime
    lua = LuaRuntime(unpack_returned_tuples=True)
    config, body = controller.read_text(encoding='utf-8').split('\n', 1)
    c = plain(lua.execute(config + '\nreturn C'))
    assert c['ram'] == prior['observer_RAM'] and c['hooks'] == prior['hooks'] and c['sha'] == V1.PIN
    c['ram']['Enemy_BoundBoxCtrl'] = V1.address(source, 'Enemy_BoundBoxCtrl')
    if 'Enemy_BoundBoxCtrl' in target['syms']:
        assert c['ram']['Enemy_BoundBoxCtrl'] == V1.address(target, 'Enemy_BoundBoxCtrl')
    c['native_boxes'], c['shell_speed'] = boxes, speed
    old = " row.qualified=native and p.vx_hi==4 and p.vx_lo==0 and math.abs(dx)<=12 and math.abs(dy)<=12 and\n               row.object_offset==a.slot"
    new = """ local control=r('Enemy_BoundBoxCtrl',a.slot)
 local box=C.native_boxes[control+1]
 row.native_box_control=control
 row.shell_rectangle={left=p.x-8,top=p.y-8,right=p.x+7,bottom=p.y+7}
 if box then row.native_rectangle={left=a.x+box[1],top=a.y+box[2],right=a.x+box[3],bottom=a.y+box[4]} end
 local sbox,ebox=row.shell_rectangle,row.native_rectangle
 row.linked_box_overlap=not not (ebox and sbox.right>=ebox.left and sbox.left<=ebox.right and
                                sbox.bottom>=ebox.top and sbox.top<=ebox.bottom)
 local first=probes[1] and probes[1].shell
 local origin=attack.player.x+16
 row.linked_forward_trajectory=not not (first and first.age==1 and first.slot==p.slot and
   first.vx_hi==C.shell_speed and first.vx_lo==0 and first.x==origin+C.shell_speed and
   p.vx_hi==C.shell_speed and p.vx_lo==0 and p.age>0 and p.age<90 and p.x==origin+C.shell_speed*p.age)
 row.qualified=native and row.linked_box_overlap and row.linked_forward_trajectory and row.object_offset==a.slot"""
    new_body = once(body, old, new)
    text = 'local C=' + V1.lua(c) + '\n' + new_body
    ok, error = lua.eval('function(s) local f,e=load(s); return f~=nil,e end')(text)
    assert ok, error
    V1.prepare(args.output, V1.ROM, text, [Path(__file__), ready, controller, binding, result, LINKED, BOX_SOURCE,
                                           V1.AUTHORITY, V1.AUTHORITY.with_suffix('.dbg'), Path(c['policy'])],
               expected=V1.PIN, timeout=220, allow_interactive=True, scope=prior['scope'])
    output = args.output / 'ready.json'
    q = json.loads(output.read_text())
    q.update(observer_RAM=c['ram'], hooks=c['hooks'], original_controls_unchanged=True,
             previous_negative_SHA256=V1.sha(result), linked_shell_spans=spans, linked_CPU=cpu,
             native_box_control9=boxes[9], shell_forward_speed=speed)
    output.write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
