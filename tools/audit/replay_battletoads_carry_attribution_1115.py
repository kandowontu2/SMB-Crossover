"""Exact ACE normal/catch-up Main, audio, draw and collision attribution."""
from copy import deepcopy
from functools import lru_cache
import replay_battletoads_carry_native_profile_1115 as Prior

C,F,Model=Prior.C,Prior.F,Prior.Model
R,ROM,W,N=Prior.R,Prior.ROM,Prior.W,Prior.N
FACTORY_SHA='92a42eb3cf1339d800a9385cccdb51e084a9109be02be16d721dca23ee1da38c'
PRIOR_LUA='2c1c0fc42610d67add057f6983d750df6ab94ee4348bf2e3e6d2bfa7a6522704'
CACHE=1989648


def load_current_image():return Prior.load_current_image()


@lru_cache(maxsize=1)
def config(raw):
    from pathlib import Path
    assert C.digest(Path(Prior.__file__).read_bytes())==FACTORY_SHA
    Prior.reference(raw);q=deepcopy(Prior.config(raw));b=Model.symbols(raw)
    points={}
    for name in('AudioUpdate','DrawAllMetasprites','MetaspriteRenderLoop',
                 'BlockBufferColli_Head','BlockBufferColli_Side'):
        pc=W.address(b,name);at=W.location(b,name)
        assert 16<=at<1048592
        points[name]=dict(pc=pc,kind='prg',offset=at-16,bytes=list(raw[at:at+8]))
    assert points['BlockBufferColli_Head']['pc']==0x9587 and points['BlockBufferColli_Side']['pc']==0x958b
    for name in('BtMovement','BtGraphics','BtDraw'):
        pc=W.address(b,name);seg=b['segs'][b['syms'][name]['seg']]
        assert seg['name'].startswith('"BT_CACHE')and 0xa000<=pc<0xc000
        at=CACHE+(pc&8191)
        points[name]=dict(pc=pc,kind='work',offset=3*8192+(pc&8191),bytes=list(raw[at:at+12]),source_file=at)
    core=W.address(b,'BtCoreStep');code=raw[CACHE+(core&8191):CACHE+(core&8191)+6]
    assert code[0]==0x8e and code[3]==0x4c
    pc=int.from_bytes(code[4:6],'little');assert pc==W.address(b,'BtPhysicsStep')and 0xa000<=pc<0xc000
    at=CACHE+(pc&8191)
    points['BtPhysicsStep_actual']=dict(pc=pc,kind='work',offset=3*8192+(pc&8191),bytes=list(raw[at:at+12]),source_file=at)
    q['attribution']=dict(points=points,source_step_JMP=dict(pc=core,bytes=list(code)),
        source_step_JMP_file=CACHE+(core&8191),maximum_rows=32,maximum_groups=32)
    return q


