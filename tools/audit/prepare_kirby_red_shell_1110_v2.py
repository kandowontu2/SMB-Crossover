"""Rebind Red Koopa 4-3 to c8bd and add a native lower-ledge target route."""

import argparse
import json
from pathlib import Path
import re
import sys

import prepare_kirby_red_shell_1110 as V1
import prepare_kirby_first_inhale_1110 as K
from prepare_kirby_contacts_current_1108_v1 import plain
from prepare_kirby_green_shell_1110_v2 import once


R = V1.R
PRIOR = R / 'build/kirby-red-shell-1110'
READY = '58096dca4ea5410b17f5d5b0d15bdd81f4651c36ff874819eac04fb69b55ff1f'
ROM = R / 'build/mini-contact-platform-combo-native-1110/candidate.nes'
PIN = 'c8bd2e2c75015b84fe7bc3c4dba5b24b87e517620ef914ff229b5d4249acbe48'
NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
POLICY = R / 'tools/playthroughs/kirby_red_shell_1110_v2.lua'
PATCH_OFFSET = 16 + 126 * 8192 + 0x1659
PATCH_SIZE = 0x9690 - 0x9659


def checked_previous():
    ready, controller = (PRIOR / n for n in ('ready.json', 'controller.lua'))
    binding, result = (PRIOR / 'capture' / n for n in ('binding.json', 'result.json'))
    assert K.sha(ready) == READY
    q = json.loads(ready.read_text())
    assert q['ROM_sha256'] == V1.PIN
    for path, digest in q['bindings'].items():
        assert K.sha(path) == digest, path
    assert json.loads(binding.read_text()) == dict(ROM_sha256=V1.PIN, ready_sha256=READY, exit_code=1)
    # The original file remains intact. Its only malformed keys are its two
    # numeric constructor coordinates, recovered in memory for comparison.
    fixed, count = re.subn(r'([,{])(448|464):', r'\1"\2":', result.read_text())
    assert count == 2
    old = json.loads(fixed)
    assert old['reason'] == 'bounded-red-shell-timeout' and old['terminal']['x'] == 441
    assert old['terminal']['copy'] == 3 and old['terminal']['hp'] == 6 and old['terminal']['lives'] == 2
    assert 'issued_shot' not in old and len(old['native_red_koopas']) == 2
    return q, controller, [ready, controller, binding, result]


