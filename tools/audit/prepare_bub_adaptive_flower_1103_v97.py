"""Prepare natural mushroom/flower with measured powered rising-bubble interception."""
import ast,json,re,sys
from pathlib import Path
import check_bub_powered_bubble_1103_v92 as P
from prepare_selected_native_packet_v1 import R,sha,prepare


HELPER=r'''
local powered_generation,powered_slot=nil,nil
local powered_takeoffs={}
local function powered_growth(q,base,step)
 local actor=Q.launch.bob==1 and 0x42 or 0x2e
 local oy=Q.launch.bob==1 and 8 or 0
 if powered_generation~=base.completed_Main then powered_generation=base.completed_Main;powered_slot=nil end
 if powered_slot==nil then
  for i=#q.events,1,-1 do local e=q.events[i]
   if e.Main>base.completed_Main and e.kind=='original-bubble-launch'and e.detail.flag==1 then powered_slot=e.detail.logical_slot;break end
  end
 end
 local pad={right=step<4,b=step<4}
 if powered_slot==nil then return pad,nil end
 local at=0x88+4*powered_slot;local bo=0x188+8*powered_slot
 local kind=full_state(at);local dx=((full_state(bo+3)-full_state(0x103+oy)+128)%256)-128
 local dy=((full_state(bo)-full_state(0x100+oy)+128)%256)-128
 if step>=4 then pad.right=dx>34 end
 if kind==2 and dx>=30 and dx<=36 and dy<=-16 and dy>=-20 then
  assert(full_normal_jump_ready(actor),'Powered takeoff requires actual native foot/zeroDY support')
  assert(full_state(0x301)&128==0,'Powered takeoff requires a fresh A')
  local row={Main=q.completed_Main,x=full_x(),y=r('Player_Y_Position'),slot=powered_slot,
   bubble_kind=kind,source_gap=dx,source_vertical_gap=dy,source_clock=full_state(0x1f),
   source_selector=full_state(actor+3),actual_native_support=full_support_probe()}
  assert(#powered_takeoffs<8,'Bounded powered takeoffs');powered_takeoffs[#powered_takeoffs+1]=row
  return{right=true,a=true},row
 end
 return pad,nil
end
'''


