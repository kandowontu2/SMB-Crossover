"""Reuse proven supported stepback at final castle stairs, without ROM edits."""
import argparse,json,sys
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha

O=R/'build/bub-menu-candidate-1102-v2'
PIN='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--identity',choices=['bub','bob'],default='bub');args=ap.parse_args()
    source=O/('native-current-landing-'+args.identity+'-full11-reachable-pit/controller.lua');text=source.read_text()
    proof=O/'castle-stairs-v38-CPU.json';q=json.loads(proof.read_text());assert q['passed']and q['ROM_sha256']==PIN
    assert {(c['identity'],c['start'])for c in q['cases']}=={(i,s)for i in[0,1]for s in['last-pipe','actual-stuck-step']}
    assert all(c['final_x']==3024 and c['final_y']==48 and c['final_native_state']==0 and c['lives']==2 and len(c['supported_retreats'])==3 for c in q['cases'])
    def once(a,b):
        nonlocal text
        assert text.count(a)==1,(a,text.count(a));text=text.replace(a,b)
    once('local full_stair_target,full_stair_y,full_stair_base,full_stair_seen=nil,nil,nil,false',
         "local full_stair_target,full_stair_y,full_stair_base,full_stair_seen=nil,nil,nil,false\nlocal full_stair_resume='approach'")
    once(" if not obstacle then full_part='march' end"," if not obstacle and full_part=='approach'then full_part='march' end")
    once("   full_part='approach';full_step=0;full_pad={right=true}\n  elseif full_step>150 then full_fail('Original staircase jump missed supported landing')end",
         "   full_part=full_stair_resume;full_step=0;full_pad={right=true}\n  elseif full_step>150 then full_fail('Original staircase jump missed supported landing')end")
    once('  q.original_PC=h.pc;q.Main_pending=BUB_OBSERVER.summary().completed_Main+1',
         "  q.original_PC=h.pc;q.Main_pending=BUB_OBSERVER.summary().completed_Main+1\n  q.route_section=full_index==8 and'castle-stairs'or'pre-pit-stairs'")
    old=""" elseif full_part=='march'then
  full_pad={right=true}
  if grounded then
   local need=not full_solid(x+12,y+32)or full_solid(x+20,y+31)
   if need and(full_state(actor+3)==0 or full_state(actor+3)==3)then full_ground_pulse=full_ground_pulse+1;full_pad.a=full_ground_pulse<=3 else full_ground_pulse=0 end
  else full_ground_pulse=0 end
 end
end"""
    new=""" elseif full_part=='march'then
  full_pad={right=true}
  if grounded then
   local side=full_solid(x+20,y+31)
   if x>=2944 and x<3040 and side and(full_state(actor+3)==0 or full_state(actor+3)==3)then
    -- Exact native1-1 staircase, allremainingsteps source-CPU qualified.
    -- Earlierpipe/lowsteps retain oldcontrols; at the highsteps a genuine
    -- supported6pxLeft avoids the original D4BB air-direction clear.
    assert(#full_stair_controls<8,'Bounded genuine staircase retreats')
    full_stair_target=x-6;full_stair_resume='march';full_part='stair-back';full_step=0;full_pad={left=true}
    full_stair_controls[#full_stair_controls+1]={Main=q.completed_Main,x=x,y=y,target=full_stair_target,
     section='castle-stairs',support=full_support_probe()}
    full_event('original-supported-castle-stair-retreat')
   else
    local need=not full_solid(x+12,y+32)or side
    if need and(full_state(actor+3)==0 or full_state(actor+3)==3)then full_ground_pulse=full_ground_pulse+1;full_pad.a=full_ground_pulse<=3 else full_ground_pulse=0 end
   end
  else full_ground_pulse=0 end
 end
end"""
    once(old,new)
    for bad in['emu.write','emu.loadSavestate','emu.reset','emu.loadState']:assert bad not in text
    for guard in["q.native_state==0 and(q.foot[2].solid or q.foot[4].solid)",
                  "full_state(actor+9)==0 and full_state(actor+1)&128~=0",'if#full_clears~=7',
                  'if full_stationary>500',"Original staircase retreat lost actual native foot support",
                  "full_solid(x+5,y+32)","full_step>150",'q.source_total_jump_starts~=full_stair_base+1']:assert guard in text
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    target=O/('native-current-landing-'+args.identity+'-full11-castle-stairs');assert not target.exists()
    prepare(target,O/'combined-current-landing.nes',text,[Path(__file__),source,proof,O/'combined-current-landing.json',O/'reachable-pit-takeoff-v36-CPU.json'],
        expected=PIN,timeout=240,allow_interactive=True,
        scope='Current9cf controller-only castle-stair correction afterv37actualall7crossings/latepipes/noinjury pass thenstationary2961. ActualcurrentAreaParserCore208columns proves authoredendstairs2896..3040/tops192..80. Bothidentities actualGameCore fromlastpipeandactualstuck2961/Y96/camera2880 qualify3supported6pxLeft/freshRightA/air/landing steps→3024/Y48/native0. Reuseexistingstair-back/air states only for highcastle2944..3040; preserve stateswhen obstaclelistends and resumemarchafterlanding. PhysicalD36Bnative0/realfoot/A/nobubblemarker, retreatsupport, exactly1sourcejump/step, bounds, all7earliercrossings/combat/noinjury/lives/active1-2/sourcehardware remainstrict. No sourcephysics/gameplaybytes/helper/resource changes.')
    ready=json.loads((target/'ready.json').read_text());assert all(sha(Path(k))==v for k,v in ready['bindings'].items())
    print(json.dumps(dict(READY=True,immutable=True,identity=args.identity,ROM_sha256=PIN,path=str(target),Lua54_syntax=True,all_bindings_verified=True)))


if __name__=='__main__':main()
