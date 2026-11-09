"""Prepare the stock 4-3 Red Koopa pair witness on delivered df03."""

import argparse
import json
from pathlib import Path
import re
import sys

import check_hogan_current_bounded_v1 as N
import prepare_kirby_first_inhale_1110 as V1
from prepare_kirby_contacts_current_1108_v1 import plain
from prepare_kirby_green_shell_1110_v2 import once


R = V1.R
ROM = R / 'build/mini-platform-pair-native-1110/candidate.nes'
PIN = 'df03fc35ebdc516a8df0b501bbe2008e52836aa8fcfad5c34e4df76783e9f331'
GREEN = R / 'build/kirby-green-shell-1110-v3'
READY = '7f084c5e986179f51d10a12dd709920be5007a3a4b90758f1161f708444496d0'
SOURCE = R / 'src/level_tiles.s'
CHEATS = R / 'src/cheats.s'
POLICY = R / 'tools/playthroughs/kirby_red_shell_1110.lua'


def retarget(body):
    def replace_span(start, end, replacement):
        nonlocal body
        assert body.count(start) == 1 and body.count(end) == 1
        lo, hi = body.index(start), body.index(end)
        assert lo < hi
        body = body[:lo] + replacement + body[hi:]

    replace_span("hook('init',function(s)", "hook('inhale',function()", """hook('redInit',function(s)
 local a=actor(s['cpu.x'])
 if a.id==3 and (a.x==448 or a.x==464) and a.flag==1 and a.y_high==1 then
  births[a.slot]=a;redBirths[a.x]=a;koopa=koopa or a
 end
end)
""")
    replace_span('local function nextEnemy(origin)', 'emu.addEventCallback(function()\n polls=polls+1', POLICY.read_text() + '\n')
    replace_span(' row.v1_predicates=', ' appendBounded(contactAttempts,row)', '')
    body = once(body, " press('start')\n ready(function()return r('CrossoverMenuState')==2", """ press('down');press('start')
 assert(r('CrossoverMenuState')==4,'Actual Options opens')
 press('down');press('down');press('a')
 assert(r('CrossoverMenuState')==6 and r('CrossoverOptionsFocus')==0,'Actual Cheats opens')
 press('down')
 for i=1,14 do
  press('right');assert(r('CheatStartLevel')==0x20+i and noCheats(),'Only Start Level changes')
 end
 events[1]={frame=frame,start_level=r('CheatStartLevel'),cheats=r('CheatInvincible')}
 press('b');press('b')
 ready(function()return r('CrossoverMenuState')==0 and r('CrossoverTitleDrawn')==1 and
   r('DisableScreenFlag')==0 end,180,'title return')
 press('start')
 ready(function()return r('CrossoverMenuState')==2""")
    edits = {
        'local births,checkpoints={},{}': 'local births,redBirths,checkpoints={},{},{}',
        "ROSTER_CONFIG={name='kirby'}\nlocal route=assert(dofile(C.policy))\n": '',
        "r('WorldNumber')==0 and r('LevelNumber')==0 and r('AreaType')==1 and r('AreaAddrsLOffset')==5":
            "r('WorldNumber')==3 and r('LevelNumber')==2 and r('AreaType')==1 and r('AreaAddrsLOffset')==12 and r('AreaPointer')==0x2c",
        "return r('CheatStartLevel')==0 and r('CheatInvincible')==0": "return r('CheatInvincible')==0",
        "r('CrossoverBehaviorVersion')==0 and noCheats()\nend":
            "r('CrossoverBehaviorVersion')==0 and r('CheatStartLevel')==0x2e and noCheats()\nend",
        "and active() and identity() and stage() and last.copy==2":
            "and redBirths[448] and redBirths[464] and active() and identity() and stage() and last.copy==3",
        'no_cheats=noCheats(),': "all_other_cheats_off=noCheats(),start_level_override=r('CheatStartLevel'),",
        'native_green_koopa=koopa,': 'native_red_koopas=redBirths,',
        "print('Kirby 29aa green-shell ": "print('Kirby df03 red-shell ",
        "r('SavedJoypadBits')&0x43~=0x41": "r('SavedJoypadBits')&0x43~=(0x40|inhaleInput.facing)",
        "r('PlayerFacingDir')~=1 then\n  failure='unexpected-fresh-inhale-state'":
            "r('PlayerFacingDir')~=inhaleInput.facing then\n  failure='unexpected-fresh-inhale-state'",
        'target=actor(koopa.slot)': 'target=actor(inhaleInput.target.slot)',
        'local gap=a.x-x()': 'local gap=(a.x-x())*(inhaleInput.facing==1 and 1 or -1)',
        'a.slot~=koopa.slot or a.id~=0 or not aligned(a) or a.state~=0':
            'not births[a.slot] or a.id~=3 or not aligned(a) or a.state>=2',
        "r('KbActionAge')~=0 or\n    r('PlayerFacingDir')~=1":
            "r('KbActionAge')>8 or\n    r('PlayerFacingDir')~=inhaleInput.facing",
        "r('KbMouth')~=1 or r('KbMouthCopy')~=2": "r('KbMouth')~=4 or r('KbMouthCopy')~=3",
        "r('KbCopy')~=2 or r('SavedJoypadBits')&64==0": "r('KbCopy')~=3 or r('SavedJoypadBits')&64==0",
        "r('Player_Y_Position')~=176 or r('PlayerFacingDir')~=1 then":
            "r('KbFloat')~=0 or r('PlayerFacingDir')~=shotInput.facing then",
        'native_goomba=born': 'native_red_koopa=born',
        'local native=a.id==6 and a.state<2': 'local native=a.id==3 and a.state<2',
        'born and born.id==6 and born.flag==1': 'born and born.id==3 and born.flag==1',
        "'intended-goomba' or 'other-natural-goomba'": "'intended-red-koopa' or 'other-natural-red-koopa'",
        'local origin=attack.player.x+16':
            'local origin=attack.player.x+(attack.facing==1 and 16 or 0)\n'
            ' local speed=attack.facing==1 and C.shell_speed or -C.shell_speed\n local vx=speed&255',
        'first.vx_hi==C.shell_speed and first.vx_lo==0 and first.x==origin+C.shell_speed':
            'first.vx_hi==vx and first.vx_lo==0 and first.x==origin+speed',
        'p.vx_hi==C.shell_speed and p.vx_lo==0 and p.age>0 and p.age<90 and p.x==origin+C.shell_speed*p.age':
            'p.vx_hi==vx and p.vx_lo==0 and p.age>0 and p.age<C.red_return_age and p.x==origin+speed*p.age',
        'row.linked_forward_trajectory': 'row.linked_outbound_trajectory',
        'row.qualified=native and': 'row.qualified=native and a.slot~=capture.target.slot and',
        'genuine_natural_goomba': 'genuine_natural_red_koopa',
        'contact.qualified and a.id==6': 'contact.qualified and a.id==3',
        ' events[1]={frame=frame,slot=C.slot': ' events[2]={frame=frame,slot=C.slot',
        'not capture and x()>=1744': 'not capture and x()>=544',
        'if x()>=2070': 'if x()>=570',
        'frame>=11000': 'frame>=4200',
    }
    multi = {'r(\'SavedJoypadBits\')&0x43~=0x41': 2,
             "r('KbMouth')~=1 or r('KbMouthCopy')~=2": 2,
             'row.linked_forward_trajectory': 2, 'genuine_natural_goomba': 2}
    for old, new in edits.items():
        assert body.count(old) == multi.get(old, 1), old
        body = body.replace(old, new)
    assert body.count('p.kind~=2') == 2
    body = body.replace('p.kind~=2', 'p.kind~=3').replace('green-shell', 'red-shell').replace('green-', 'red-')
    return body


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert V1.sha(ROM) == PIN and V1.sha(GREEN / 'ready.json') == READY
    assert V1.sha(V1.AUTHORITY) == V1.AUTHORITY_ROM and V1.sha(V1.AUTHORITY.with_suffix('.dbg')) == V1.AUTHORITY_DBG
    q = json.loads((GREEN / 'ready.json').read_text())
    binding, result = (GREEN / 'capture' / n for n in ('binding.json', 'result.json'))
    assert json.loads(binding.read_text()) == dict(ROM_sha256=V1.PIN, ready_sha256=READY, exit_code=0)
    assert json.loads(result.read_text())['passed']
    previous = GREEN / 'controller.lua'
    assert V1.sha(previous) == q['bindings'][str(previous)]
    authority, current = map(V1.scoped_load, (V1.AUTHORITY, ROM))
    raw = current['raw']
    source = SOURCE.read_text()
    streams = {}
    for name in ('E_GroundArea13', 'L_GroundArea13'):
        part = source.split(name + ':\n', 1)[1].split('\n\n', 1)[0]
        data = bytes(int(v, 16) for v in re.findall(r'\$([\da-f]{2})\b', part))
        assert data and raw.count(data) == 1
        streams[name] = dict(offset=raw.find(data), size=len(data), bytes=data.hex())
    assert streams['E_GroundArea13']['bytes'].startswith('c783d703')
    assert '7716' in streams['L_GroundArea13']['bytes']
    for span in q['linked_shell_spans'].values():
        data = bytes.fromhex(span['bytes'])
        start = span['physical_offset']
        assert raw[start:start + len(data)] == data

    def bind_hook(symbol, size):
        at = V1.location(authority, symbol)
        data = raw[at:at + size]
        assert data == authority['raw'][at:at + size]
        return dict(pc=V1.address(authority, symbol), offset=at - 16, bytes=list(data))

    return_point = V1.location(authority, 'KbWeapons::NotArc')
    before_return = raw[return_point:V1.location(authority, 'KbWeapons::NotReturn')]
    assert before_return.count(bytes.fromhex('c920')) == 1
    pull = bind_hook('KbWeapons::Pull', 3)
    suction = V1.address(authority, 'KbWeapons::Suction')
    assert pull['bytes'] == [0x20, suction & 255, suction >> 8]

    sys.path.insert(0, str(V1.LUA_DEPS))
    from lupa.lua54 import LuaRuntime
    lua = LuaRuntime(unpack_returned_tuples=True)
    config, body = previous.read_text(encoding='utf-8').split('\n', 1)
    c = plain(lua.execute(config + '\nreturn C'))
    assert c['ram'] == q['observer_RAM'] and c['hooks'] == q['hooks'] and c['sha'] == V1.PIN
    for hook in c['hooks'].values():
        at = hook['offset'] + 16
        assert raw[at:at + len(hook['bytes'])] == bytes(hook['bytes'])
    c['hooks']['redInit'] = bind_hook('InitRedKoopa', 9)
    c['red_return_age'] = 32
    c['sha'] = PIN
    c.pop('policy')
    new_body = retarget(body)
    names = set(re.findall(r"\br\('([\w]+)'", new_body))
    names.update(n for pair in re.findall(r"\bpos\('([\w]+)','([\w]+)'", new_body) for n in pair)
    c['ram'] = {n: V1.address(authority, n) for n in sorted(names)}
    assert all(V1.address(current, n) == a for n, a in c['ram'].items() if n in current['syms'])
    assert c['ram']['SelectedCharacter'] == 0x6002 and c['ram']['CheatStartLevel'] == 0x7ffc
    authority['raw'] = raw
    state = N.fresh(authority)
    N.put(state, CheatStartLevel=0x2e)
    N.invoke(state, 'CheatsApplyStartingLevel')
    fields = {name: N.get(state, name) for name in ('WorldNumber', 'LevelNumber', 'AreaNumber', 'HalfwayPage')}
    assert fields == dict(WorldNumber=3, LevelNumber=2, AreaNumber=3, HalfwayPage=0)
    N.put(state, AreaPointer=0x2c, AreaType=1, SelectedCharacter=13, CrossoverBehaviorVersion=0)
    N.invoke(state, 'GetAreaDataAddrs')
    length = V1.address(authority, 'AreaObjectLength')
    for slot in range(3):
        state[length + slot] = 255
    columns = {}
    for col in range(32):
        N.invoke(state, 'AreaParserCore')
        if 15 <= col <= 30:
            columns[col * 16] = [N.get(state, 'MetatileBuffer', row) for row in range(13)]
        N.invoke(state, 'IncrementColumnPos')
    assert all(columns[x][7] in (0x19, 0x1a, 0x1b) for x in (400, 416, 432, 448, 464)), columns
    edges, routes = V1.menu_routes(authority, 0)
    assert c['menu'] == [routes[i][0] if routes[i] else '' for i in sorted(edges)]
    text = 'local C=' + V1.lua(c) + '\n' + new_body
    assert not any(banned in text for banned in ('emu.write', 'emu.setState', 'emu.loadSavestate'))
    ok, error = lua.eval('function(s) local f,e=load(s); return f~=nil,e end')(text)
    assert ok, error
    V1.prepare(args.output, ROM, text, [Path(__file__), POLICY, SOURCE, CHEATS, previous, GREEN / 'ready.json',
                                      binding, result, V1.AUTHORITY, V1.AUTHORITY.with_suffix('.dbg')],
               expected=PIN, timeout=200, allow_interactive=True,
               scope='Easy Kirby 4-3. Actual Start Level menu only. Native Red Koopa pair, earned copy, '
                     'normal outbound shell and native defeat of the other Red Koopa. Prepared only.')
    ready = args.output / 'ready.json'
    receipt = json.loads(ready.read_text())
    receipt.update(observer_RAM=c['ram'], hooks=c['hooks'], stages=dict(selected='4-3', start_level=46, **fields),
                   streams=streams, authored_red_pair_world_x=[448, 464], linked_shell_spans=q['linked_shell_spans'],
                   CPU_layout_columns_240_to_480=columns,
                   red_shell_return_age=32, route_reason='1-2 first red is X2336 with lifts/control ahead; 4-3 has adjacent same-row Red Koopas')
    ready.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
