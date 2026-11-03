"""Use the authentic normal jump across the authored final stair/pit."""
import argparse,json,sys
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha

O=R/'build/bub-menu-candidate-1102-v2'
PIN='be8095fd18cbb3f1d2eac96a20c6600c16acb7e86052c04e18f0fe75b22c8d55'


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--identity',choices=['bub','bob'],default='bub');args=ap.parse_args()
    source=O/('native-landing-'+args.identity+'-full11-intercept2/controller.lua');text=source.read_text()
    proof=O/'final-stair-gap-v25-CPU.json';p=json.loads(proof.read_text())
    assert p['passed']and p['ROM_sha256']==PIN and p['pit']==[2448,2480]
    good=[c for c in p['cases']if c['foot_probe_dx']==4]
    assert len(good)==2 and all(c['takeoff']['x']==2444 and c['takeoff']['left_support']and c['crossing']and c['lives']==2 and not c['source_injury']for c in good)
    negative=O/'native-landing-bub-full11-intercept2/capture/full11.json';q=json.loads(negative.read_text())
    assert q['why']=='Source route stationary500Main without a completed crossing'and q['current_x']==2353
    assert q['index']==7 and len(q['clears'])==6 and q['source']['failures']==0
    anchor="local full_ground_pulse,full_last_engine,full_near_castle=0,8,false"
    assert text.count(anchor)==1;text=text.replace(anchor,anchor+'\nlocal full_normal_takeoff=nil')
    anchor=" if full_part=='approach'then\n  full_pad={right=true}"
    replacement=""" if full_part=='approach'then
  full_pad={right=true}
  if full_index==7 and x>=2330 then
   -- The final runup lies inside an authored rising staircase. Keep normal
   -- side-step jumps enabled there instead of growing a bubble against it.
   -- Actual Main CPU proves a fresh A with left-foot support at2444 clears
   -- the32px hole; the former12px probe launches at2436 and falls short.
   if grounded then
    local side=full_solid(x+20,y+31)
    local edge=not full_solid(x+4,y+32)
    if(side or edge)and(full_state(actor+3)==0 or full_state(actor+3)==3)then
     full_ground_pulse=full_ground_pulse+1;full_pad.a=full_ground_pulse<=3
     if edge and x>=2432 and x<2448 and full_pad.a then
      full_normal_takeoff=full_support_probe()
      if not full_normal_takeoff.foot[2].solid then full_fail('Final pit normal takeoff lacks real left-foot support')end
      full_part='normal-pit';full_step=0;full_start_y=y;full_min_y=y;full_ride_base=q
      full_event('original-normal-jump-from-supported-final-stair')
      full_events[#full_events].actual_takeoff=full_normal_takeoff
     end
    else full_ground_pulse=0 end
   else full_ground_pulse=0 end
   return
  end"""
    assert text.count(anchor)==1;text=text.replace(anchor,replacement)
    anchor=" elseif full_part=='march'then\n  full_pad={right=true}"
    replacement=""" elseif full_part=='normal-pit'then
  full_pad={right=true,a=full_step<3};full_min_y=math.min(full_min_y,y)
  if full_step>=5 and q.source_total_jump_starts<=full_ride_base.source_total_jump_starts then full_fail('Final pit missed genuine original normal jump')end
  if q.source_bubble_ride_restarts~=full_ride_base.source_bubble_ride_restarts or q.launches~=full_ride_base.launches then full_fail('Final pit normal jump was unexpectedly bubble-assisted')end
  if x>=obstacle.right+8 and grounded then
   if q.source_total_jump_starts~=full_ride_base.source_total_jump_starts+1 then full_fail('Final pit requires exactly one original normal jump')end
   full_clears[#full_clears+1]={kind=obstacle.kind,left=obstacle.left,right_exclusive=obstacle.right,
    Main=q.completed_Main,x=x,y=y,minimum_anchor_y=full_min_y,
    ability='original-normal43px-jump',actual_takeoff=full_normal_takeoff,
    original_jump_starts=1,original_support_restarts=0}
   full_event('actual-supported-final-pit-normal-jump-crossing')
   full_index=full_index+1;full_part='march';full_step=0;full_pad={right=true}
  elseif full_step>500 then full_fail('Original normal jump failed final authored pit')end
 elseif full_part=='march'then
  full_pad={right=true}"""
    assert text.count(anchor)==1;text=text.replace(anchor,replacement)
    assert "if#full_clears~=7" in text and "if full_stationary>500" in text
    for bad in['emu.write','emu.loadSavestate','emu.reset','emu.loadState']:assert bad not in text
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    target=O/('native-landing-'+args.identity+'-full11-final-stair');rom=O/'combined-landing.nes'
    prepare(target,rom,text,[Path(__file__),source,proof,O/'combined-landing.json',O/'landing-v21-proposal.json'],
        expected=PIN,timeout=240,allow_interactive=True,
        scope='Controller-only final stair/pit correction from actualv24X2353 gate stall and bothidentity actualMain CPU. First6earnedrides/naturalcombat/interception controls unchanged. At finalstairs only keep original43px side-step jumps active, and freshA at the measured4px ledge probe/real left-foot support earns exactly1originalnormaljump across2448..2480. Must land supported beyond2488 with no bubble launch/ride duringcrossing. Still requiresall7authoredcrossings/active1-2/noinjury/lives/actualsource/physicalartheaders. NoROM/helpers/install.')
    ready=json.loads((target/'ready.json').read_text());assert all(sha(Path(p))==h for p,h in ready['bindings'].items())
    print(json.dumps(dict(READY=True,identity=args.identity,ROM_sha256=PIN,path=str(target),Lua54_syntax=True,all_bindings_verified=True,native=False)))


if __name__=='__main__':main()
