"""Read-only mapped native getter/Main/ISR profiler for exact 7a80 and a90c."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json

import replay_battletoads_idle_funded_benchmark_1115 as B

C,F=B.C,B.F
R,ROM,W,N=F.R,F.ROM,F.W,F.N
BENCH_SHA='3bee1e34d1da8ebf737d555e996286fc36198ab78e929f9540fd58c230b224c4'


@lru_cache(maxsize=2)
def config(raw):
    assert sha256(Path(B.__file__).read_bytes()).hexdigest()==BENCH_SHA
    B.candidate(raw);q=deepcopy(B.config(raw));b=dict(C.Packet.bundle(C.inverse(raw)if sha256(raw).hexdigest()==C.CANDIDATE else raw),raw=raw)
    def point(pc,at,size):
        return dict(pc=pc,offset=at-16,bytes=list(raw[at:at+size]))
    nmi_at=W.location(b,'NonMaskableInterrupt');irq_at=W.location(b,'IrqScrollSplit')
    nmi_pc=W.address(b,'NonMaskableInterrupt');irq_pc=W.address(b,'IrqScrollSplit')
    assert int.from_bytes(raw[16+127*8192+0x1ffa:16+127*8192+0x1ffc],'little')==nmi_pc
    assert int.from_bytes(raw[16+127*8192+0x1ffe:16+128*8192],'little')==irq_pc
    done_at=W.location(b,'NmiBankCRestoreDone');done_pc=W.address(b,'NmiBankCRestoreDone')
    assert raw[done_at:done_at+6]==bytes.fromhex('68a868aa6840')
    assert raw[irq_at+67]==0x40,'Exact expanded IRQ68-byte body'
    soft_at=16+96*8192+(0xdecc&8191)
    producer=bytes.fromhex('a9bf8d1551688da17dbabd0101a8bd03019d0101bd020148a9009d0201a9b69d030168aaa98048a94248ada17d4cc580')
    assert len(producer)==48 and raw[soft_at-45:soft_at+3]==producer
    thunk_at=16+126*8192+0xc5
    assert raw[thunk_at:thunk_at+4]==bytes.fromhex('8d165160')
    guard_at=653512;guard_pc=0xb8b8
    assert raw[guard_at:guard_at+4]==(bytes.fromhex('c00cf004')if sha256(raw).hexdigest()==C.CANDIDATE else bytes.fromhex('a9b08d6d'))
    q['profile']={
        'guard':point(guard_pc,guard_at,13 if sha256(raw).hexdigest()==C.CANDIDATE else 8),
        'nmi':point(nmi_pc,nmi_at,8),'nmi_rti':point(done_pc+5,done_at+5,1),
        'irq':point(irq_pc,irq_at,8),'irq_rti':point(irq_pc+67,irq_at+67,1),
        'software_rti_producer':point(0xdecc,soft_at,3),'bankC_rts':point(0x80c8,thunk_at+3,1),
        'NmiDisable':W.address(b,'NmiDisable'),
    }
    q['profile']['software_rti_producer'].update(envelope_offset=soft_at-45-16,envelope_bytes=list(producer))
    return q


DECLARATIONS=r'''
local nativeProfile={groups={},rows={},mapped_guard_entries=0,guard_returns=0,unacknowledged_getters=0,software_RTI_dispatches=0,software_RTI_targets={},max_rows=32,method='Actual mapped entry and caller-PC/SP return; Main wall minus completed outer hardware IRQ/NMI spans matched by entrySP/status/returnPC; hardware entry7 and RTI6 included; nested IRQ not double counted; authenticated software RTI dispatch does not close hardware span'}
local pSparse,pIsrs,pRoot,pMain,pGetters,pReturnHooks={}, {},0,nil,{},{}
local pSoftware={}
local pInstallReturn
local function pClock()return assert(emu.getState()['cpu.cycleCount'],'Native CPU cycle clock')end
local function pPhase()if not idleStart then return nil end;return walkStart and'walk'or'idle'end
local function pRead(at)return emu.read(at,emu.memType.nesDebug)end
local function pMap(pc)
 local a=emu.convertAddress(pc)
 return a and{kind=a.memType,offset=a.address}or{kind=-1,offset=pc}
end
local function pSameMap(pc,m)local a=pMap(pc);return a.kind==m.kind and a.offset==m.offset end
local function pAdd(phase,name,wall,isr,extra)
 if not phase then return end
 assert(wall>=0 and isr>=0 and wall>=isr,'Native monotonic span/correct interrupt subtraction')
 local key=phase..':'..name;local g=nativeProfile.groups[key]
 if not g then g={calls=0,wall=0,interrupt=0,exclusive=0,min_wall=wall,max_wall=wall};nativeProfile.groups[key]=g end
 g.calls=g.calls+1;g.wall=g.wall+wall;g.interrupt=g.interrupt+isr;g.exclusive=g.exclusive+wall-isr;g.min_wall=math.min(g.min_wall,wall);g.max_wall=math.max(g.max_wall,wall)
 pSparse[key]=(pSparse[key]or 0)+1
 if pSparse[key]<=2 and #nativeProfile.rows<32 then
  local row={phase=phase,name=name,wall=wall,interrupt=isr,exclusive=wall-isr,frame=frame,Main=updates}
  for k,v in pairs(extra or{})do row[k]=v end
  nativeProfile.rows[#nativeProfile.rows+1]=row
 end
end
local function pMainBegin()
 local phase=pPhase();if not phase or not active()or not identity()then return end
 assert(#pIsrs==0 and not pMain,'Profile Main entry context')
 local s=emu.getState();pMain={phase=phase,start=pClock(),root=pRoot,frame=frame,entrySP=s['cpu.sp'],map=pMap(C.hooks.GameLoop.pc)}
end
local function pMainEnd()
 if not pMain then return end
 assert(#pIsrs==0,'Profile Main return outside ISR')
 local q=pMain;pMain=nil
 pAdd(q.phase,'Main',pClock()-q.start,pRoot-q.root,{entry_frame=q.frame,entrySP=q.entrySP,mapped_kind=q.map.kind,mapped_offset=q.map.offset})
end
local function pGuardBegin()
 local phase=pPhase();if not phase or not active()or not identity()or #pIsrs~=0 then return end
 local s=emu.getState();local y=s['cpu.y'];if y~=12 and y~=13 then return end
 local sp=s['cpu.sp'];local ret=(pRead(0x100+((sp+3)&255))+256*pRead(0x100+((sp+4)&255))+1)&65535
 nativeProfile.mapped_guard_entries=nativeProfile.mapped_guard_entries+1
 pGetters[#pGetters+1]={phase=phase,name='getter'..y,start=pClock(),root=pRoot,ret=ret,sp=(sp+4)&255,retmap=pMap(ret),
  entrySP=sp,A=s['cpu.a'],Y=y,savedP=pRead(0x100+((sp+2)&255)),map=pMap(C.profile.guard.pc)}
 if not pReturnHooks[ret]then pReturnHooks[ret]=true;pInstallReturn(ret)end
end
local function pGetterReturn(pc)
 if #pIsrs~=0 then return end
 local s=emu.getState();local keep={}
 for _,q in ipairs(pGetters)do
  if q.ret==pc and q.sp==s['cpu.sp']and pSameMap(pc,q.retmap)then
   nativeProfile.guard_returns=nativeProfile.guard_returns+1
   pAdd(q.phase,q.name,pClock()-q.start,pRoot-q.root,{entrySP=q.entrySP,returnSP=s['cpu.sp'],returnPC=pc,A=q.A,Y=q.Y,savedP=q.savedP,
    mapped_kind=q.map.kind,mapped_offset=q.map.offset,return_kind=q.retmap.kind,return_offset=q.retmap.offset,resultA=s['cpu.a'],resultX=s['cpu.x'],resultY=s['cpu.y'],resultP=s['cpu.ps']})
  else keep[#keep+1]=q end
 end
 pGetters=keep
end
local function pIsrEnter(kind)
 local name=kind
 if kind=='NMI'then name=pRead(C.profile.NmiDisable)>=128 and'NMI_busy'or'NMI_regular'end
 local sp=emu.getState()['cpu.sp']
 pIsrs[#pIsrs+1]={name=name,start=pClock()-7,child=0,phase=pPhase(),entrySP=sp,
  frameP=pRead(0x100+((sp+1)&255)),returnPC=pRead(0x100+((sp+2)&255))+256*pRead(0x100+((sp+3)&255))}
end
local function pSoftwareProducer()
 local sp=emu.getState()['cpu.sp']
 assert(pRead(0x100+((sp+1)&255))==0x42 and pRead(0x100+((sp+2)&255))==0x80,'Exact manufactured8042 RTS frame')
 local q={sp=(sp+2)&255,depth=#pIsrs,frameP=pRead(0x100+((sp+3)&255)),returnPC=pRead(0x100+((sp+4)&255))+256*pRead(0x100+((sp+5)&255)),mapped=false}
 pSoftware[#pSoftware+1]=q
end
local function pBankCRts()
 local q=pSoftware[#pSoftware]
 if q and #pIsrs==q.depth and emu.getState()['cpu.sp']==((q.sp-2)&255)then
  local sp=emu.getState()['cpu.sp']
  assert(pRead(0x100+((sp+1)&255))==0x42 and pRead(0x100+((sp+2)&255))==0x80,'Same software RTS transport')
  q.mapped=true
 end
end
local function pIsrExit(kind)
 local sp=emu.getState()['cpu.sp'];local status=pRead(0x100+((sp+1)&255));local ret=pRead(0x100+((sp+2)&255))+256*pRead(0x100+((sp+3)&255))
 local soft=pSoftware[#pSoftware]
 if kind=='IRQ'and soft and soft.mapped and soft.depth==#pIsrs and soft.sp==sp and soft.frameP==status and soft.returnPC==ret then
  pSoftware[#pSoftware]=nil
  if pPhase()then
   nativeProfile.software_RTI_dispatches=nativeProfile.software_RTI_dispatches+1
   local key=tostring(ret);nativeProfile.software_RTI_targets[key]=(nativeProfile.software_RTI_targets[key]or 0)+1
  end
  return
 end
 local q=pIsrs[#pIsrs];assert(q and(q.name==kind or kind=='NMI'and q.name:sub(1,3)=='NMI')and q.entrySP==sp and q.frameP==status and q.returnPC==ret,'Hardware ISR entry/SP/status/returnPC matches mapped RTI kind='..tostring(kind)..' top='..tostring(q and q.name)..' pc='..tostring(emu.getState()['cpu.pc'])..' sp='..tostring(sp))
 local wall=pClock()+6-q.start;pIsrs[#pIsrs]=nil
 pAdd(q.phase,q.name,wall,q.child,{depth=#pIsrs+1,entrySP=q.entrySP})
 if #pIsrs>0 then pIsrs[#pIsrs].child=pIsrs[#pIsrs].child+wall else pRoot=pRoot+wall end
end
'''

INSTALL=r'''
pInstallReturn=function(pc)emu.addMemoryCallback(guard(function()pGetterReturn(pc)end),emu.callbackType.exec,pc)end
local function pHook(name,fn)
 local h=C.profile[name]
 if h.envelope_bytes then for i,v in ipairs(h.envelope_bytes)do assert(emu.read(h.envelope_offset+i-1,emu.memType.nesPrgRom)==v,'Exact software dispatcher48-byte producer')end end
 for i,v in ipairs(h.bytes)do assert(emu.read(h.offset+i-1,emu.memType.nesPrgRom)==v,'Exact profiler ROM bytes '..name)end
 emu.addMemoryCallback(guard(function()
  local a=emu.convertAddress(h.pc)
  if not a or a.memType~=emu.memType.nesPrgRom or a.address~=h.offset then return end
  for i,v in ipairs(h.bytes)do assert(pRead(h.pc+i-1)==v,'Exact mapped profiler bytes '..name)end
  fn()
 end),emu.callbackType.exec,h.pc)
end
pHook('guard',pGuardBegin)
pHook('software_rti_producer',pSoftwareProducer);pHook('bankC_rts',pBankCRts)
pHook('nmi',function()pIsrEnter('NMI')end);pHook('nmi_rti',function()pIsrExit('NMI')end)
pHook('irq',function()pIsrEnter('IRQ')end);pHook('irq_rti',function()pIsrExit('IRQ')end)
'''


@lru_cache(maxsize=2)
def controller(raw):
    text=B.controller(raw);_,body=text.split('\n',1)
    once=F.Previous.replace
    body=once(body,'local function finish(reason)',DECLARATIONS+'\nlocal function finish(reason)')
    body=once(body,"print('SMB_NATIVE_RECEIPT '..json({", "nativeProfile.unacknowledged_getters=#pGetters;nativeProfile.pending_Main=not not pMain;nativeProfile.pending_ISR=#pIsrs\n print('SMB_NATIVE_RECEIPT '..json({native_cycle_profile=nativeProfile,")
    body=once(body,"hook('GameLoop',function()",INSTALL+"\nhook('GameLoop',function()\n pMainBegin()")
    body=once(body,' pendingReturn=nil;updates=updates+1',' pMainEnd()\n pendingReturn=nil;updates=updates+1')
    text='local C='+F.Previous.Stage.Previous.Parent.Frozen.lua(config(raw))+'\n'+body
    F.Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    assert '\r'not in text
    return text


def metadata(raw):
    q=config(raw)
    return dict(ROM_SHA256=sha256(raw).hexdigest(),controller_SHA256=sha256(controller(raw).encode()).hexdigest(),
        body_SHA256=sha256(controller(raw).split('\n',1)[1].encode()).hexdigest(),
        profile_hooks=q['profile'],maximum_sparse_rows=32,aggregate_groups_at_most=12,
        readonly=True,outputs=0,Mesen_run=False)


def main():
    parent=C.load_current_image();image=B.candidate(parent);original=Path.read_bytes
    def guarded(path):
        assert path.resolve()!=ROM.resolve(),'Profiler reread Downloads'
        return original(path)
    def forbid(*a,**kw):raise RuntimeError('Profiler attempted output/native')
    with patch.object(Path,'read_bytes',guarded),patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(C.Packet.Frozen.Cold.Runner.Native,'run',forbid):
        rows=[metadata(raw)for raw in(parent,image)];rejects=[]
        assert rows[0]['body_SHA256']==rows[1]['body_SHA256']
        for label,raw in(('truncated',image[:-1]),('unknown',bytes(len(parent))),('ae66',F.reference(image))):
            try:controller(raw)
            except AssertionError:rejects.append(label)
            else:raise AssertionError(('Invalid profiler input accepted',label))
        for label,raw,at in(('parent_dirty',parent,90000),('candidate_dirty',image,653512)):
            dirty=bytearray(raw);dirty[at]^=1
            try:controller(bytes(dirty))
            except AssertionError:rejects.append(label)
            else:raise AssertionError(('Dirty profiler input accepted',label))
    q=dict(controllers=rows,rejections=rejects,frozen_benchmark_file_unchanged=True,outputs=0,Mesen_run=False)
    q['source_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)


if __name__=='__main__':main()
