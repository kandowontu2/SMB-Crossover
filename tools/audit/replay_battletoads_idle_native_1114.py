"""Readonly actual f11 Rash48-Main idle cadence observation, not a stage run."""
from copy import deepcopy
from hashlib import sha256
import replay_battletoads_camera_full11_1114 as Stage


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new,1)


def controller(raw):
    q=deepcopy(Stage.bindings(raw,'rash'))
    original=Stage.controller(raw,'rash')
    assert sha256(original.encode()).hexdigest()=='c5539dc5f7655ccb7f8f375e22e2467648094fca6b0b8d563f285583415924ac'
    prefix='local C='+Stage.Previous.Parent.Frozen.lua(Stage.bindings(raw,'rash'))+'\n'
    assert original.startswith(prefix)
    b=dict(Stage.W.Symbols.bundle(),raw=raw)
    q['ram']['NmiSkipped']=Stage.W.address(b,'NmiSkipped')
    body=original[len(prefix):]
    body=once(body,'local function finish(reason)',
        'local idleStart,idleEnd\nlocal idleActors=0\nlocal function finish(reason)')
    begin=body.index(' local ok=reason==')
    end=body.index('\n print(',begin)
    body=body[:begin]+" local ok=reason=='idle48-observation'and first and idleStart and idleEnd and identity()and active()and r('NumberofLives')==2 and updates-idleStart.Main==48\n"+body[end:]
    body=once(body,'Bt_source_steps=btMoves',
        "idle_start=idleStart,idle_end=idleEnd,idle_Main_returns=idleStart and updates-idleStart.Main or -1,idle_physical_frames=idleStart and frame-idleStart.frame or -1,idle_NMI_skips=idleStart and(r('NmiSkipped')-idleStart.skips)&255 or -1,idle_max_active_actors=idleActors,scope='Actual f11 Rash idle48 completed Main updates; no game-state writes or stage-clear claim',Bt_source_steps=btMoves")
    point=' pendingReturn=nil;updates=updates+1'
    body=once(body,point,point+"""
 if first and active()and identity()then
  idleStart=idleStart or{Main=updates,frame=frame,skips=r('NmiSkipped'),source_steps=btMoves}
  local actors=0;for i=0,5 do if r('Enemy_Flag',i)>0 then actors=actors+1 end end
  idleActors=math.max(idleActors,actors)
  if updates-idleStart.Main==48 then idleEnd=state();finish('idle48-observation');return end
 end""")
    body=once(body,"then btInput=choose(context())else btInput={}end",'then btInput={}else btInput={}end')
    text='local C='+Stage.Previous.Parent.Frozen.lua(q)+'\n'+body
    Stage.Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    return text
