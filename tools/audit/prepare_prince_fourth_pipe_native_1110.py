"""Stage the later Goomba birth and supported standing-A fourth-pipe route."""

import argparse
from pathlib import Path
import sys

import check_prince_fourth_pipe_1110 as Fourth
from deliver_helper_camera_render_1110 import bindings
from prepare_prince_full11_1110 import once
from prepare_selected_native_packet_v1 import prepare, sha


R,Route,Current=Fourth.R,Fourth.Route,Fourth.Current
V2=Fourth.NATIVE.parent
PROOF=R/'build/prince-fourth-pipe-1110/proof.json'
SUPPORT=PROOF.with_name('support.json')
PINS={
    V2/'ready.json':'e6902beb94089374bc3658dcae505578e7b75a68708043b667304914abf0090f',
    V2/'controller.lua':'033fb6a6920e4db45c8f14ddb493318a24f04a5746779988ffcc8163c8f8b19f',
    PROOF:'813fe771ce2410b777d5a7104fc4c9ce9bc5398d5db1c9b96167aca0d9ed8833',
    SUPPORT:'ac7d3267ec18480097ce355c18cc7a5a0184943b920cc5d838f7c35d7453e553',
    **{Fourth.NATIVE/p:h for p,h in Fourth.PINS.items()},
}


WITNESS=r'''
local function writeFourth(ok,why)
 if route.fourth_written then return end
 route.fourth_written=true
 writejson('fourth-pipe.json',{passed=ok,reason=why,ROM_sha256=Q.ROM_sha256,controller_only=true,
   emulated_writes=false,left=912,right=944,top=144,hop=route.fourth_hop,terminal=state(),
   Main=admitted,frame=frame,initial_lives=initialLives,final_lives=r('NumberofLives')})
end
'''


CONTROL=r'''
local function fourthCapHop(s,o,support)
 if not o or o.left~=912 then return false end
 if route.mode=='pipe-climb' then
  route.pad={'up'}
  local x=s.world_x
  if s.source_action==10 and s.source_frame==15 and s.source_mode==0 and s.source_A_lock==0
     and support and x+13>=912 and x<944 and 111<=s.native_y and s.native_y<=114 then
   local foot=x+13
   local cap,tile=solid(foot,144)
   if not cap then foot=x+2;cap,tile=solid(foot,144) end
   if not cap or (tile&0xfc)~=0x10 or solid(foot,143) or not route.hang
      or (route.hang.source_mode~=2 and route.hang.source_mode~=6) then
    routeFail('Fourth standing A requires a real original hang and exposed native cap')
   end
   route.on_top=s
   route.fourth_hop={support=s,original_hang=route.hang,cap_tile=tile,cap_x=foot,request_Main=admitted}
   routeMode('fourth-cap-A',{'a'})
  elseif admitted-route.changed>150 then routeFail('Original fourth climb did not settle on the native cap')end
  return true
 end
 if route.mode=='fourth-cap-A' then
  route.pad={'a'}
  if s.source_action==3 then
   route.fourth_hop.admission=s
   route.fourth_hop.admission_Main=admitted
   routeMode('fourth-cap-flight',{'right'})
  elseif admitted-route.changed>28 then routeFail('Supported fourth cap did not admit original standing A')end
  return true
 end
 if route.mode=='fourth-cap-flight' then
  route.pad={'right'}
  if admitted-route.changed>170 then routeFail('Original fourth cap hop did not land beyond the pipe')end
  return true
 end
 return false
end
'''


def controller():
    source=(V2/'controller.lua').read_text(encoding='utf-8')
    source=once(source,'if right>=803 then change', 'if right>=779 then change')
    anchor='local function routeWrite(ok,why)'
    source=once(source,anchor,WITNESS+'\n'+anchor+'\n if not route.fourth_written then writeFourth(false,why) end')
    anchor='local function fullTick(finish)'
    source=once(source,anchor,CONTROL+'\n'+anchor)
    source=once(source,"  if #route.clears~=6 or route.max_x<3100 or not route.flag or not thirdGroup.clear then",
                "  if #route.clears~=6 or route.max_x<3100 or not route.flag or not thirdGroup.clear\n"
                "      or not route.fourth_hop or not route.fourth_hop.far_ground then")
    anchor="  routeLog('supported-far-side')"
    source=once(source,anchor,"""  if o.kind=='pipe' and o.left==912 then
   local hop=route.fourth_hop
   if not hop or not hop.admission or s.native_y~=176 or not support then
    routeFail('Fourth pipe lacks actual supported standing A and far-side floor')
   end
   hop.far_ground=s
   writeFourth(true,'Actual original standing A crossed the fourth native pipe')
  end
"""+anchor)
    anchor=" if o and o.kind=='pipe' and x+13>=o.left and x<o.right"
    source=once(source,anchor," if fourthCapHop(s,o,support) then return end\n"+anchor)
    assert source.count(Route.PIN)==1 and 'emu.write(' not in source
    sys.path.insert(0,str(Route.Seam.Stage.LUA_DEPS))
    from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(source)
    return source


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not out.exists()
    for path,pin in PINS.items():
        assert sha(path)==pin,path
    assert sha(Route.ROM)==Route.PIN
    ready,old,support=(Current.read(p) for p in (V2/'ready.json',Fourth.NATIVE/'binding.json',SUPPORT))
    assert ready['ROM_sha256']==old['ROM_sha256']==support['ROM_SHA256']==Route.PIN
    assert old['ready_sha256']==PINS[V2/'ready.json'] and old['exit_code']!=0 and not ready['emulated_writes']
    assert Fourth.trace()['hit']['native_collision_slot']==1
    group=Current.read(Fourth.NATIVE/'third-goombas.json')
    brakes=[p['right'] for p in group['camera_route']['events'] if p['from']=='third-cam-brake-right']
    assert brakes==[737,749,761,773,785,797,809] and next(r for r in brakes if r>=779)==785
    for k,sha_expected in support['bindings'].items():
        assert sha(R/k)==sha_expected,k
    assert [(q['start_right'],q['goal']) for q in support['results']]==[(707,779),(748,785)]
    for case in support['results']:
        assert case['third']['terminal']=='cleared'
        fourth,=case['fourth']
        assert fourth['policy']=='standing-cap' and fourth['terminal']=='clear'
        start,=[p['row'] for p in fourth['events'] if p['transition']=='climb to cap-A']
        admit,=[p['row'] for p in fourth['events'] if p['transition']=='cap-A to cap']
        assert (start['x'],start['y'],start['frame'],start['mode'],start['native_state'])==(899,112,15,0,0)
        assert admit['action']==3 and admit['epoch']==start['epoch']+2
        assert fourth['end']['x']>=960 and fourth['end']['y']==176 and fourth['end']['lives']==2
    bindings(ready['bindings'])
    refs={Path(__file__),*PINS,*map(Path,ready['bindings']),*(R/k for k in support['bindings'])}
    prepare(out,Route.ROM,controller(),refs,expected=Route.PIN,timeout=ready['timeout'],
            scope='Earlier camera handoff delays native group birth. Fourth pipe uses original Up climb and '
                  'one standing A from exact supported cap. Keeps all third, group, fourth and full-stage witnesses.',
            allow_interactive=ready['allow_interactive'])
    assert sum(p.is_file() for p in out.rglob('*'))==3


if __name__=='__main__':
    main()
