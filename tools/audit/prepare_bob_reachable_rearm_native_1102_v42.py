"""Accept a measured supported source wall stop, retaining genuine rearm."""
import json,sys
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha

O=R/'build/bub-menu-candidate-1102-v2'
PIN='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'


def main():
    source=O/'native-current-landing-bob-full11-castle-stairs/controller.lua';text=source.read_text()
    proof=O/'bob-reachable-rearm-v41-CPU.json';p=json.loads(proof.read_text());assert p['passed']and p['ROM_sha256']==PIN
    assert {(c['source_clock'],c['mode'])for c in p['cases']}=={(c,f)for c in[147,148]for f in['face1','face2','direct-RightB']}
    assert all(c['confirmed_source_wall']['x']==647 and c['lives']==2 for c in p['cases'])
    direct=[c for c in p['cases']if c['mode']=='direct-RightB']
    assert all(c['launch']['x']==647 and c['crossed']and c['final_x']>=776 and c['final_y']==176 and c['minimum_y']==96 for c in direct)
    assert all(not c['crossed']and 721<=c['final_x']<=722 for c in p['cases']if c['mode']=='face2')
    def once(a,b):
        nonlocal text
        assert text.count(a)==1,(a,text.count(a));text=text.replace(a,b)
    once('local full_rearm_target,full_rearm_clock,full_rearm_age=nil,nil,0',
         'local full_rearm_target,full_rearm_clock,full_rearm_age=nil,nil,0\nlocal full_rearm_wall_x,full_rearm_wall_clock=nil,nil\nlocal full_rearm_wall_contacts={}')
    once('  source_shot_rearm=full_rearm_rows,source_shot_rearm_dropped=full_rearm_dropped,',
         '  source_shot_rearm=full_rearm_rows,source_shot_rearm_dropped=full_rearm_dropped,\n  source_rearm_wall_contacts=full_rearm_wall_contacts,')
    once("full_rearm_clock=full_state(0x1f);full_rearm_age=0;full_rearm_mode='rewind'",
         "full_rearm_clock=full_state(0x1f);full_rearm_age=0;full_rearm_mode='rewind';full_rearm_wall_x=nil")
    old="  if full_rearm_mode=='rewind'and x>full_rearm_target+1 then\n   full_pad={left=true}"
    new="""  local source_wall=false
  if full_rearm_mode=='rewind'and x>full_rearm_target+1 then
   local prior=obstacles[full_index-1]
   local support=full_support_probe()
   local solid,tile=full_solid(x-8,y+31)
   if prior and prior.kind=='pipe'and full_rearm_target==prior.right+4
    and x<=prior.right+7 and solid and full_state(0x301)&3==2
    and full_state(actor+8)==0 and full_state(0x301)&64==0
    and support.native_Y_high==1 and support.native_Y_speed==0 and support.source_selector==0
    and(support.native_state==0 or support.native_state==2)
    and support.foot[2].solid and support.foot[4].solid then
    local now=full_state(0x1f)
    if full_rearm_wall_x~=x then
     full_rearm_wall_x=x;full_rearm_wall_clock=now
    else
     local elapsed=(now-full_rearm_wall_clock)&255
     if elapsed>4 then full_fail('Bounded actual source wall rearm clock')end
     if elapsed>=1 then
      source_wall=true;assert(#full_rearm_wall_contacts<8,'Bounded measured source wall contacts')
      full_rearm_wall_contacts[#full_rearm_wall_contacts+1]={Main=q.completed_Main,
       target=full_rearm_target,prior_pipe_right=prior.right,elapsed_source_clocks=elapsed,
       left_probe={x=x-8,y=y+31,tile=tile,solid=solid},support=support}
      full_event('actual-supported-source-left-wall-rearm')
     end
    end
   else full_rearm_wall_x=nil end
  end
  if source_wall then
   -- Original D530 only marks the request. PlayerStep moves/facesRight
   -- before BubbleStep publishes it, so directRight+B is authentic and
   -- avoids a coalesced extraRight update pushing this takeoff too late.
   full_part='grow';full_step=0;full_start_y=y;full_min_y=y;full_ride_base=q
   full_pad={right=true,b=true};full_event('actual-source-wall-freshRightB-request-before-bubble-publication')
  elseif full_rearm_mode=='rewind'and x>full_rearm_target+1 then
   full_pad={left=true}"""
    once(old,new)
    for bad in['emu.write','emu.loadSavestate','emu.reset','emu.loadState']:assert bad not in text
    for guard in["if not full_rearm_has_support(actor)then",'if full_step>150',
                  'if full_rearm_age<1 or full_state(0x102+oy)&64==0',
                  "q.native_state==0 and(q.foot[2].solid or q.foot[4].solid)",
                  "full_state(actor+9)==0 and full_state(actor+1)&128~=0",'if#full_clears~=7',
                  'if full_stationary>500',"x>=2944 and x<3040"]:assert guard in text
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    target=O/'native-current-landing-bob-full11-source-wall';assert not target.exists()
    prepare(target,O/'combined-current-landing.nes',text,[Path(__file__),source,proof,O/'combined-current-landing.json',O/'castle-stairs-v38-CPU.json'],
        expected=PIN,timeout=240,allow_interactive=True,
        scope='Controller-only actualBobsourcewall rearm correction. Nativev39camera591 stops647 whileoldtarget644 waitsforever. Newgate onlybesidepriorpipe, nominaltarget=priorright+4, actualX<=priorright+7, original8pxleftsideprobesolid, previousLeft, healthy0/DY0/Yhigh1/bothrealnativefeet, cooldown0/Breleased and actualpositive sourceclockwithunchangedX. Then directfreshRight+B uses originalorder: D530request→PlayerStepmove/pose→BubbleSteppublish. No priorRightfacing delay; bothclockparities CPUclear64pipe fromactualwall647→far776/Y176/lives2. Face2delayed649 CPUnegative721/min133retained. AllactualBubv39fullstage-success castle/pit/stepback/combat/sourcehardware/noinjury/lives/all7crossings/active1-2 guards unchanged. No source/ROM/physics/helper/reset/timer change.')
    ready=json.loads((target/'ready.json').read_text());assert all(sha(Path(k))==v for k,v in ready['bindings'].items())
    print(json.dumps(dict(READY=True,immutable=True,identity='bob',ROM_sha256=PIN,path=str(target),Lua54_syntax=True,all_bindings_verified=True)))


if __name__=='__main__':main()
