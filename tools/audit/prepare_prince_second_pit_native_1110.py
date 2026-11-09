"""Bind the authored second-pit run-up to the exact Prince native controller."""

import argparse
from pathlib import Path
import sys

import check_prince_second_pit_1110 as Second
from deliver_helper_camera_render_1110 import bindings
from prepare_prince_full11_1110 import once
from prepare_selected_native_packet_v1 import prepare, sha


R, First, Route = Second.R, Second.First, Second.Route
PROOF = R/'build/prince-second-pit-1110/proof.json'
PRIOR = Second.OLD/'native'
PINS = {
    PROOF:'ed0910b9daf9310c0c44e00c18d93dd0371d948b87fbc7ec313ae1133996d01e',
    PRIOR/'ready.json':'555b3506ac8497c24718ded32ea15b35abe150d23d0695bdb8b8d615d8bb4e00',
    PRIOR/'controller.lua':'fb3163cb763d23a3c81bc0b7074be2df448cffd749517bb4cdb1923453b2daaa',
}


def controller():
    text = (PRIOR/'controller.lua').read_text(encoding='utf-8')
    old = First.CONTROL
    for name,value in (('BRAKE_RIGHT',First.BRAKE_RIGHT),('BRAKE_LEFT',First.BRAKE_LEFT),
                       ('ARM',First.ARM),('HEADROOM',First.HEADROOM)):
        old = old.replace(name,str(value))
    cases = f'''
local pitTurns={{
 [1104]={{key='first_pit',tag='first-pit',label='First-pit',brake_right={First.BRAKE_RIGHT},
         brake_left={First.BRAKE_LEFT},arm={First.ARM},last_arm=1077,room={First.HEADROOM},right=1121,
         run_bound=1081,lip_bound=1095}},
 [1376]={{key='second_pit',tag='second-pit',label='Second-pit',brake_right={Second.BRAKE_RIGHT},
         brake_left={Second.BRAKE_LEFT},arm=1340,last_arm=1356,room=60,right=1407,
         run_bound=1361,lip_bound=1365}}
}}
'''
    new = once(old,"local function firstPitTurn(s,o,support)\n if not o or o.kind~='pit' or o.left~=1104 then return false end\n local p=route.first_pit",
               "local function pitTurn(s,o,support)\n if not o or o.kind~='pit' then return false end\n"
               " local spec=pitTurns[o.left]\n if not spec then return false end\n local p=route[spec.key]")
    new = once(new,'route.first_pit=p','route[spec.key]=p')
    new = once(new,"routeLog('first-pit-'..stage)","routeLog(spec.tag..'-'..stage)")
    new = once(new,f'x>={First.BRAKE_RIGHT}','x>=spec.brake_right')
    new = once(new,f'x<={First.BRAKE_LEFT}','x<=spec.brake_left')
    new = once(new,f'x>={First.ARM} and x<=1077 and right-x>={First.HEADROOM}',
               'x>=spec.arm and x<=spec.last_arm and right>=spec.right and right-x>=spec.room')
    new = once(new,"   if not solid(1088,208) or solid(1104,208) or solid(1120,208) or not solid(1136,208) then\n"
               "    routeFail('First-pit takeoff lacks the actual native two-tile gap')\n   end",
               "   if not solid(o.left-16,208) or not solid(o.right,208) then\n"
               "    routeFail(spec.label..' takeoff lacks both actual native banks')\n   end\n"
               "   for column=o.left,o.right-16,16 do\n"
               "    if solid(column,208) then routeFail(spec.label..' takeoff lacks the actual native gap')end\n   end")
    new = once(new,'x>=1081','x>=spec.run_bound')
    new = once(new,'x>=1095','x>=spec.lip_bound')
    new = new.replace("routeFail('First-pit ","routeFail(spec.label..' ")
    text = once(text,old,cases+new)
    text = once(text,'if firstPitTurn(s,o,support) then return end','if pitTurn(s,o,support) then return end')
    text = once(text,'local function routeWrite(ok,why)',r'''
local function writeSecondPit(ok,why)
 if route.second_pit_written then return end
 route.second_pit_written=true
 writejson('second-pit.json',{passed=ok,reason=why,ROM_sha256=Q.ROM_sha256,route=route.second_pit,
   controller_only=true,emulated_writes=false,state=state(),frame=frame,
   initial_lives=initialLives,final_lives=r('NumberofLives')})
end

local function routeWrite(ok,why)
 if not route.second_pit_written then writeSecondPit(false,why) end''')
    text = once(text,"  routeLog('supported-far-side')",r'''  if o.kind=='pit' and o.left==1376 then
   local p=route.second_pit
   if not p or not p.request or not p.request.support or not p.admission or p.admission.source_action~=4
       or s.native_y~=176 or s.native_y_high~=1 or not support or not solid(s.world_x+2,208) then
    routeFail('Second pit lacks actual original running A and native far-bank support')
   end
   p.far_ground=s
   writeSecondPit(true,'Actual original running A crossed the second native pit after a supported turn and run-up')
  end
  routeLog('supported-far-side')''')
    text = once(text,"   if o and o.kind=='pit' and o.left==1104 and route.first_pit then route.first_pit.admission=s end",
                "   local spec=o and o.kind=='pit' and pitTurns[o.left]\n"
                "   if spec and route[spec.key] then route[spec.key].admission=s end")
    text = once(text,"   if o and o.kind=='pit' and o.left==1104 and x+13<o.left then\n"
                "    route.first_pit.short_landing=s\n    routeFail('First-pit original jump returned to the near bank')\n   end",
                "   local spec=o and o.kind=='pit' and pitTurns[o.left]\n"
                "   if spec and x+13<o.left then\n    route[spec.key].short_landing=s\n"
                "    routeFail(spec.label..' original jump returned to the near bank')\n   end")
    text = once(text,'or not route.first_pit or not route.first_pit.far_ground then',
                'or not route.first_pit or not route.first_pit.far_ground\n'
                '      or not route.second_pit or not route.second_pit.far_ground then')
    assert text.count(Route.PIN)==1 and 'emu.write(' not in text
    sys.path.insert(0,str(Route.Seam.Stage.LUA_DEPS))
    from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(text)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and not out.exists()
    for p,digest in PINS.items():
        assert sha(p)==digest,p
    prior, proof = (First.Pit.Current.read(p) for p in (PRIOR/'ready.json',PROOF))
    assert prior['ROM_sha256']==proof['ROM_SHA256']==Route.PIN and not prior['emulated_writes']
    bindings(prior['bindings'])
    for p,digest in proof['bindings'].items():
        assert sha(R/p)==digest,p
    assert [(q['begin']['x'],q['begin']['camera_right'],q['end']['x'],q['end']['y'],q['end']['hp'],q['end']['lives'])
            for q in proof['flights'] if q['terminal']=='far-ground']==[
            (1342,1407,1441,176,4,2),(1352,1412,1441,176,4,2),(1356,1417,1441,176,4,2)]
    refs = {Path(__file__),*PINS,*map(Path,prior['bindings']),*(R/p for p in proof['bindings'])}
    prepare(out,Route.ROM,controller(),refs,expected=Route.PIN,timeout=prior['timeout'],
            allow_interactive=prior['allow_interactive'],
            scope='Original supported stop, left turn and running A at the native second pit. '
                  'Preserves the first pit and preceding pipe/group control and native witnesses.')
    assert sum(p.is_file() for p in out.rglob('*'))==3


if __name__=='__main__':
    main()