DECLARATIONS=r'''
local aPending,aReturnHooks,aRows,aSparse={}, {},{},{}
local aInstallReturn
local attribution={groups={},entries={},returns={},maximum_rows=32,maximum_groups=32,
 method='Actual mapped entry and stack-derived return; Main class uses observed BtCheck/BtDraw/render calls; Main spans subtract completed outer hardware ISR; NMI Audio spans subtract completed nested child ISR; named function spans overlap and must not be summed'}
local aLastEnd
local function aRow(key,row,limit)
 aSparse[key]=(aSparse[key]or 0)+1
 if aSparse[key]<=(limit or 1)and #aRows<32 then aRows[#aRows+1]=row end
end
local function aAdd(phase,name,wall,isr,extra,limit)
 assert(wall>=isr and isr>=0,'Attribution monotonic time/nested interrupt subtraction')
 local key=phase..':'..name;local g=attribution.groups[key]
 if not g then
  local count=0;for _ in pairs(attribution.groups)do count=count+1 end;assert(count<32,'Bounded attribution groups')
  g={calls=0,wall=0,interrupt=0,exclusive=0,min_wall=wall,max_wall=wall};attribution.groups[key]=g
 end
 g.calls=g.calls+1;g.wall=g.wall+wall;g.interrupt=g.interrupt+isr;g.exclusive=g.exclusive+wall-isr;g.min_wall=math.min(g.min_wall,wall);g.max_wall=math.max(g.max_wall,wall)
 local row={phase=phase,name=name,wall=wall,interrupt=isr,exclusive=wall-isr,frame=frame,Main=updates}
 for k,v in pairs(extra or{})do row[k]=v end;aRow(key,row,limit)
end
local aOldMainBegin,aOldMainEnd=pMainBegin,pMainEnd
pMainBegin=function()
 aOldMainBegin()
 if pMain then
  pMain.actual_calls={};pMain.entry_skips=pRead(C.ram.NmiSkipped);pMain.entry_disable=pRead(C.profile.NmiDisable)
  if aLastEnd then
   aAdd(pMain.phase,'BetweenMain',pClock()-aLastEnd.clock,pRoot-aLastEnd.root,{prior_frame=aLastEnd.frame,entry_frame=frame},2)
  end
 end
end
pMainEnd=function()
 if pMain then
  local q=pMain;local calls=q.actual_calls
  local key='Main/checks'..(calls.BtCheck or 0)..'/BTdraw'..(calls.BtDraw or 0)..'/render'..(calls.DrawAllMetasprites or 0)
  aAdd(q.phase,key,pClock()-q.start,pRoot-q.root,{actual_calls=calls,entry_frame=q.frame,entrySP=q.entrySP,
   entry_skips=q.entry_skips,exit_skips=pRead(C.ram.NmiSkipped),entry_disable=q.entry_disable,exit_disable=pRead(C.profile.NmiDisable)},2)
  aLastEnd={clock=pClock(),root=pRoot,frame=frame}
 end
 aOldMainEnd()
end
local aOldServiceBegin=pServiceBegin
pServiceBegin=function(name,hook)
 if pMain and #pIsrs==0 then pMain.actual_calls[name]=(pMain.actual_calls[name]or 0)+1 end
 return aOldServiceBegin(name,hook)
end
local function aReturn(pc)
 local s=emu.getState();local keep={}
 for _,q in ipairs(aPending)do
  if q.ret==pc and q.sp==s['cpu.sp']and #pIsrs==q.depth and(q.depth==0 or pIsrs[q.depth]==q.parent)and pSameMap(pc,q.retmap)then
   attribution.returns[q.context..':'..q.name]=(attribution.returns[q.context..':'..q.name]or 0)+1
   local interrupts=q.depth==0 and pRoot-q.root or q.parent.child-q.child
   aAdd(q.phase,q.context..'/'..q.name,pClock()-q.start,interrupts,{entrySP=q.entrySP,returnSP=s['cpu.sp'],returnPC=pc,
    mapped_kind=q.map.kind,mapped_offset=q.map.offset,depth=q.depth},q.name=='AudioUpdate'and 2 or 1)
  else keep[#keep+1]=q end
 end
 aPending=keep
end
local function aBegin(name)
 local phase=pPhase();if not phase or not active()or not identity()then return end
 local depth=#pIsrs;local context=depth==0 and'Main'or pIsrs[depth].name
 if name~='AudioUpdate'and(depth~=0 or not pMain)then return end
 local s=emu.getState();local sp=s['cpu.sp'];local ret=(pRead(0x100+((sp+1)&255))+256*pRead(0x100+((sp+2)&255))+1)&65535
 if pMain and depth==0 then pMain.actual_calls[name]=(pMain.actual_calls[name]or 0)+1 end
 local parent=depth>0 and pIsrs[depth]or nil
 aPending[#aPending+1]={phase=phase,name=name,context=context,start=pClock(),root=pRoot,ret=ret,sp=(sp+2)&255,retmap=pMap(ret),
  entrySP=sp,map=pMap(C.attribution.points[name].pc),depth=depth,parent=parent,child=parent and parent.child or 0}
 attribution.entries[context..':'..name]=(attribution.entries[context..':'..name]or 0)+1
 if not aReturnHooks[ret]then aReturnHooks[ret]=true;aInstallReturn(ret)end
end
'''

INSTALL=r'''
aInstallReturn=function(pc)emu.addMemoryCallback(guard(function()aReturn(pc)end),emu.callbackType.exec,pc)end
for name,h in pairs(C.attribution.points)do
 local target,point=name,h
 emu.addMemoryCallback(guard(function()
  local mapped=emu.convertAddress(point.pc);local kind=point.kind=='work'and emu.memType.nesWorkRam or emu.memType.nesPrgRom
  if not mapped or mapped.memType~=kind or mapped.address~=point.offset then return end
  for i,v in ipairs(point.bytes)do assert(pRead(point.pc+i-1)==v,'Actual mapped attribution bytes '..target)end
  aBegin(target)
 end),emu.callbackType.exec,point.pc)
end
'''


@lru_cache(maxsize=1)
def controller(raw):
    old=Prior.controller(raw);assert C.digest(old.encode())==PRIOR_LUA
    body=old.split('\n',1)[1];once=F.FrozenStage.Previous.replace
    body=once(body,Prior.SERVICES,Prior.SERVICES+DECLARATIONS)
    body=once(body,Prior.SERVICE_INSTALL,Prior.SERVICE_INSTALL+INSTALL)
    body=once(body,'nativeProfile.unacknowledged_getters=#pGetters;',
        'attribution.unacknowledged=#aPending;nativeProfile.attribution=attribution;nativeProfile.rows=aRows;nativeProfile.unacknowledged_getters=#pGetters;')
    text='local C='+F.FrozenStage.Previous.Stage.Previous.Parent.Frozen.lua(config(raw))+'\n'+body
    F.Frozen.LuaRuntime().compile(text)
    assert Prior.Prior.DECLARATIONS in body and Prior.Prior.INSTALL in body
    assert '\r'not in text and not any(x in text for x in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw):
    text=controller(raw)
    return dict(ROM_SHA256=C.digest(raw),controller_SHA256=C.digest(text.encode()),
        body_SHA256=C.digest(text.split('\n',1)[1].encode()),prior_profiler_SHA256=FACTORY_SHA,
        original_Main_ISR_getter_logic_unchanged=True,ordinary_48idle_32Right_controls_unchanged=True,
        actual_classification_by_calls_not_assumed_draw_or_check_rate=True,profile_hooks=config(raw)['attribution'],
        maximum_total_sparse_rows=32,maximum_attribution_groups=32,maximum_prior_groups=18,
        nested_named_spans_overlap=True,no_game_bytes_changed=True,outputs=0,Mesen_run=False)
