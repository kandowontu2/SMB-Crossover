"""Use the linked Kirby air puff to reach the Red Koopa before it retires."""

import argparse
import json
from pathlib import Path
import sys

from check_tmnt_render_oa import Memory
from prepare_kirby_contacts_current_1108_v1 import plain
from prepare_kirby_green_shell_1110_v2 import once
import prepare_kirby_first_inhale_1110 as K
import prepare_kirby_red_shell_1110_v2 as V2
from verify_native_relocation import NesMPU


PRIOR = K.R / 'build/kirby-red-shell-1110-v2'
READY = '7d88f67fa99be5b9691636b6ab431123724fb7864019e2639e99eb4291eaf359'


def source_cpu(source):
    def run(m, first, last):
        cpu = NesMPU(memory=m, pc=K.address(source, first))
        cpu.sp = 0xe0
        cpu.p = 0x30
        for _ in range(400):
            if cpu.pc == K.address(source, last):
                assert cpu.sp == 0xe0
                return
            assert m[cpu.pc] != 0, hex(cpu.pc)
            cpu.step()
        raise AssertionError((first, last, hex(cpu.pc)))

    for fresh in (0, 0x40):
        m = Memory(source)
        m.page(1, 74)
        for name, value in dict(KbFloat=1, KbCopy=3, KbFresh=fresh, SavedJoypadBits=0x40,
                                PlayerFacingDir=1, Player_X_Position=591 & 255, Player_PageLoc=591 >> 8,
                                Player_Y_Position=16).items():
            m[K.address(source, name)] = value
        run(m, 'KbWeapons::Empty', 'KbWeapons::Update')
        get = lambda name: m[K.address(source, name)]
        assert get('KbCopy') == 3 and get('KbFloat') == (0 if fresh else 1)
        assert get('KbShotType') == (2 if fresh else 0)
        assert get('KbShotKind') == 0

    result = {}
    for name, cap in (('HoverDown', 256), ('FallGravity', 640)):
        m = Memory(source)
        m.page(1, 72)
        velocity = K.address(source, 'MmVY')
        total = 0
        for updates in range(1, 180):
            run(m, 'KbMovement::' + name, 'KbMovement::Integrate')
            speed = m[velocity + 1] + 256 * m[velocity + 2]
            assert 0 < speed <= cap
            total += speed
            if total >= 144 * 256:
                assert speed == cap
                result[name] = dict(cap_Q8=cap, updates_for_144px=updates)
                break
        else:
            raise AssertionError(name)
    assert result['FallGravity']['updates_for_144px'] < result['HoverDown']['updates_for_144px'] - 70
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    ready, controller = (PRIOR / name for name in ('ready.json', 'controller.lua'))
    binding, result = (PRIOR / 'capture' / name for name in ('binding.json', 'result.json'))
    assert K.sha(ready) == READY and K.sha(V2.NIGHTLY) == V2.PIN
    prior = json.loads(ready.read_text())
    for path, digest in prior['bindings'].items():
        assert K.sha(path) == digest, path
    assert json.loads(binding.read_text()) == dict(ROM_sha256=V2.PIN, ready_sha256=READY, exit_code=1)
    old = json.loads(result.read_text())
    assert old['reason'] == 'bounded-red-shell-timeout' and old['terminal']['copy'] == 3
    events = {row['event']: row for row in old['route_events']}
    release, landing = (events[name] for name in ('release-over-lower-ledge', 'lower-ledge-landing'))
    assert release['player']['frame'] == 1602 and landing['player']['frame'] == 1833
    slot = old['native_red_koopas']['624']['slot']
    assert release['slots'][slot]['state'] == 0 and release['slots'][slot]['x'] == 661
    assert landing['slots'][slot]['state'] == 132 and landing['slots'][slot]['x'] == 573

    authority, current = map(K.scoped_load, (K.AUTHORITY, V2.ROM))
    spans = {}
    for name, size in (('KbWeapons::Empty', 51), ('KbWeapons::Spawn', 90),
                       ('KbMovement::HoverDown', 12), ('KbMovement::FallGravity', 78)):
        at = K.location(authority, name)
        data = current['raw'][at:at + size]
        assert data == authority['raw'][at:at + size], name
        spans[name] = dict(offset=at, pc=K.address(authority, name), bytes=data.hex())
    authority['raw'] = current['raw']
    timing = source_cpu(authority)

    sys.path.insert(0, str(K.LUA_DEPS))
    from lupa.lua54 import LuaRuntime
    lua = LuaRuntime(unpack_returned_tuples=True)
    config, body = controller.read_text(encoding='utf-8').split('\n', 1)
    c = plain(lua.execute(config + '\nreturn C'))
    assert c['sha'] == V2.PIN and c['ram'] == prior['observer_RAM'] and c['hooks'] == prior['hooks']
    spawn = spans['KbWeapons::Spawn']
    c['hooks']['puffSpawn'] = dict(pc=spawn['pc'], offset=spawn['offset'] - 16,
                                bytes=list(bytes.fromhex(spawn['bytes'])[:8]))
    body = once(body, 'local approachHP', 'local approachHP\nlocal puffRequest,puffSpawn,puffDeflated')
    body = once(body, '  terminal_slots=terminalSlots,issued_inhale=',
                '  terminal_slots=terminalSlots,puff_request=puffRequest,puff_native_spawn=puffSpawn,\n'
                '  puff_deflated=puffDeflated,issued_inhale=')
    body = once(body, "hook('attack',function()", """hook('puffSpawn',function(s)
 if not puffRequest or puffSpawn or puffDeflated then return end
 if s['cpu.a']~=2 or r('KbCopy')~=3 or r('KbFloat')==0 or r('KbFresh')&64==0 then
  failure='unexpected-air-puff-source';return
 end
 puffSpawn={player=player(),kind=s['cpu.a'],fresh=r('KbFresh'),float=r('KbFloat')}
end)
hook('attack',function()""")
    body = once(body, "   change('release-over-lower-ledge')\n  end", """   change('request-lower-ledge-puff')
  end
  if phase=='request-lower-ledge-puff' then
   if not puffRequest then
    if r('KbFloat')==0 or grounded then failure='puff-approach-not-inflated';return {} end
    puffRequest=player()
   end
   if r('KbFloat')~=0 then
    if frame-puffRequest.frame>12 then failure='puff-input-not-acknowledged';return {} end
    return {b=true}
   end
   if not puffSpawn or r('KbCopy')~=3 then failure='puff-did-not-preserve-copy';return {} end
   puffDeflated=player()
   change('release-over-lower-ledge')
  end""")
    text = 'local C=' + K.lua(c) + '\n' + body
    assert not any(banned in text for banned in ('emu.write', 'emu.setState', 'emu.loadSavestate'))
    ok, error = lua.eval('function(s) local f,e=load(s); return f~=nil,e end')(text)
    assert ok, error
    K.prepare(args.output, V2.ROM, text, [Path(__file__), ready, controller, binding, result,
                                         K.AUTHORITY, K.AUTHORITY.with_suffix('.dbg')],
              expected=V2.PIN, timeout=200, allow_interactive=True, scope=prior['scope'])
    output = args.output / 'ready.json'
    q = json.loads(output.read_text())
    q.update(observer_RAM=c['ram'], hooks=c['hooks'], previous_native_SHA256=K.sha(result),
             actual_puff_source_spans=spans, CPU_puff_preserves_red_copy=True,
             CPU_Q8_descent=timing, observed_previous_float_release_frame=1602,
             observed_previous_landing_frame=1833)
    output.write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
