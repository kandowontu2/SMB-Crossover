"""Current16a full route accepting every original partial careful step."""
from functools import lru_cache
from hashlib import sha256
import current_prince_body_transition_1115 as Current
import audit_prince_sword_control_map_1115 as Map
import replay_prince_sword_chain_handoff_1115 as Frozen

C=Current.C
PIN=Frozen.PIN
FROZEN_LUA='41925405c5c42aa3d2da1a4e1fc87b698b81c6b12d42eeb8eb3d8f0ffb226c8d'


@lru_cache(maxsize=1)
def controller(raw):
    Current.normalize(raw,kind='prince-body-transition-16a')
    text=Frozen.controller(raw);assert sha256(text.encode()).hexdigest()==FROZEN_LUA
    old="    if s.action==42 or s.action==30 then switch('late-finish-brake',0)"
    new="    if s.action>=30 and s.action<=42 then switch('late-finish-brake',0)"
    assert text.count(old)==1;text=text.replace(old,new,1)
    names=Map.labels(C.R/'build/prince-actor-1101-v1/contact-core.lbl');parts=C.Packet.extract(raw)[1]
    hooks=[];setter=names['PpN_7_D6D8']
    for key in('PpN_7_F631','PpN_7_F646'):
        pc=names[key];data=parts[0][pc-0xa000:pc-0xa000+3]
        assert data==bytes((0x4c,setter&255,setter>>8))
        hooks.append(dict(pc=pc,bytes=list(data),kind='partial'if key.endswith('F631')else'full'))
    lua=Frozen.Frozen.Frozen.lua
    observer=r'''
local carefulStepHooks=@HOOKS@
for _,h in ipairs(carefulStepHooks)do
 emu.addMemoryCallback(guarded(function()
  if progress~='late-finish-pipe-step' or not mapped(h.pc,3)then return end
  for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Exact original careful-step selector')end
  local cpu=emu.getState();local action=cpu['cpu.a'];local half=source(0x4f)
  assert(action>=30 and action<=42,'Original admitted careful-step range')
  if h.kind=='partial'then assert(action==29+half and half>=1 and half<=13,'Original partial-step formula')end
  late.careful_step_admissions=late.careful_step_admissions or {}
  local rows=late.careful_step_admissions;assert(#rows<16,'Bounded original step-admission witness')
  rows[#rows+1]={PC=h.pc,SP=cpu['cpu.sp'],completed=verifiedMainReturns,commit=commits,
    kind=h.kind,action=action,half_distance=half,state=state()}
 end),emu.callbackType.exec,h.pc)
end
'''.replace('@HOOKS@',lua(hooks))
    text+='\n'+observer
    Frozen.Frozen.Frozen.Full.LuaRuntime().compile(text)
    assert not any(token in text for token in('emu.write','emu.setState','io.open','saveState','loadState'))
    return text


def metadata(raw):
    q=Frozen.metadata(raw)
    q.update(Lua_SHA256=sha256(controller(raw).encode()).hexdigest(),
        controls='Keep41925 sword handoff; accept original careful-step actions30..42, then existing neutral/idle/Up climb',
        frozen_parent_Lua_SHA256=FROZEN_LUA,read_only_original_step_selector=True,
        careful_step_primitive_receipt='e12c2126a890b715ff3edefb63faf555aef2823479488441cfa0b93f004ce2b3',
        preserved_first_BBC1_cookies_and4027bytes=True,preserved_full1_1_and25_grounded_return_endpoint=True)
    return q
