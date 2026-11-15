"""Separate actual-Goomba-phase successor; frozen91535 navigation is retained."""
from hashlib import sha256
import argparse,json
from unittest.mock import patch
import replay_prince_body_four_caps_1114 as Frozen
from check_ff_stdout_controller_source_1110 import LuaRuntime

PIN=Frozen.PIN
FROZEN_SOURCE_SHA='9e7d37e120445c92b1d4863beda99e738dc24079f3b6b6856bb6cf7f8d16bbb9'
LUA_PINS={True:'68020fd28ee6672e5ba9372ad2f48740b5f4b5be64ce8e3718788f5cd3d1c6c9',
          'partial':'5d8f72dfba22c666430bb302927fec38419bd2d1238e613a8ea19d4586c8aa09'}


def lua(value):
    if isinstance(value,dict):return '{'+','.join('['+lua(k)+']='+lua(v)for k,v in sorted(value.items()))+'}'
    if isinstance(value,str):return json.dumps(value)
    return str(value).lower()


def controller(raw,*,wait=True):
    assert isinstance(wait,bool)or wait=='partial'
    assert sha256(open(Frozen.__file__,'rb').read()).hexdigest()==FROZEN_SOURCE_SHA
    text=Frozen.controller(raw)
    def change(old,new):
        nonlocal text
        assert text.count(old)==1,old;text=text.replace(old,new,1)
    variant="local variant = tonumber(os.getenv('SMB_TEST_VARIANT') or '0')"
    change(variant,variant+"\nassert(variant==3,'Explicit Prince four-cap phase replay')")
    if wait=='partial':
        change("          switch('third-running-approach',1)","          switch('third-partial-wait',0)")
        change("  if progress=='third-running-approach' then", """  if progress=='third-partial-wait' then
    local left,right=capFeet(s,736,144)
    assert((left or right) and idle(s),'Real third-cap support throughout safe phase wait')
    local walkers=thirdWalkers()
    if #walkers==2 and walkers[1].direction==2 and walkers[2].direction==2 and walkers[1].x<=848 and walkers[2].x<=848 then
      switch('third-running-approach',1,walkers)
    end
  elseif progress=='third-running-approach' then""")
    elif wait:
        change("          switch('third-running-approach',1)","          switch('third-park',65)")
        change("      switch('third-standing-jump',129,walkers)","      switch('third-running-approach',1,walkers)")
    W=Frozen.Earned.Frozen.W;b=W.Symbols.bundle()
    ram={name:W.address(b,name)for name in('Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_PageLoc',
        'Enemy_Y_Position','Enemy_Y_HighPos','Enemy_MovingDir','PlayerStatus','StarInvincibleTimer')}
    observer=r'''
local fourthActorRam=@RAM@
local fourthActorTrace={samples={},phase_wait=@WAIT@}
late.fourth_actor_trace=fourthActorTrace
local function fourthActorSample(tag,value)
  local rows=fourthActorTrace.samples
  if #rows>=48 then return end
  local s=state();s.source_x=source(0x60f)+256*source(0x610)
  s.sword=source(0x6ee);s.power=read(fourthActorRam.PlayerStatus);s.star=read(fourthActorRam.StarInvincibleTimer)
  local actors={}
  for slot=0,5 do
    local flag=read(fourthActorRam.Enemy_Flag+slot)
    if flag~=0 then actors[#actors+1]={slot=slot,flag=flag,id=read(fourthActorRam.Enemy_ID+slot),state=read(fourthActorRam.Enemy_State+slot),
      x=read(fourthActorRam.Enemy_X_Position+slot)+256*read(fourthActorRam.Enemy_PageLoc+slot),y=read(fourthActorRam.Enemy_Y_Position+slot),
      high=read(fourthActorRam.Enemy_Y_HighPos+slot),direction=read(fourthActorRam.Enemy_MovingDir+slot)}end
  end
  local cpu=emu.getState()
  rows[#rows+1]={tag=tag,state=s,actors=actors,value=value,PC=cpu['cpu.pc'],A=cpu['cpu.a'],X=cpu['cpu.x'],Y=cpu['cpu.y'],P=cpu['cpu.ps'],SP=cpu['cpu.sp']}
end
emu.addMemoryCallback(guarded(function(_,value)
  if mapped(0xc6cf,2) and read(0x6002)==38 and value<source(0x6cf) then fourthActorSample('HP-write',value)end
end),emu.callbackType.write,0xc6cf)
'''.replace('@RAM@',lua(ram)).replace('@WAIT@',lua(wait))
    change('local function switch(nextPhase,buttons,details)\n',observer+'\nlocal function switch(nextPhase,buttons,details)\n')
    change('  progress,pad,changedAt=nextPhase,buttons,commits\n',
        "  progress,pad,changedAt=nextPhase,buttons,commits\n  if nextPhase:sub(1,6)=='third-' or nextPhase:sub(1,7)=='fourth-' then fourthActorSample(nextPhase)end\n")
    assert not any(s in text for s in('emu.write','emu.setState','io.open','pad=201','or 201'))
    LuaRuntime().compile(text)
    if wait in LUA_PINS:assert sha256(text.encode()).hexdigest()==LUA_PINS[wait]
    return text


def metadata(raw,*,wait=True):
    text=controller(raw,wait=wait)
    return dict(ROM_SHA256=PIN,Lua_SHA256=sha256(text.encode()).hexdigest(),required_native_variant=3,
        frozen91535_source_exact=True,actual_live_actor_phase_wait=wait,readonly_actor_HP_trace=True,
        ordinary_controls_only=True,qualification_pending=True,outputs=0,Mesen=False)


def controller_partial(raw):return controller(raw,wait='partial')


def metadata_partial(raw):return metadata(raw,wait='partial')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',action='store_true');parser.add_argument('--current-bt-f11',action='store_true');parser.add_argument('--partial',action='store_true');args=parser.parse_args()
    if args.current_bt_f11:import current_prince_body_research_f11_1114 as Current
    else:import current_prince_body_research_input_1114 as Current
    import check_prince_body_four_caps_1114 as Check
    from types import SimpleNamespace
    choice='partial'if args.partial else True
    proxy=SimpleNamespace(controller=lambda raw:controller(raw,wait=choice),metadata=lambda raw:metadata(raw,wait=choice))
    with patch.object(Check,'Factory',proxy):
        result=Check.run(Current.load(Frozen.Earned.ROM),source=args.source)
        print(json.dumps(result,separators=(',',':')),flush=True)
        if not result['passed']:raise SystemExit(1)
