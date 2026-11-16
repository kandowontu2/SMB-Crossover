"""Add one original careful Left step for the measured running-jump startup."""
from functools import lru_cache
import replay_prince_oneup_roof_admission_bc5_1115 as Previous
from replay_prince_natural_stock_40a_1115 import LuaRuntime,lua
import audit_prince_sword_control_map_1115 as Map

C,PIN=Previous.C,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    text=Previous.controller(raw,mode,jump)
    assert C.digest(text.encode())=='3012f4a2cc9e348d29bb0df8106873e3f41da4d3ceca064abcb624d8c1e684fe'
    old="   stock.platform_runway=s;stockPhase('two1-platform-face-right',1)"
    new="""   if not stock.additional_runway_step then
    stock.additional_runway_step={start=s};stock.step_start=#stock.step_decisions;stockPhase('two1-platform-one-step',66)
   else
    stock.additional_runway_step.completed=s;stock.platform_runway=s;stockPhase('two1-platform-face-right',1)
   end"""
    assert text.count(old)==1;text=text.replace(old,new,1)
    labels=Map.labels(C.R/'build/prince-actor-1101-v1/contact-core.lbl');pc=labels['PpN_5_8735'];part=C.Packet.extract(raw)[1][0]
    h=dict(pc=pc,address=3*8192+pc-0xa000,private=True,bytes=list(part[pc-0xa000:pc-0xa000+3]))
    assert h['bytes']==[0x99,0x16,0xc6]
    text+='\n'+r'''
stock.running_action_writes={}
stockHook(@HOOK@,function(cpu)
 if stock.phase~='two1-platform-flight'or cpu['cpu.y']~=0 or #stock.running_action_writes>=12 then return end
 stock.running_action_writes[#stock.running_action_writes+1]={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],before=source(0x616),requested=cpu['cpu.a'],
  source_x=source(0x60f)+256*source(0x610),source_y=source(0x611),source_foot=source(0x84)+256*source(0x85),material=source(0x9f),state=stockState()}
end)
'''.replace('@HOOK@',lua(h))
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    q=Previous.metadata(raw,mode,jump);q.update(Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),
        exactly_one_additional_original_B_Left_step_before_turn_and_run=True,
        basis='Previous admitted4 becamefall7 before upward arc after roof edge during startup',
        original_action_writer_observed_read_only=True)
    return q
