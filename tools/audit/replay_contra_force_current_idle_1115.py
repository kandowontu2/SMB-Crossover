"""Strict currentbc5 Burns idle48/Right16 completed-Main literal-read observer."""
from functools import lru_cache
from pathlib import Path
import re
import profile_contra_force_current_costs_1115 as P
import replay_contra_force_clock_1114 as Clock

C,W,N=P.C,P.W,P.N
R,ROM,PIN=C.R,C.ROM,C.CANDIDATE
PROFILE_SHA='721d91c5220c20f71d31cb61683b05cfb3612244b4f86aff1d3c6c692d8f1a94'
CLOCK_SHA='9637e055765d51948aded6f0bad44882138949393e977679baae587552911c63'
LUA_SHA='8752e93299f3ae10e11da02b975bb5bdc067fa1e4e3d02fb42c84ec9e4e7ebe0'
BODY_SHA='6e1bababb077ad935556b7b2202f001c76c40a1119e8add52d2a9b41086e1a31'


def body():
    assert C.H(Path(Clock.__file__).read_bytes())==CLOCK_SHA
    text=Clock.TEMPLATE
    def once(old,new):
        nonlocal text
        assert text.count(old)==1,old
        text=text.replace(old,new,1)
    once('local first,pendingMain,pendingWorker','local first,pendingMain,pendingWorker,phaseTick\nlocal nativePending\nlocal nativeServices={CfNativeInput={entries=0,returns=0},CfNativeBody={entries=0,returns=0}}\nlocal portReads,priorFrameMain=0,0\nlocal literal={idle={frames=0,missed=0,port_reads=0,Main_histogram={}},right={frames=0,missed=0,port_reads=0,Main_histogram={}}}')
    once("local phaseDefs={{name='idle',frames=120},{name='right',frames=32},{name='left',frames=32}}","local phaseDefs={{name='idle',updates=48},{name='right',updates=16}}")
    once('source_jump_age=source(0x4b4)}end','source_jump_age=source(0x4b4),NMI_skips=r(\'NmiSkipped\')}end')
    once("reason=='bare-idle120-right32-left32'and#phases==3", "reason=='idle48-right16-completed-Main'and#phases==2 and not nativePending and nativeServices.CfNativeInput.entries==nativeServices.CfNativeInput.returns and nativeServices.CfNativeBody.entries==nativeServices.CfNativeBody.returns")
    once("kind='CF-bare-clock'","kind='currentbc5-CF-completed-Main-literal-reads'")
    once('phases=phases,terminal=state()',"phases=phases,literal_controller_reads=literal,native_RAM1_services=nativeServices,terminal=state(),scope='Burns idle48 then Right16 completed Main returns; actual complete physical-frame reads, no cadence acceptance assumed'")
    once(' pendingMain=nil;mainReturns=mainReturns+1',' pendingMain=nil;mainReturns=mainReturns+1\n if phaseTick then phaseTick()end')
    marker='local function empty()'
    native=r'''
local nativeReturnHooks={}
local function nativeHook(name)
 hook(C.cf.hooks[name],emu.memType.nesWorkRam,function()
  if not first then return end
  assert(not nativePending,'Previous original RAM1 CF service must return')
  local sp=emu.getState()['cpu.sp']
  local pc=emu.read(0x100+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(0x100+((sp+2)&255),emu.memType.nesDebug)+1
  local a=emu.convertAddress(pc)
  assert(a and a.memType==emu.memType.nesWorkRam and a.address//8192==2,'Actual original CF service caller is C2 transport')
  nativeServices[name].entries=nativeServices[name].entries+1
  nativePending={name=name,pc=pc,sp=(sp+2)&255,address=a.address}
  if not nativeReturnHooks[pc]then
   nativeReturnHooks[pc]=true
   emu.addMemoryCallback(guard(function()
    local p=nativePending
    if not p or p.pc~=pc or p.sp~=emu.getState()['cpu.sp']then return end
    local z=emu.convertAddress(pc)
    assert(z and z.memType==emu.memType.nesWorkRam and z.address==p.address,'Original RAM1 service exact return mapping')
    nativeServices[p.name].returns=nativeServices[p.name].returns+1;nativePending=nil
   end),emu.callbackType.exec,pc)
  end
 end)
end
nativeHook('CfNativeInput');nativeHook('CfNativeBody')
'''
    once(marker,native+'\n'+marker)
    begin=text.index('local function clockFrame()');end=text.index('local function wait(n)',begin)
    text=text[:begin]+r'''
phaseTick=function()
 if not first then return end
 assert(identity()and r('NumberofLives')==2 and r('PlayerStatus')==0 and r('StarInvincibleTimer')==0 and active(),'Bare current clock living initial1-1')
 assert(r('WorldNumber')==0 and r('LevelNumber')==0 and r('AreaType')==1,'Current bare clock stays actual1-1')
 assert(not pendingMain and not pendingWorker and not nativePending,'Completed Main includes actual CF service returns')
 cookie();empty()
 if phaseIndex==0 then
  if workerReturns>0 and r('Player_State')==0 and source(0x4d2)==1 then phaseIndex=1;began=state()end
  return
 end
 local ended=state();local def=phaseDefs[phaseIndex]
 if mainReturns-began.Main_returns==def.updates then
  phases[#phases+1]={phase=def.name,requested_Main=def.updates,physical_frames=ended.frame-began.frame,input_polls=ended.polls-began.polls,Main_entries=ended.Main_entries-began.Main_entries,Main_returns=ended.Main_returns-began.Main_returns,CF_movement_entries=ended.CF_entries-began.CF_entries,CF_movement_returns=ended.CF_returns-began.CF_returns,NMI_skips=(ended.NMI_skips-began.NMI_skips)&255,start=began,finish=ended}
  phaseIndex=phaseIndex+1;began=ended
  if phaseIndex==3 then finish('idle48-right16-completed-Main')end
 end
end
emu.addMemoryCallback(guard(function()portReads=portReads+1 end),emu.callbackType.read,0x4016)
emu.addMemoryCallback(guard(function()portReads=portReads+1 end),emu.callbackType.read,0x4017)
emu.addEventCallback(guard(function()
 if phaseIndex>0 and phaseIndex<3 and began and frame>began.frame then
  local q=literal[phaseDefs[phaseIndex].name];q.frames=q.frames+1;q.port_reads=q.port_reads+portReads
  if portReads==0 then q.missed=q.missed+1 end
  local k=tostring(mainReturns-priorFrameMain);q.Main_histogram[k]=(q.Main_histogram[k]or 0)+1
 end
 portReads=0;priorFrameMain=mainReturns
end),emu.eventType.endFrame)
''' +text[end:]
    once("'Exact421 clock ROM pin'","'Exact currentbc5 clock ROM pin'")
    once("if phaseIndex==2 then b.right=true elseif phaseIndex==3 then b.left=true end","if phaseIndex==2 then b.right=true end")
    once(' clockFrame()',' if first then cookie();empty()end')
    return text


