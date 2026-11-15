"""Ordinary16a route waiting for a fresh original careful-step decision."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import replay_prince_full_careful_step_1115 as Frozen

C,PIN=Frozen.C,Frozen.PIN
FROZEN_LUA='d330560febdb82b54f1f7a81c9593b4a333e1d51669fef7c8a632253aae9be9c'


@lru_cache(maxsize=1)
def controller(raw):
    assert sha256(Path(Frozen.__file__).read_bytes()).hexdigest()=='c6a987178ca5373afc276ea0edbc3920c82d26f93f5f3992d9a89013e3cf7f13'
    text=Frozen.controller(raw);assert sha256(text.encode()).hexdigest()==FROZEN_LUA
    def change(old,new):
        nonlocal text
        assert text.count(old)==1,old;text=text.replace(old,new,1)
    change('        attempt.steps=(attempt.steps or 0)+1',
        '        attempt.step_outcome_start=#(late.fresh_step_outcomes or {})\n        attempt.steps=(attempt.steps or 0)+1')
    change("    if s.action>=30 and s.action<=42 then switch('late-finish-brake',0)",
        "    local attempt=p.climbs[#p.climbs]\n    if #(late.fresh_step_outcomes or {})>(attempt.step_outcome_start or 0) then switch('late-finish-brake',0)")
    trace=r'''
local function latePipeControlSample(s)
 if s.x<2570 or s.x>2660 then return end
 if not late.late_pipe_geometry then
  local cells={}
  for x=2544,2672,16 do for y=128,208,16 do
   local at=0x300+((x//256)&1)*208+(y&240)-32+((x&255)//16)
   local value=tile(x,y);assert(value==read(at),'Actual native BlockBuffer tile')
   cells[#cells+1]={x=x,y=y,address=at,value=value,attribute=read(0xef36+value)}
  end end
  late.late_pipe_geometry={at=s,source='Actual native BlockBuffer and MTileAttribute, read only',cells=cells}
 end
 local rows=late.late_pipe_control or {};late.late_pipe_control=rows
 local key=progress..':'..s.x..':'..s.y..':'..s.action..':'..s.pose..':'..s.mode
 if late.late_pipe_key==key then return end
 late.late_pipe_key=key
 local box={read(0x658)+s.scroll,read(0x659),read(0x65a)+s.scroll,read(0x65b)}
 rows[#rows+1]={phase=progress,state=s,source_x=source(0x60f)+256*source(0x610),
  source_pad=source(0x40a),requested_pad=pad,body_world_at_control_sample=box,
  fresh_outcomes=#(late.fresh_step_outcomes or {})}
 if #rows>64 then table.remove(rows,17)end
end
'''
    change('local function endingTick(s)\n',trace+'\nlocal function endingTick(s)\n  latePipeControlSample(s)\n')
    names=Frozen.Map.labels(C.R/'build/prince-actor-1101-v1/contact-core.lbl');parts=C.Packet.extract(raw)[1]
    hooks=[]
    for name,kind in(('PpN_7_F631','partial'),('PpN_7_F646','full'),('PpN_7_F63B','no-step')):
        pc=names[name];length=1 if kind=='no-step'else 3
        data=parts[0][pc-0xa000:pc-0xa000+length]
        if kind=='no-step':assert data==b'\x60'
        else:assert data==bytes((0x4c,names['PpN_7_D6D8']&255,names['PpN_7_D6D8']>>8))
        hooks.append(dict(pc=pc,kind=kind,bytes=list(data)))
    observer=r'''
local freshStepHooks=@HOOKS@
for _,h in ipairs(freshStepHooks)do
 emu.addMemoryCallback(guarded(function()
  if progress~='late-finish-pipe-step' or not mapped(h.pc,3)then return end
  for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Exact reached original fresh-step decision')end
  local rows=late.fresh_step_outcomes or {};late.fresh_step_outcomes=rows
  assert(#rows<16,'Bounded fresh original decisions')
  local cpu=emu.getState()
  rows[#rows+1]={PC=h.pc,SP=cpu['cpu.sp'],A=cpu['cpu.a'],half_distance=source(0x4f),
   kind=h.kind,state=state(),completed=verifiedMainReturns,commit=commits,
   source_x=source(0x60f)+256*source(0x610)}
 end),emu.callbackType.exec,h.pc)
end
'''.replace('@HOOKS@',Frozen.Frozen.Frozen.Frozen.lua(hooks))
    text+='\n'+observer
    Frozen.Frozen.Frozen.Frozen.Full.LuaRuntime().compile(text)
    assert not any(token in text for token in('emu.write','emu.setState','io.open','saveState','loadState','pad=201','or 201'))
    return text


def metadata(raw):
    q=Frozen.metadata(raw)
    q.update(Lua_SHA256=sha256(controller(raw).encode()).hexdigest(),frozen_parent_Lua_SHA256=FROZEN_LUA,
        controls='Same ordinary careful steps, release only after a fresh original partial/full/no-step selector decision',
        authentic_native_BlockBuffer_and_bounded_control_trace=True,game_byte_changes=0,
        stale_action_field_is_not_new_admission=True)
    return q
