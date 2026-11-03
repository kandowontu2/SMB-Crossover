"""Current captured-stair route: supported retreat, original fresh directional jump."""
import argparse,json,sys
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha

O=R/'build/bub-menu-candidate-1102-v2';PIN='be8095fd18cbb3f1d2eac96a20c6600c16acb7e86052c04e18f0fe75b22c8d55'


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--identity',choices=['bub','bob'],default='bub');args=ap.parse_args()
    source=O/('native-landing-'+args.identity+'-full11-supported-stair/controller.lua');text=source.read_text()
    proof=O/'actual-stair-route-v30-CPU.json';p=json.loads(proof.read_text());assert p['passed']and p['ROM_sha256']==PIN
    assert len(p['cases'])==4 and{(c['identity'],c['retreat_distance'])for c in p['cases']}=={(i,d)for i in[0,1]for d in[6,7]}
    assert all(c['final_x']==2502 and c['final_y']==128 and c['final_native_state']==0 and c['final_pit_original_jumps']==2 and c['lives']==2 for c in p['cases'])
    def once(a,b):
        nonlocal text
        assert text.count(a)==1,a;text=text.replace(a,b)
    once('local full_normal_actual={} ','local full_normal_actual={}\nlocal full_stair_actual,full_stair_landings,full_stair_controls={},{},{}\nlocal full_stair_target,full_stair_y,full_stair_base,full_stair_seen=nil,nil,nil,false')
    once("  if phase~='fullstage'or full_part~='normal-pit'then return end","  if phase~='fullstage'or(full_part~='normal-pit'and full_part~='stair-air')then return end")
    once("  assert(#full_normal_actual<2,'At most two measured original final-pit jumps')","  local target=full_part=='stair-air'and full_stair_actual or full_normal_actual\n  local cap=full_part=='stair-air'and 8 or 2\n  assert(#target<cap,'Bounded actual original supported stair/pit jumps')")
    once('  full_normal_actual[#full_normal_actual+1]=q','  target[#target+1]=q')
    once('  actual_normal_pit_jump_entries=full_normal_actual,','  actual_normal_pit_jump_entries=full_normal_actual,\n  actual_stair_jump_entries=full_stair_actual,actual_stair_landings=full_stair_landings,actual_stair_controls=full_stair_controls,')
    start=text.index('  if full_index==7 and x>=2330 then');end=text.index('  if grounded and x<obstacle.left-obstacle.lead-32 then',start)
    new="""  if full_index==7 and x>=2330 then
   if grounded then
    local side=full_solid(x+20,y+31)
    local edge=not full_solid(x+4,y+32)
    if side and(full_state(actor+3)==0 or full_state(actor+3)==3)then
     assert(#full_stair_controls<8,'Bounded genuine staircase retreats')
     full_stair_target=x-6;full_part='stair-back';full_step=0;full_pad={left=true}
     full_stair_controls[#full_stair_controls+1]={Main=q.completed_Main,x=x,y=y,target=full_stair_target,support=full_support_probe()}
    elseif edge and x>=2432 and x<2448 and(full_state(actor+3)==0 or full_state(actor+3)==3)then
     full_normal_takeoff=full_support_probe()
     if not full_normal_takeoff.foot[2].solid then full_fail('Final pit normal takeoff lacks real left-foot support')end
     full_part='normal-pit';full_step=0;full_start_y=y;full_min_y=y;full_ride_base=q
     full_ground_pulse=1;full_pad={right=true,a=true}
     full_event('original-normal-jump-from-supported-final-stair')
     full_events[#full_events].actual_takeoff=full_normal_takeoff
    end
   end
   return
  end
"""
    text=text[:start]+new+text[end:]
    anchor=" elseif full_part=='clear-route'then\n  -- Keep a safe grounded position"
    new=""" elseif full_part=='stair-back'then
  local support=full_support_probe()
  if not grounded or not(support.foot[2].solid or support.foot[4].solid)then full_fail('Original staircase retreat lost actual native foot support')end
  if full_step>20 then full_fail('Bounded six-pixel source staircase retreat')end
  if x>full_stair_target then full_pad={left=true}
  else
   if full_state(0x301)&128~=0 then full_fail('Original stair jump A was not released during retreat')end
   full_part='stair-air';full_step=0;full_stair_y=y;full_stair_base=q.source_total_jump_starts;full_stair_seen=false
   full_pad={right=true,a=true}
  end
 elseif full_part=='stair-air'then
  full_pad={right=true,a=full_step<3}
  if not grounded or y<full_stair_y then full_stair_seen=true end
  if full_stair_seen and grounded then
   if q.source_total_jump_starts~=full_stair_base+1 then full_fail('Stair step requires one genuine original source jump')end
   local support=full_support_probe()
   if not(support.foot[2].solid or support.foot[4].solid)then full_fail('Original stair jump missed real native supported landing')end
   assert(#full_stair_landings<8,'Bounded actual staircase landings')
   full_stair_landings[#full_stair_landings+1]=support
   full_part='approach';full_step=0;full_pad={right=true}
  elseif full_step>150 then full_fail('Original staircase jump missed supported landing')end
 elseif full_part=='clear-route'then
  -- Keep a safe grounded position"""
    once(anchor,new)
    for bad in['emu.write','emu.loadSavestate','emu.reset','emu.loadState']:assert bad not in text
    assert 'if#full_clears~=7'in text and 'if full_stationary>500'in text
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    target=O/('native-landing-'+args.identity+'-full11-stepback');rom=O/'combined-landing.nes'
    prepare(target,rom,text,[Path(__file__),source,proof,O/'stair-wall-contact-v29-CPU.json',O/'landing-v21-proposal.json',O/'combined-landing.json'],
        expected=PIN,timeout=240,allow_interactive=True,
        scope='Controller-only actualcapturedstair/sourcegrid correction. BothIDs/6or7pxretreat actualMain qualifyfouroriginal43pxsteps and final32pit2supportedjumps throughallcamera transitions; no extraability/ROMchanges. Nativecontroller retreats6px over verifiedactualnativefoot support, freshRightA thenactualair/realfootlanding for eachstep. Physicallyqualified originalD36B callbacks validateground/realfoot/A/nobubblemarker for stairandpit; finalpit max2acceptedjumps. Sixearlierbubblecrossings/combat/recovery/headersart/noinjury/lives/all7crossings/active1-2 retained.')
    ready=json.loads((target/'ready.json').read_text());assert all(sha(Path(p))==h for p,h in ready['bindings'].items())
    print(json.dumps(dict(READY=True,identity=args.identity,ROM_sha256=PIN,path=str(target),Lua54_syntax=True,all_bindings_verified=True)))


if __name__=='__main__':main()
