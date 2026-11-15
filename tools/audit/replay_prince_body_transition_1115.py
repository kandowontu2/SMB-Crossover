"""Strict16a ordinary controls; four caps or narrow opposed-loss endpoint."""
from functools import lru_cache
from hashlib import sha256
import json
import compose_prince_body_transition_590_1115 as C
import replay_prince_body_four_caps_wait_1114 as Four
import replay_prince_body_earned_wait_stage_1114 as Full

PIN=C.CANDIDATE


def lua(value):
    if isinstance(value,dict):return '{'+','.join('['+lua(k)+']='+lua(v)for k,v in sorted(value.items()))+'}'
    if isinstance(value,(tuple,list)):return '{'+','.join(map(lua,value))+'}'
    if isinstance(value,str):return json.dumps(value)
    return str(value).lower()


@lru_cache(maxsize=2)
def controller(raw,*,scope='four-caps'):
    assert scope in('four-caps','opposed-loss')and C.digest(raw)==PIN,'Expected exact16a candidate and explicit scope'
    parent=C.inverse(raw);current=C.Plan.Current.normalize(parent,kind='prince-graphics-590')
    historical,_=C.Plan.Body.proposal(current.reference1daca)
    if scope=='four-caps':
        text=Four.controller(historical,wait='partial');frozen_pin=Four.LUA_PINS['partial']
    else:
        text=Full.controller(historical,brick_runup=True,combat=True)
        frozen_pin='a69e9bba0d95df765efcaeddb047e5ff6838a79276237f1bc2aac398046eecef'
    assert sha256(text.encode()).hexdigest()==frozen_pin
    def change(old,new):
        nonlocal text
        assert text.count(old)==1,old;text=text.replace(old,new,1)
    change(C.digest(historical),PIN)
    oldcookie=historical[C.Packet.COOKIE:C.Packet.COOKIE+16].hex()
    change(oldcookie,raw[C.Packet.COOKIE:C.Packet.COOKIE+16].hex())
    change('local function finish(passed,reason)\n',
        "local newPacketVerified=nil\nlocal function finish(passed,reason)\n  if passed then assert(newPacketVerified,'Actual16a packet consumer readback required')end\n")
    change('    commits=commits,source_updates=sourceUpdates,source_draws=sourceDraws,',
        '    commits=commits,source_updates=sourceUpdates,source_draws=sourceDraws,new_candidate_readback=newPacketVerified,')
    parts=C.Packet.extract(raw)[1];rows=[]
    for row in C.allocation()['decoded_spans']:
        stream=row['stream'];lo,hi=row['decoded_half_open'];origin=0xa000 if stream==0 else 0xc800 if stream==1 else 0xc0b0
        rows.append(dict(bank=3 if stream==0 else 2,offset=(origin+lo)&8191,bytes=list(parts[stream][lo:hi])))
    for row in C.Plan.Current.Graphics.allocation()['decoded_envelopes']:
        stream=row['stream'];lo=row['offset'];size=row['bytes'];origin=0xa000 if stream==0 else 0xc800
        rows.append(dict(bank=3 if stream==0 else 2,offset=(origin+lo)&8191,bytes=list(parts[stream][lo:lo+size])))
    witness=r'''
local candidateStaticExtents=@ROWS@
emu.addMemoryCallback(guarded(function()
  if not mapped(0xbbc1,3)or newPacketVerified then return end
  assert(hexHeader(2)==cookie and hexHeader(3)==cookie,'Both complete16a cookies')
  local count=0
  for _,row in ipairs(candidateStaticExtents)do
    for i,value in ipairs(row.bytes)do
      assert(emu.read(row.bank*8192+row.offset+i-1,emu.memType.nesWorkRam)==value,'Actual16a static extent before first renderer')
      count=count+1
    end
  end
  local cpu=emu.getState()
  newPacketVerified={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],bytes=count,both_cookies=true,three_body_transition_and_three_graphics_extents=true}
end),emu.callbackType.exec,0xbbc1)
'''.replace('@ROWS@',lua(rows))
    text+='\n'+witness
    if scope=='opposed-loss':
        change('  if ending and s.world==0 and s.level==1 and s.engine==8 and read(verifiedHooks.ram.OperMode)==1 and read(verifiedHooks.ram.OperMode_Task)==3 then',r'''
  late.body_transition=late.body_transition or {samples={}}
  local transition=late.body_transition
  local now={active=source(0x6e0),uid=source(0x61c),sword=source(0x6ee),marker=source(0x6de),facing=source(0x615),guard_facing=source(0x623),x=s.x,y=s.y,Main=verifiedMainReturns,commit=commits}
  local previous=transition.previous
  if not transition.loss and previous and previous.active==1 and previous.sword==2 and previous.facing~=previous.guard_facing and now.active==0 and now.marker==1 then
    transition.loss={before=previous,after=now}
  end
  if transition.loss and not transition.sheath and now.sword==1 then transition.sheath=now end
  if transition.sheath and not transition.movement and math.abs(now.x-transition.sheath.x)>=8 then transition.movement=now end
  if transition.movement and now.active==1 and now.sword==2 and now.marker==0 and s.x>=1800 and s.y==176 and s.hp>0 then
    assert(late.fourth_practical_cap and s.lives==2,'Four actual caps and living opposed-loss re-admission')
    transition.readmitted=now;final=s
    finish(true,'Prince four caps and opposed sword loss, sheath, movement and re-admission; not full stage')
    return
  end
  transition.previous=now
  if ending and s.world==0 and s.level==1 and s.engine==8 and read(verifiedHooks.ram.OperMode)==1 and read(verifiedHooks.ram.OperMode_Task)==3 then''')
    assert not any(token in text for token in('emu.write','emu.setState','io.open','saveState','loadState','pad=201','or 201'))
    Full.LuaRuntime().compile(text)
    return text


def metadata(raw,*,scope='four-caps'):
    text=controller(raw,scope=scope)
    return dict(ROM_SHA256=PIN,Lua_SHA256=sha256(text.encode()).hexdigest(),required_native_variant=3,
        scope=scope,ordinary_controls_only=True,gameplay_seeds=0,read_only_first_renderer_extents=4027,
        strict590_inverse=True,equal_facing_F090_exit_open=True,full_stage_qualified=False,outputs=0,Mesen=False)
