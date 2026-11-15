"""Strict optimized-ROM controllers: unchanged stage route and real cadence."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256

import compose_battletoads_native_service_1114 as C
import compose_native_floatey_score_1114 as Score
import replay_battletoads_camera_full11_1114 as Stage
import replay_battletoads_score_idle_1114 as Idle

R,ROM,W,N=Stage.R,Stage.ROM,Stage.W,Stage.N
IDENTITIES=Stage.IDENTITIES


@lru_cache(maxsize=2)
def parent(raw):return C.inverse(raw)


class Frozen:
    LuaRuntime=Stage.Frozen.LuaRuntime
    @staticmethod
    def normalize(raw):return Stage.normalize(Score.inverse(parent(raw)))


normalize=Frozen.normalize


@lru_cache(maxsize=4)
def bindings(raw,key):
    q=deepcopy(Stage.bindings(Score.inverse(parent(raw)),key));q['sha']=C.CANDIDATE
    for h in q['hooks'].values():
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes'])
        if 'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q


def replace(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new,1)


@lru_cache(maxsize=4)
def controller(raw,key='rash'):
    p=Score.inverse(parent(raw));old=Stage.controller(p,key)
    pins={'rash':'c5539dc5f7655ccb7f8f375e22e2467648094fca6b0b8d563f285583415924ac',
          'zitz':'c1bfc6d1079069c6f697d2f492163ba41d407d31fd56d8c41928b3a90d25372d'}
    assert sha256(old.encode()).hexdigest()==pins[key]
    prefix='local C='+Stage.Previous.Parent.Frozen.lua(Stage.bindings(p,key))+'\n'
    assert old.startswith(prefix)
    text='local C='+Stage.Previous.Parent.Frozen.lua(bindings(raw,key))+'\n'+old[len(prefix):]
    assert text.split('\n',1)[1]==old.split('\n',1)[1]
    Frozen.LuaRuntime().compile(text)
    return text


def cadence(raw,*,baseline=False):
    if baseline:
        assert sha256(raw).hexdigest()==Score.CANDIDATE
        Score.inverse(raw);p=raw;q=deepcopy(Idle.config(p))
    else:
        p=parent(raw);q=deepcopy(bindings(raw,'rash'));q['ram']['NmiSkipped']=Idle.config(p)['ram']['NmiSkipped']
    old=Idle.controller(p)
    assert sha256(old.encode()).hexdigest()=='b5617b7ba05020eea8d8859d39c611c9827e7a221878e6a4774b9e9d5669d359'
    prefix='local C='+Stage.Previous.Parent.Frozen.lua(Idle.config(p))+'\n';assert old.startswith(prefix)
    body=old[len(prefix):]
    body=replace(body,'local idleStart,idleEnd','local idleStart,idleEnd,walkStart,walkEnd')
    body=replace(body,"reason=='idle48-observation'","reason=='idle48-walk32-observation'")
    body=replace(body,'updates-idleStart.Main==48\n','updates-idleStart.Main==80 and walkStart and walkEnd and idleActors==0\n')
    body=replace(body,'idle_start=idleStart,idle_end=idleEnd,',
        "walk_start=walkStart,walk_end=walkEnd,walk_Main_returns=walkStart and updates-walkStart.Main or -1,walk_physical_frames=walkStart and frame-walkStart.frame or -1,walk_NMI_skips=walkStart and(r('NmiSkipped')-walkStart.skips)&255 or -1,idle_start=idleStart,idle_end=idleEnd,")
    body=replace(body,'idle_Main_returns=idleStart and updates-idleStart.Main or -1',
        'idle_Main_returns=walkStart and walkStart.Main-idleStart.Main or -1')
    body=replace(body,'idle_physical_frames=idleStart and frame-idleStart.frame or -1',
        'idle_physical_frames=walkStart and walkStart.frame-idleStart.frame or -1')
    body=replace(body,"idle_NMI_skips=idleStart and(r('NmiSkipped')-idleStart.skips)&255 or -1",
        'idle_NMI_skips=walkStart and(walkStart.skips-idleStart.skips)&255 or -1')
    body=replace(body,'Actual f11 Rash idle48 completed Main updates; no game-state writes or stage-clear claim',
        'Optimized Rash idle48 then Right32 completed Main updates; real physical cadence; no stage-clear claim')
    body=replace(body,"if updates-idleStart.Main==48 then idleEnd=state();finish('idle48-observation');return end",
        "if updates-idleStart.Main==48 then idleEnd=state();walkStart={Main=updates,frame=frame,skips=r('NmiSkipped'),source_steps=btMoves};btInput={right=true}end\n  if updates-idleStart.Main==80 then walkEnd=state();finish('idle48-walk32-observation');return end")
    body=replace(body,'then btInput={}else btInput={}end',
        'then btInput=walkStart and{right=true}or{}else btInput={}end')
    text='local C='+Stage.Previous.Parent.Frozen.lua(q)+'\n'+body
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key):
    q=bindings(raw,key)
    return dict(ROM_SHA256=C.CANDIDATE,identity=key,controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        stage_body_unchanged_from_verified_camera_route=True,normal_controls_only=True,gameplay_seeds=0,outputs=0)


def cadence_reads(raw):
    """Native-only read observer; excludes the first partial physical frame."""
    text=cadence(raw)
    text=replace(text,'local idleActors=0',
        "local idleActors=0\nlocal portRead=false\nlocal priorFrameMain=0\nlocal readCounts={idle={frames=0,missed=0,Main_histogram={}},walk={frames=0,missed=0,Main_histogram={}}}")
    text=replace(text,'walk_start=walkStart,','controller_read_observations=readCounts,walk_start=walkStart,')
    point='emu.addMemoryCallback(guard(function()\n local h=C.private_hook;'
    observe=r'''
emu.addMemoryCallback(guard(function()portRead=true end),emu.callbackType.read,0x4016)
emu.addMemoryCallback(guard(function()portRead=true end),emu.callbackType.read,0x4017)
emu.addEventCallback(guard(function()
 if idleStart and frame>idleStart.frame and not walkEnd then
  local q=readCounts[walkStart and'walk'or'idle'];q.frames=q.frames+1
  if not portRead then q.missed=q.missed+1 end
  local key=tostring(updates-priorFrameMain);q.Main_histogram[key]=(q.Main_histogram[key]or 0)+1
 end
 portRead=false;priorFrameMain=updates
end),emu.eventType.endFrame)
'''
    text=replace(text,point,observe+point)
    Frozen.LuaRuntime().compile(text)
    return text
