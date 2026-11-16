"""Owning54b full stage, exact retained v9/v7 inputs and returned source work."""
from functools import lru_cache
from pathlib import Path
import re
import current_rogue_missile_dispatch_54b_v2_1116 as J
import replay_rogue_full11_current_1114 as Retained
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,H,N,W,Frames,PIN=J.R,J.ROM,J.H,J.N,J.W,J.Frames,J.PIN
TEMPLATE=R/'tools/playthroughs/smb1_alts_full11_1114.lua'
def once(t,a,b):assert t.count(a)==1,(a,t.count(a));return t.replace(a,b,1)


@lru_cache(maxsize=1)
def pack(raw):
    b=J.bindings(raw)['bundle'];assert H(TEMPLATE.read_bytes())=='0a697d21d47bf5dc491c453858363f63d45e34bddbfd4034865c078b6560758b'
    assert H(Path(Retained.__file__).read_bytes())=='08cd3790eb43fd7885626c478b039cffa9e02bd7016f9bf75ff822422a343d0a'
    body=TEMPLATE.read_text()
    body=once(body,"r('SelectedCharacter')==0 and r('MarioVariant')==C.variant","r('SelectedCharacter')==2 and r('RdVariant')==C.variant")
    assert body.count("variant=r('MarioVariant')")==2;body=body.replace("variant=r('MarioVariant')","variant=r('RdVariant')")
    body=once(body,'MarioVariant=C.variant','RdVariant=C.variant')
    body=once(body,"power=r('PlayerStatus'),lives=r('NumberofLives')","power=r('PlayerStatus'),source_action=r('RdAction'),source_vy=r('RdVY'),source_hp=r('RdHealthLo')+256*r('RdHealthHi'),lives=r('NumberofLives')")
    body=once(body,'frame=frame,poll=polls,char=0','frame=updates,poll=updates,char=2')
    body=once(body,'lastA=lastA,grounded=',"lastA=(r('RdHeld')&128)~=0,grounded=")
    body=once(body," for i=1,C.cycle do press('select');"," press('right');press('right')\n assert(r('CrossoverMenuIndex')==2 and r('SelectedCharacter')==2 and r('RdVariant')==0,'Actual Samus slot')\n for i=1,C.cycle do press('select');")
    body=once(body,'local function finish(reason)','local rogueInput,rogueDecide={},nil\nlocal workerPending,workerHooks,workerEntered,workerReturned={},{},{},{}\nlocal groundWorkers,lastGroundWorker=0,0\nlocal function finish(reason)')
    body=once(body,' pendingReturn=nil;updates=updates+1'," pendingReturn=nil;updates=updates+1\n assert(#workerPending==0,'Actual workers returned before public Main')\n if rogueDecide then rogueDecide()end")
    body=once(body,"and nextUpdates==25 and identity()and r('NumberofLives')==2","and nextUpdates==25 and identity()and r('NumberofLives')==2 and groundWorkers>=25 and r('RdHealthLo')+r('RdHealthHi')>0")
    body=once(body,'full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false','source_entries=workerEntered,source_returns=workerReturned,grounded_original_return_snapshots=groundWorkers,full_nonshortcut1_1=not not(flag and castle and entrance),game_state_writes=false')
    body=once(body,'   nextUpdates=nextUpdates+1',"   nextUpdates=nextUpdates+1;assert(r('RdSourceAltPalette')==0,'Original donor guard admitted');local now=workerReturned.RdControlDispatch or 0;assert(now>lastGroundWorker,'New actual original work before grounded Main');lastGroundWorker=now;groundWorkers=groundWorkers+1")
    start=body.index("local stairPhase,stairAge='approach',0");end=body.index('emu.addEventCallback(guard(function()\n polls=polls+1',start)
    body=body[:start]+'''local function workerReturn(pc)
 local c=emu.getState();while #workerPending>0 do local p=workerPending[#workerPending]
  if p.pc~=pc or p.sp~=c['cpu.sp']then return end
  workerPending[#workerPending]=nil;workerReturned[p.name]=(workerReturned[p.name]or 0)+1
 end
end
for _,name in ipairs({'RdControlStep','RdControlDispatch','RdLifeMovement'})do hook(name,function()
 if not first or not identity()then return end
 local c=emu.getState();local sp=c['cpu.sp'];local ret=(emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+1)&65535
 workerEntered[name]=(workerEntered[name]or 0)+1
 workerPending[#workerPending+1]={name=name,pc=ret,sp=(sp+2)&255}
 if not workerHooks[ret]then workerHooks[ret]=true;emu.addMemoryCallback(guard(function()workerReturn(ret)end),emu.callbackType.exec,ret)end
end)end
rogueDecide=function()
 if menuDone and active()and identity()and r('LevelNumber')==0 then rogueInput=choose(context())else rogueInput={}end
end
'''+body[end:]
    body=once(body,"if menuDone then b=active()and r('LevelNumber')==0 and controls(context())or{}end",'if menuDone then b=rogueInput end')
    sources={};policy=Retained.route('rogue_dawn_11_v9.lua',sources)
    names=set(re.findall(r"\br\('([^']+)'",body+policy))|set(J.bindings(raw)['fields'])|{'RdSourceAltPalette'}
    cfg=dict(sha=PIN,key='rogue',name='ROGUE DAWN',cycle=1,variant=1,slot=2,owner=2,
        ram={name:W.address(b,name)for name in names},hooks={},rogue_tile_attributes=list(raw[W.location(b,'MTileAttribute'):W.location(b,'MTileAttribute')+256]))
    for name in('GameLoop','FlagpoleRoutine','RdControlStep','RdControlDispatch','RdLifeMovement'):
        at=W.location(b,name);cfg['hooks'][name]=dict(pc=W.address(b,name),offset=at-16,bytes=list(raw[at:at+16]))
    at=W.location(b,'IdleLoop');pc=W.address(b,'IdleLoop');call=b'\x20'+W.address(b,'GameLoop').to_bytes(2,'little')
    offsets=[i+3 for i in range(61)if raw[at+i:at+i+3]==call];assert len(offsets)==2 and offsets[0]==12
    for i,delta in enumerate(offsets):cfg['hooks']['GameLoopReturn'+str(i)]=dict(pc=pc+delta,offset=at+delta-16,bytes=list(raw[at+delta:at+delta+8]))
    text='local C='+Retained.Frozen.lua(cfg)+'\nlocal ROSTER_CONFIG={rogue_tile_attributes=C.rogue_tile_attributes}\nlocal choose=(function()\n'+policy+'\nend)()\n'+body
    LuaRuntime().compile(text)
    assert not any(v in text for v in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text,dict(owning_SHA256=PIN,controller_SHA256=H(text.encode()),factory_SHA256=H(Path(__file__).read_bytes()),
        retained_route_sources=sources,retained_v9_v7_input_policy_exact=True,previous82_controller_not_relabelled=True,
        full_nonshortcut1_1_and25_grounded_completed_public_returns=True,actual_original_worker_returns_observed=True,outputs=0,native=False)


def controller(raw):return pack(raw)[0]
def metadata(raw):return pack(raw)[1]