@lru_cache(maxsize=1)
def bindings(raw,key='burns'):
    assert key=='burns'and isinstance(raw,bytes)and C.H(raw)==PIN,'Explicit currentbc5 Burns only'
    assert C.H(Path(P.__file__).read_bytes())==PROFILE_SHA
    q=P.bindings(raw);b=q['bundle'];text=body()
    names=set(re.findall(r"r\('([^']+)'",text))
    names.update(n for pair in re.findall(r"pos\('([^']+)','([^']+)'\)",text)for n in pair)
    ram={n:W.address(b,n)for n in names}
    hooks={}
    def hook(name,pc,at):
        bank=(at-16)//8192;assert 0<=bank<128
        return dict(pc=pc,offset=at-16,bank=bank,bytes=list(raw[at:at+8]),bank_SHA256=C.H(raw[16+bank*8192:16+(bank+1)*8192]))
    pc,at=W.address(b,'GameLoop'),W.location(b,'GameLoop');hooks['GameLoop']=hook('GameLoop',pc,at)
    ip,ia=W.address(b,'IdleLoop'),W.location(b,'IdleLoop');call=b'\x20'+pc.to_bytes(2,'little')
    returns=[i+3 for i in range(61)if raw[ia+i:ia+i+3]==call]
    assert len(returns)==2 and returns[0]==12
    for i,d in enumerate(returns):hooks['GameLoopReturn'+str(i)]=hook('return',ip+d,ia+d)
    private={}
    for name in('CfHostMovement','CfNativeInput','CfNativeBody'):
        p=next(p for p in q['points'].values()if p['name']==name)
        private[name]=dict(pc=p['PC'],raw=p['tag']*8192+(p['PC']&8191),bytes=p['bytes'],physical_RAM=p['tag'])
    assert private['CfNativeInput']['physical_RAM']==private['CfNativeBody']['physical_RAM']==1
    ci=W.location(b,'CfExternalCookie');cookie=raw[ci:ci+16]
    assert cookie==raw[W.location(b,'CfLoaderExpectedCookie'):W.location(b,'CfLoaderExpectedCookie')+16]
    return dict(sha=PIN,key='burns',name='BURNS',variant=0,cycle=0,slot=30,ram=ram,hooks=hooks,
        cf=dict(cookie=list(cookie),hooks=private,carrier_SHA256=q['CF_carrier_SHA256']))


@lru_cache(maxsize=1)
def controller(raw,key='burns'):
    text='local C='+Clock.Frozen.lua(bindings(raw,key))+'\n'+body()
    Clock.Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    assert C.H(body().encode())==BODY_SHA and C.H(text.encode())==LUA_SHA
    return text


def metadata(raw,key='burns'):
    q=bindings(raw,key)
    return dict(ROM_SHA256=PIN,reference67_SHA256=C.PIN,identity='burns',compiled_name='BURNS',slot=30,Select_cycles=0,
        controller_SHA256=C.H(controller(raw,key).encode()),body_SHA256=C.H(body().encode()),
        frozen_clock_source_SHA256=CLOCK_SHA,profile_bindings_source_SHA256=PROFILE_SHA,
        actual_private_input_and_body_RAM=1,actual_hooks=q['hooks'],private_hooks=q['cf']['hooks'],
        complete_cookie=q['cf']['cookie'],NmiSkipped_RAM=q['ram']['NmiSkipped'],
        ordinary_controls='idle48/Right16 completed Main returns; no A/B',
        physical4016_4017_read_frames_and_Main_histograms=True,all_dynamic_returns_PC_SP_and_mapping_acknowledged=True,
        naturally_zero_native_actors_and_12_source_shots_required=True,
        native_run=False,cadence_acceptance=False,game_state_writes=False,outputs=0)