def retarget(body):
    lo = body.index('local function steer(facing, b)')
    hi = body.index('emu.addEventCallback(function()\n polls=polls+1', lo)
    body = body[:lo] + POLICY.read_text(encoding='utf-8') + '\n' + body[hi:]
    body = once(body, 'local births,redBirths,checkpoints={},{},{}',
                'local births,redBirths,checkpoints,routeEvents,retirements={},{},{},{},{}')
    body = once(body, ' local rows={}\n if #v>0 then', ''' local rows={}
 local dense,count=true,0
 for k in pairs(v) do
  count=count+1
  if type(k)~='number' or k<1 or k%1~=0 or k>#v then dense=false end
 end
 if dense and count==#v and count>0 then''')
    body = once(body, " for k,a in pairs(v) do rows[#rows+1]=json(k)..':'..json(a) end",
                " for k,a in pairs(v) do rows[#rows+1]=json(tostring(k))..':'..json(a) end")
    body = once(body, ' local last=player()\n local passed=', ''' local last=player()
 local terminalSlots={}
 for i=0,5 do terminalSlots[#terminalSlots+1]=actor(i) end
 local passed=''')
    body = once(body, '  native_red_koopas=redBirths,issued_inhale=',
                '  native_red_koopas=redBirths,route_events=routeEvents,native_retirements=retirements,\n'
                '  terminal_slots=terminalSlots,issued_inhale=')
    body = once(body, "print('Kirby df03 red-shell ", "print('Kirby c8bd red-shell ")
    body = once(body, '(a.x==448 or a.x==464)', '(a.x==448 or a.x==464 or a.x==624)')
    body = once(body, "hook('inhale',function()", '''hook('eraseActor',function(s)
 local a=actor(s['cpu.x'])
 local born=births[a.slot]
 if born and a.id==3 and a.flag==1 and #retirements<8 then
  retirements[#retirements+1]={actor=a,birth=born,player=player(),earned_capture=not not(capture and capture.birth==born)}
 end
end)
hook('inhale',function()''')
    body = once(body, 'if not inhaleFresh or not births[a.slot] or a.id~=3',
                'local born=births[a.slot]\n if not inhaleFresh or not born or born.x==624 or a.id~=3')
    body = once(body, 'capture={player=player(),target=a,gap=gap}',
                'capture={player=player(),target=a,birth=born,gap=gap}')
    body = once(body, 'row.qualified=native and a.slot~=capture.target.slot and',
                'row.qualified=native and born~=capture.birth and')
    body = once(body, 'if x()>=570 then', 'if x()>=676 then')
    return body


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    prior, controller, refs = checked_previous()
    assert K.sha(ROM) == PIN and K.sha(NIGHTLY) == PIN
    old, raw = V1.ROM.read_bytes(), ROM.read_bytes()
    assert len(old) == len(raw) and old[:PATCH_OFFSET] == raw[:PATCH_OFFSET]
    assert old[PATCH_OFFSET + PATCH_SIZE:] == raw[PATCH_OFFSET + PATCH_SIZE:]
    count = sum(a != b for a, b in zip(old[PATCH_OFFSET:PATCH_OFFSET + PATCH_SIZE],
                                     raw[PATCH_OFFSET:PATCH_OFFSET + PATCH_SIZE]))
    assert count > 0
    for span in prior['streams'].values():
        at = span['offset']
        assert raw[at:at + span['size']].hex() == span['bytes']
    assert prior['streams']['E_GroundArea13']['bytes'].startswith('c783d703428f7a03')
    authority, current = map(K.scoped_load, (K.AUTHORITY, ROM))
    at = K.location(authority, 'EraseEnemyObject')
    assert raw[at:at + 9] == authority['raw'][at:at + 9] == bytes.fromhex('a90095109517951f9d')
    authority['raw'] = raw
    state = V1.N.fresh(authority)
    V1.N.put(state, WorldNumber=3, LevelNumber=2, AreaNumber=3, AreaPointer=0x2c, AreaType=1,
             SelectedCharacter=13, CrossoverBehaviorVersion=0)
    V1.N.invoke(state, 'GetAreaDataAddrs')
    length = K.address(authority, 'AreaObjectLength')
    for slot in range(3):
        state[length + slot] = 255
    cols = {}
    for col in range(43):
        V1.N.invoke(state, 'AreaParserCore')
        if 30 <= col < 43:
            cols[col * 16] = [V1.N.get(state, 'MetatileBuffer', row) for row in range(13)]
        V1.N.invoke(state, 'IncrementColumnPos')
    assert all(cols[x][10] in (0x19, 0x1a, 0x1b) for x in (576, 592, 608, 624, 640, 656, 672))
    assert cols[592][3] == cols[608][3] == 0

    sys.path.insert(0, str(K.LUA_DEPS))
    from lupa.lua54 import LuaRuntime
    lua = LuaRuntime(unpack_returned_tuples=True)
    config, body = controller.read_text(encoding='utf-8').split('\n', 1)
    c = plain(lua.execute(config + '\nreturn C'))
    assert c['ram'] == prior['observer_RAM'] and c['hooks'] == prior['hooks'] and c['sha'] == V1.PIN
    for hook in c['hooks'].values():
        off = hook['offset'] + 16
        assert raw[off:off + len(hook['bytes'])] == bytes(hook['bytes'])
    for span in prior['linked_shell_spans'].values():
        data = bytes.fromhex(span['bytes'])
        off = span['physical_offset']
        assert raw[off:off + len(data)] == data
    c['hooks']['eraseActor'] = dict(pc=K.address(authority, 'EraseEnemyObject'), offset=at - 16,
                                   bytes=list(raw[at:at + 9]))
    c['sha'] = PIN
    updated = retarget(body)
    dependencies = set(re.findall(r"\br\('([\w]+)'", updated))
    dependencies.update(n for pair in re.findall(r"\bpos\('([\w]+)','([\w]+)'", updated) for n in pair)
    assert dependencies <= c['ram'].keys()
    assert all(K.address(current, n) == a for n, a in c['ram'].items() if n in current['syms'])
    text = 'local C=' + K.lua(c) + '\n' + updated
    assert not any(banned in text for banned in ('emu.write', 'emu.setState', 'emu.loadSavestate'))
    ok, error = lua.eval('function(s) local f,e=load(s); return f~=nil,e end')(text)
    assert ok, error
    serializer = updated[updated.index('local function json(v)'):updated.index('local function shot(slot)')]
    for expression, expected in (('{[448]={x=448},[624]={x=624}}', {'448': {'x': 448}, '624': {'x': 624}}),
                                 ('{[1]=1,[3]=3}', {'1': 1, '3': 3}), ('{{x=448},{x=624}}', [{'x': 448}, {'x': 624}])):
        assert json.loads(lua.execute(serializer + '\nreturn json(' + expression + ')')) == expected
    K.prepare(args.output, ROM, text, [Path(__file__), POLICY, *refs, K.AUTHORITY, K.AUTHORITY.with_suffix('.dbg')],
              expected=PIN, timeout=200, allow_interactive=True,
              scope='Easy Kirby 4-3. Real Start Level menu, earned copy from first Red Koopa pair. '
                    'Controller-only native shell defeat against a distinct authored Red Koopa. Prepared only.')
    output = args.output / 'ready.json'
    q = json.loads(output.read_text())
    q.update(observer_RAM=c['ram'], hooks=c['hooks'], prior_negative_sha256=K.sha(refs[-1]),
             exact_downloads_binding=PIN, current_ROM_changed_only_fixed126_9659_9690=True, changed_bytes=count,
             authored_red_koopa_x=[448, 464, 624], CPU_later_ledge_columns=cols)
    output.write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
