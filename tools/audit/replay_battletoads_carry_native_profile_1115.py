"""Read-only exact ACE cadence/Main/ISR and acknowledged service profiler."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
import compose_battletoads_carry_current_1115 as C
import replay_battletoads_carry_current_1115 as F
import battletoads_carry_current_model_1115 as Model
import replay_battletoads_carry_cadence_fixture_1115 as Cadence
import replay_battletoads_idle_native_profile_1115 as Prior

R,ROM,W,N=C.R,C.ROM,F.W,F.N
PINS={C:'6b87663ae0de5a1bb8b58ab73fa5313dcc8b80def75b09102fd2b66669fd604d',
 F:'872d88e4efdb0a86a7a21b91c1b59789c49f320057fbecda3b670b8c1431832c',
 Model:'fc37d90964ddbbe76b02ea2e7b66198e1b356b27959709b00a1802a986cb8217',
 Cadence:'53656a3dc35669535f4db5dc20d739db154fbaee4dab020e217b17eb6d5cee25',
 Prior:'93af79300b34f62161b5ff5a8c794cea0ab91dba8d726000542a17d9abdd892c'}


@lru_cache(maxsize=1)
def reference(raw):
    for module,pin in PINS.items():assert C.digest(Path(module.__file__).read_bytes())==pin
    assert isinstance(raw,bytes)and C.digest(raw)==C.CANDIDATE,'Expected exact owning ACE image'
    return C.reference(C.inverse(raw))


def load_current_image():
    raw=C.load_current_image();reference(raw);return raw


@lru_cache(maxsize=1)
def config(raw):
    old=reference(raw);q=deepcopy(F.observer_config(raw));b=Model.symbols(raw)
    # Only the config is rebound. The proven hardware entry/RTI pairing and
    # dynamic software-RTI transport remain the exact frozen implementation.
    q['profile']=deepcopy(Prior.config(old)['profile'])
    for name,h in q['profile'].items():
        if not isinstance(h,dict):continue
        assert raw[16+h['offset']:16+h['offset']+len(h['bytes'])]==bytes(h['bytes']),(name,h)
        if 'envelope_bytes'in h:
            assert raw[16+h['envelope_offset']:16+h['envelope_offset']+len(h['envelope_bytes'])]==bytes(h['envelope_bytes'])
    def point(name,pc,size):
        assert W.address(b,name)==pc
        at=W.location(b,name);data=raw[at:at+size]
        return dict(pc=pc,offset=at-16,bytes=list(data[:8]),envelope_offset=at-16,envelope_bytes=list(data))
    q['profile'].update(hu=point('HuResolve',0xba61,0xbacd-0xba61),
        wf=point('WfResolve',0xb799,175),btcheck=point('BtCheck',0xadc0,65))
    q['profile']['NmiDisable']=W.address(b,'NmiDisable')
    assert q['ram']['NmiSkipped']==314
    return q


SERVICES=r'''
local pServices,pServiceHooks={},{}
local pServiceInstallReturn
nativeProfile.service_entries={};nativeProfile.service_returns={}
nativeProfile.service_method='Mapped function entry to actual stack-derived caller PC/SP return; nested service spans overlap and must not be summed; completed outer hardware ISR spans subtracted identically to Main'
local function pServiceReturn(pc)
 if #pIsrs~=0 then return end
 local s=emu.getState();local keep={}
 for _,q in ipairs(pServices)do
  if q.ret==pc and q.sp==s['cpu.sp']and pSameMap(pc,q.retmap)then
   nativeProfile.service_returns[q.name]=(nativeProfile.service_returns[q.name]or 0)+1
   pAdd(q.phase,q.name,pClock()-q.start,pRoot-q.root,{entrySP=q.entrySP,returnSP=s['cpu.sp'],returnPC=pc,mapped_kind=q.map.kind,mapped_offset=q.map.offset,A=q.A,X=q.X,Y=q.Y,P=q.P})
  else keep[#keep+1]=q end
 end
 pServices=keep
end
local function pServiceBegin(name,hook)
 local phase=pPhase();if not phase or not active()or not identity()or #pIsrs~=0 then return end
 local s=emu.getState();local sp=s['cpu.sp']
 local ret=(pRead(0x100+((sp+1)&255))+256*pRead(0x100+((sp+2)&255))+1)&65535
 nativeProfile.service_entries[name]=(nativeProfile.service_entries[name]or 0)+1
 pServices[#pServices+1]={phase=phase,name=name,start=pClock(),root=pRoot,ret=ret,sp=(sp+2)&255,retmap=pMap(ret),entrySP=sp,
  A=s['cpu.a'],X=s['cpu.x'],Y=s['cpu.y'],P=s['cpu.ps'],map=pMap(C.profile[hook].pc)}
 if not pServiceHooks[ret]then pServiceHooks[ret]=true;pServiceInstallReturn(ret)end
end
'''

SERVICE_INSTALL=r'''
pServiceInstallReturn=function(pc)emu.addMemoryCallback(guard(function()pServiceReturn(pc)end),emu.callbackType.exec,pc)end
pHook('hu',function()pServiceBegin('HuResolve','hu')end)
pHook('wf',function()pServiceBegin('WfResolve','wf')end)
pHook('btcheck',function()pServiceBegin('BtCheck','btcheck')end)
'''


@lru_cache(maxsize=1)
def controller(raw):
    reference(raw);body=Cadence.controller(raw).split('\n',1)[1];once=F.FrozenStage.Previous.replace
    body=once(body,'local function finish(reason)',Prior.DECLARATIONS+SERVICES+'\nlocal function finish(reason)')
    body=once(body,"print('SMB_NATIVE_RECEIPT '..json({",
        "nativeProfile.unacknowledged_getters=#pGetters;nativeProfile.pending_Main=not not pMain;nativeProfile.pending_ISR=#pIsrs;nativeProfile.unacknowledged_services=#pServices\n print('SMB_NATIVE_RECEIPT '..json({native_cycle_profile=nativeProfile,")
    body=once(body,"hook('GameLoop',function()",Prior.INSTALL+SERVICE_INSTALL+"\nhook('GameLoop',function()\n pMainBegin()")
    body=once(body,' pendingReturn=nil;updates=updates+1',' pMainEnd()\n pendingReturn=nil;updates=updates+1')
    text='local C='+F.FrozenStage.Previous.Stage.Previous.Parent.Frozen.lua(config(raw))+'\n'+body
    F.Frozen.LuaRuntime().compile(text)
    assert Prior.DECLARATIONS in body and Prior.INSTALL in body
    assert '\r'not in text and not any(x in text for x in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw):
    text=controller(raw);q=config(raw)
    return dict(ROM_SHA256=C.digest(raw),controller_SHA256=C.digest(text.encode()),
        body_SHA256=C.digest(text.split('\n',1)[1].encode()),profile_hooks=q['profile'],
        cadence_body_SHA256=Cadence.BODY,old_Main_ISR_guard_declarations_and_hooks_byte_identical=True,
        maximum_sparse_rows=32,maximum_aggregate_groups=18,normal_controls='idle48 completed Main then Right32',
        nested_service_costs_overlap_do_not_sum=True,raw_cadence_budget_wait_and_actual_contexts_retained=True,
        readonly=True,outputs=0,Mesen_run=False)


if __name__=='__main__':
    raw=load_current_image();q=metadata(raw)
    q['source_receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