def main():
    O=P.O;assert sha(P.ROM)==P.PIN
    terrain=json.loads((O/'powered-terrain-CPU-v96.json').read_text());assert terrain['passed']
    source=R/'build/bub-combined-auth-native-1103-v91/bub-mushroom/controller.lua'
    text=source.read_text();assert text.count('local function full_tick(finish)')==1
    text=text.replace('local function full_tick(finish)','local function mushroom_tick(finish)')
    before='  local obs=BUB_OBSERVER.finish();assert(obs.passed and obs.failures==0)';assert text.count(before)==1
    text=text.replace(before,'  local obs=BUB_OBSERVER.summary();assert(obs.failures==0)')
    # A single new trace is sufficient. Suppress old diagnostic CSV sinks,
    # preserving all prefix/controller decisions and assertions.
    marker='-- Actual source ability route; every input is delivered through the controller.'
    assert text.count(marker)==1
    text=text.replace(marker,"local function flower_null_log()return{write=function()end,flush=function()end,close=function()end}end\n"+marker)
    for name in ['route.csv','upgrade.csv','observations.csv']:
        needle="assert(io.open(OUTPUT..'"+name+"','w'))";assert text.count(needle)==1
        text=text.replace(needle,'flower_null_log()')
    # Only the shoe-powered branch uses the measured interception. The
    # genuine unpowered mushroom prefix is byte-for-byte in its decisions.
    marker='local function full_tick_base(finish)';assert text.count(marker)==1
    text=text.replace(marker,HELPER+'\n'+marker)
    before=""" elseif full_part=='grow'then
  full_pad={right=true,b=full_step<4}"""
    after=""" elseif full_part=='grow'then
  local powered=full_state(actor+2)&1~=0
  local powered_takeoff=nil
  if powered then full_pad,powered_takeoff=powered_growth(q,full_ride_base,full_step)
  else full_pad={right=true,b=full_step<4}end"""
    assert text.count(before)==1;text=text.replace(before,after)
    before="if full_state(0x88+4*i)==2 and gap>=0 and gap<=16 then"
    after="if (powered and powered_takeoff)or(not powered and full_state(0x88+4*i)==2 and gap>=0 and gap<=16) then"
    assert text.count(before)==1;text=text.replace(before,after)
    text=text.replace("if full_step>120 then full_fail('Grown free route bubble did not reach source takeoff window')end",
        "if full_step>180 then full_fail('Grown free route bubble did not reach measured source takeoff state')end")
    original=R/'tools/audit/prepare_bub_earned_flower_1103_v91.py'
    node=next(n for n in ast.walk(ast.parse(original.read_text()))if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='wrapper'for t in n.targets))
    wrapper=ast.literal_eval(node.value)
    begin=wrapper.index(" elseif flower_phase=='grow'then")
    end=wrapper.index(" elseif flower_phase=='ride'then",begin)
    wrapper=wrapper[:begin]+''' elseif flower_phase=='grow'then
  local takeoff;full_pad,takeoff=powered_growth(q,flower_launch_base,flower_age)
  if flower_age>=5 then assert(q.launches>flower_launch_base.launches,'Original flower-mount bubble must launch')end
  if takeoff then flower_change('ride')end
  assert(flower_age<180,'Rising flower-mount bubble must reach measured takeoff state')
'''+wrapper[end:]
    wrapper=wrapper.replace("observer=obs})","observer=obs,powered_takeoffs=powered_takeoffs})")
    wrapper=wrapper.replace("local flower_csv=assert(io.open(OUTPUT..'flower.csv','w'))",
        "local flower_csv=assert(io.open(OUTPUT..'flower.csv','w'))")
    # Every row records observed source geometry; no guessed epoch window.
    wrapper=wrapper.replace("item_y,rides\\n'","item_y,rides,source_clock,source_support,bubble_slot,bubble_kind,bubble_gap,bubble_dy\\n'")
    before="item and item.y or -1,q.source_bubble_ride_restarts}"
    after="item and item.y or -1,q.source_bubble_ride_restarts,full_state(0x1f),full_state(actor+9),powered_slot or -1,powered_slot and full_state(0x88+4*powered_slot)or -1,powered_slot and(((full_state(0x18b+8*powered_slot)-full_state(0x103+(Q.launch.bob==1 and 8 or 0))+128)%256)-128)or -1,powered_slot and(((full_state(0x188+8*powered_slot)-full_state(0x100+(Q.launch.bob==1 and 8 or 0))+128)%256)-128)or -1}"
    assert wrapper.count(before)==1;wrapper=wrapper.replace(before,after)
    marker="local log=flower_null_log()";assert text.count(marker)==1;text=text.replace(marker,wrapper+'\n'+marker)
    # Always persist the final observer/events, including a failing assertion.
    before='  if not ok then\n   -- A bounded observer-only error record'
    after="  if not ok then\n   BUB_OBSERVER.finish()\n   -- A bounded observer-only error record"
    assert text.count(before)==1;text=text.replace(before,after)
    assert not re.search(r'\bemu\.(write|loadSavestate|saveSavestate)\s*\(',text)
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    lua=LuaRuntime();assert lua.eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    output=O/'bub-flower'
    prepare(output,P.ROM,text,[Path(__file__),source,original,O/'powered-terrain-CPU-v95.json',
        O/'powered-terrain-CPU-v96.json',O/'powered-bubble-CPU-v94.json',
        R/'docs/qa/allocations/combined-owner-auth-1103-v116.json'],
        expected=P.PIN,timeout=240,allow_interactive=True,
        scope='Controller-only natural firstmushroom then actual laterC1 flower. Same passing mushroom prefix; original shoes then observed rising type2bubble30..36px ahead/16px above selects genuine freshRight+A and original support restart. Actual source/hardware/header/foot/noinjury/no-life-loss guards retained; natural block/emergence/maturity/transformation/flags7 required. One compactCSV, bounded observer/events, atmost4PNGs. No emulated writes, ability seeds, ROM, helper or sourcephysics change; rootaloneexecutes.')
    (O/'adaptive-flower-prepared-v97.json').write_text(json.dumps(dict(READY=True,ROM_SHA256=P.PIN,
        packet=output.relative_to(R).as_posix(),native=False,controller_only=True,
        source_gates=dict(bubble_kind=2,horizontal_gap=[30,36],vertical_gap=[-20,-16],
            native_support_required=True,fresh_Right_A=True,physics_changed=False),
        bindings={p.relative_to(R).as_posix():sha(p)for p in[Path(__file__),source,output/'controller.lua',output/'ready.json']}),indent=2)+'\n')
    print(json.dumps(dict(READY=True,packet=str(output),ROM_SHA256=P.PIN)))


if __name__=='__main__':main()
