"""Rebind the exact funded Prince run with one grounded standing-A approach."""

import argparse
from pathlib import Path
import sys

from prepare_prince_full11_1110 import once
from prepare_prince_primary_align_native_1110 import CANDIDATE, OUT as BASE, R, SYMBOLS, checked, read
from prepare_selected_native_packet_v1 import prepare, sha


OUT = R / 'build/prince-koopa-standing-native-1110'
NATIVE = BASE / 'native'
ROM = BASE / 'prince-private.nes'
PINS = {
    NATIVE / 'ready.json': 'c91e3ce9e3b3749a9adecf0507bcee0ef5e8441c0ebded742b05448303d98665',
    NATIVE / 'controller.lua': '28f4a9e9943c389ca392d4ce8447ea4b21541fcc4feb35b9fa88762a26d5af9b',
    NATIVE / 'capture/binding.json': '6c232445d96f85a3ebf37b211178ac89a7fc7ded6041ae1eb84a3797e915bd63',
    NATIVE / 'capture/full11.json': 'ae7da0530107d9852f4b6a98e223ca5027beb8414aea25eea168428091c1e2bd',
    NATIVE / 'capture/post-pit-goombas.json': '2610e4556c5d7d23e9f55c1aec16d211b187ae7effdc5e4a665bc469a321b75d',
    NATIVE / 'capture/source-phases.csv': '90bd171a6d01e7b2893948bd93cb6e5eac9a3d78fef21614bd6e6d2651ea7e69',
    NATIVE / 'capture/prince-diagnostic.json': '5ba31a5e572a997694a18bfda4af53019ea91adf9ecbb09b8ff7df44ca1bebdb',
}


CONTROL = r'''
local function koopaStanding(s,o,support)
 if not postPit.clear or not o or o.left~=2448 then return false end
 local x=s.world_x
 local p=route.koopa_standing
 if p and p.clear then return false end
 if not p then
  if route.mode~='approach' or x<1550 then return false end
  if x<=1552 and s.source_frame==13 and (s.phase&3)==1 and s.source_facing==255 and support and runReady(s) then
   p={brake={state=s,Main=admitted,frame=frame},HP=s.HP,minimum_y=s.native_y}
   route.koopa_standing=p
   routeMode('koopa-brake',{})
  elseif x>=1564 then routeFail('Post-pit running pose missed the scoped Koopa brake')
  else return false end
 end
 if s.HP~=p.HP then routeFail('Standing-A Koopa approach lost source HP')end
 if not p.actor then
  for i=0,5 do
   local a=groupActor(i)
   if a.flag==1 and a.id==0 and a.state&32==0 and 1590<=a.x and a.x<=1720 and a.y==184 then
    p.actor={actor=a,Main=admitted,frame=frame};break
   end
  end
 end
 if route.mode=='koopa-brake' then
  route.pad={}
  if idleReady(s) and support then
   if s.source_facing~=255 or s.native_y~=176 or x<1580 or x>1588 then
    routeFail('Koopa standing A lacks the measured supported stance')
   end
   p.request={state=s,Main=admitted,frame=frame}
   routeMode('koopa-stand-A',{'a'})
  elseif admitted-route.changed>65 then routeFail('Koopa brake did not reach supported idle')end
 elseif route.mode=='koopa-stand-A' then
  route.pad={'a'}
  if s.source_action==3 then
   p.admission={state=s,Main=admitted,frame=frame}
   routeMode('koopa-flight',{'right'})
  elseif admitted-route.changed>36 then routeFail('Standing A did not admit original action3')end
 elseif route.mode=='koopa-flight' then
  route.pad={'right'}
  p.minimum_y=math.min(p.minimum_y,s.native_y)
  if p.actor and x>=1705 and s.native_y<=176 and support and s.source_action~=3 then
   local a=groupActor(p.actor.actor.slot)
   if a.flag==0 or a.id~=0 or a.state&32~=0 or a.x+12<x+2 then
    if p.minimum_y>=176 then routeFail('Standing A lacks an actual airborne interval')end
    p.clear={state=s,actor=a,Main=admitted,frame=frame}
    routeMode('approach',{'right'})
   end
  end
  if not p.clear and admitted-route.changed>118 then routeFail('Standing A did not reach supported ground beyond the live Koopa')end
 end
 return true
end

'''


def controller():
    old = (NATIVE / 'controller.lua').read_text(encoding='utf-8')
    anchor = 'local function fullTick(finish)'
    source = once(old, anchor, CONTROL + anchor)
    after = ' if postPitTick(s,o,support) then return end'
    source = once(source, after, after + '\n if koopaStanding(s,o,support) then return end')
    check = 'or not route.second_pit or not route.second_pit.far_ground or not postPit.clear then'
    source = once(source, check, check.removesuffix(' then') +
                  '\n      or not route.koopa_standing or not route.koopa_standing.clear then')
    assert 'emu.write(' not in source and source.count(CANDIDATE) == 1
    sys.path.insert(0, str(R / 'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(source)
    return source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve()
    assert out == OUT and not out.exists(), out
    direct = checked(PINS)
    ready = read(NATIVE / 'ready.json')
    prior = checked(ready['bindings'])
    old, binding, post, diag = (read(NATIVE / 'capture' / name) for name in (
        'full11.json', 'binding.json', 'post-pit-goombas.json', 'prince-diagnostic.json'))
    assert sha(ROM) == ready['ROM_sha256'] == old['ROM_sha256'] == binding['ROM_sha256'] == CANDIDATE
    assert binding['ready_sha256'] == PINS[NATIVE / 'ready.json'] and binding['exit_code'] != 0
    assert post['passed'] and not old['passed'] and not ready['emulated_writes']
    assert (old['admitted'], old['state']['world_x'], old['HP']) == (3545, 1678, 0)
    hit, = diag['first_pipe_route']['precontacts']
    assert (hit['Main'], hit['native_enemy']['id'], hit['native_enemy']['x'], hit['native_DY']) == (3545, 0, 1684, 0)
    prepare(out, ROM, controller(), {Path(__file__), *direct, *prior}, expected=CANDIDATE,
            timeout=ready['timeout'], allow_interactive=ready['allow_interactive'], rom_symbols=SYMBOLS,
            scope=ready['scope'] + ' Scoped grounded standing A at the first post-pit green Koopa. '
            'Require actual action3, native airborne interval, live actor and unchanged HP on supported far side.')
    assert (out / 'run.py').read_bytes() == (NATIVE / 'run.py').read_bytes()
    assert {path.name for path in out.iterdir()} == {'ready.json', 'controller.lua', 'run.py'}

if __name__ == '__main__':
    main()
