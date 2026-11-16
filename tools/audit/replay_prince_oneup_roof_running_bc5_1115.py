"""Use original running4 and held grab from2-1's actual longer roof runway."""
from functools import lru_cache
from pathlib import Path
import current_prince_oneup_bc5_1115 as Current
import replay_prince_oneup_stage2_stair67_1115 as Previous
from replay_prince_natural_stock_40a_1115 import LuaRuntime,lua
import audit_prince_sword_control_map_1115 as Map

C,PIN=Current.C,Current.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    old=Current.reference(raw);text=Previous.controller(old,mode,jump)
    assert C.digest(text.encode())=='e96b11e20dc5a7f697eb00cce5f1e34749885db60da2b608eb13f70b3f412796'
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:110];text=text.replace(a,b,1)
    change("if idle(s)and s.action==0 then stock.jump_request=s;stockPhase('two1-platform-A',128)end",
        "if idle(s)and s.action==0 then stock.runway_ready=s;stockPhase('two1-roof-run',1)end")
    change(" elseif stock.phase=='two1-platform-A'then\n  pad=128\n  if s.action==3 then stock.jump_admission=s;stockPhase('two1-platform-flight',1)end\n  assert(age<90,'Actual original standing jump3 required')",r''' elseif stock.phase=='two1-roof-run'then
  pad=1
  assert(s.y>=111 and s.y<=114,'Original running takeoff retains actual first-roof height')
  if s.action==1 and s.mode==1 and s.pose>=6 and s.pose<=13 and s.lock==0 then
   stock.jump_request=s;stockPhase('two1-platform-A',129)
  end
  assert(age<80,'Actual original running pose6..13 before roof edge')
 elseif stock.phase=='two1-platform-A'then
  pad=129
  if s.action==4 then stock.jump_admission=s;stock.jump_minimum_y=s.y;stock.jump_poses={};stockPhase('two1-platform-flight',129)end
  assert(age<90,'Actual original running jump4 required')''')
    a=text.index(" elseif stock.phase=='two1-platform-flight'then");b=text.index(" elseif stock.phase=='coin-ledge-approach'then",a)
    text=text[:a]+r''' elseif stock.phase=='two1-platform-flight'then
  pad=s.lock~=0 and 129 or 1
  stock.jump_minimum_y=math.min(stock.jump_minimum_y,s.y)
  if #stock.jump_poses<22 and(#stock.jump_poses==0 or stock.jump_poses[#stock.jump_poses].pose~=s.pose)then stock.jump_poses[#stock.jump_poses+1]=s end
  if s.action==9 or s.action==10 or s.mode==2 or s.mode==6 then stock.stair_hang=stock.stair_hang or s end
  if stock.stair_hang then
   pad=8
   if s.action==10 and idle(s)and s.y<=98 then stock.stair_raised=s;stockPhase('two1-roof-flight-release',0)end
  elseif age>=45 and s.action~=3 and s.action~=4 then
   stock.flight_landing=s;stockPhase('two1-roof-flight-release',0)
  end
  assert(age<220,'Original running jump and requested grab are bounded')
 elseif stock.phase=='two1-roof-flight-release'then
  pad=0
  if idle(s)and s.action==0 then
   stock.flight_idle=s
   if s.y<=98 and s.x>=384 then
    stock.request=s;stock.minimum_y=s.y;stock.attempts=stock.attempts+1;stock.actual_head_pad=128;stockPhase('jump',128)
   elseif s.x>=400 and floor(s)then stock.farbank=s;stockPhase('approach',0)
   else final=s;finish(false,'Original running roof jump did not clear the actual upper stair')end
  end
  assert(age<200,'Actual original running/grab release to idle')
'''+text[b:]
    # Bounded actual caller observations distinguish failed grab admission
    # from a failed input request, without changing private or native state.
    labels=Map.labels(C.R/'build/prince-actor-1101-v1/contact-core.lbl');part=C.Packet.extract(raw)[1][0]
    hooks=[]
    for name,kind in(('PpN_7_F89B','grab-buttons'),('PpN_7_F8D5','grab-row'),('PpN_7_F90D','grab-material')):
        pc=labels[name];hooks.append(dict(pc=pc,address=3*8192+pc-0xa000,private=True,bytes=list(part[pc-0xa000:pc-0xa000+3]),kind=kind))
    observer=r'''
stock.running_grab_calls={}
for _,h in ipairs(@HOOKS@)do stockHook(h,function(cpu)
 if stock.phase~='two1-platform-flight'or #stock.running_grab_calls>=24 then return end
 local key=h.kind..':'..source(0x617)..':'..source(0x4b1)..':'..cpu['cpu.a']
 if stock.last_running_grab==key then return end;stock.last_running_grab=key
 stock.running_grab_calls[#stock.running_grab_calls+1]={kind=h.kind,PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],A=cpu['cpu.a'],P=cpu['cpu.ps']or cpu['cpu.p'],
  source_pad=source(0x40a),row_index=source(0x4b1),source_x=source(0x60f)+256*source(0x610),source_y=source(0x611),state=stockState()}
end)end
'''.replace('@HOOKS@',lua(hooks))
    text+='\n'+observer;text=Current.bind(text,raw)
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        stage='2-1',exact_level_setting36_and_all_gameplay_flags_zero=True,
        actual_original_running_gate_and_action4_then_held_grab=True,
        actual_bc5_CPU_all106changes_preserved=True,binding_reference67_only=True,
        real_birth_mature_overlap_erase_delayed_INC_cue64_and25returns_required=True,
        source_UI_vblank_limitation=True,no_gameplay_seeds=True,no_helpers_added=True,outputs=0,Mesen=False)
