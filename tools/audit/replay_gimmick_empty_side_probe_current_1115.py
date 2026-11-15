"""Read-only7a80 side-filter observer; frozen105ff ordinary controls intact."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import compose_gimmick_empty_side_1115 as C
import replay_gimmick_empty_side_current_1115 as Core
import replay_gimmick_flower_side_probe_current_1115 as Parent
import replay_smb1_alts_full11_1114 as Text

R,ROM,W,N,PIN=C.R,C.ROM,C.W,C.N,C.CURRENT_CANDIDATE
Frozen,normalize=Core.Frozen,Core.normalize
IDENTITIES=Parent.IDENTITIES
PARENT_SOURCE='e4140378d20e700fa31e97f10a3b576c1f1df9ceb43d5a19d40bdd0ba7a6e73e'
PARENT_LUA='105ffbc04e94af3f5ff41d833f372398ff52f4413099896ecb69ff454e9c43c3'


@lru_cache(maxsize=1)
def bindings(raw,key='mr_gimmick'):
    old=Core.reference590(raw);q=deepcopy(Parent.bindings(old,key));q['sha']=PIN
    for label,hook in q['hooks'].items():
        at=16+hook['offset']
        if label=='GmSideProbeEnter':
            assert hook['pc']==0xb87d;hook['bytes']=list(raw[at:at+len(hook['bytes'])])
        elif label=='GmSideProbeReturn':
            # Public Side returns through the new wrapper, not raw Body RTS.
            assert hook['pc']==0xb8d7;hook['pc']=0xb92c;hook['offset']=202882+(0xb92c-0xb872)-16
            at=16+hook['offset'];hook['bytes']=list(raw[at:at+8]);assert raw[at]==0x60
        else:assert raw[at:at+len(hook['bytes'])]==bytes(hook['bytes']),label
        if'bank'in hook:
            a=16+hook['bank']*8192;hook['bank_SHA256']=sha256(raw[a:a+8192]).hexdigest()
    at=202882+(0xb8d6-0xb872);assert raw[at-2:at+1]==bytes.fromhex('a50660')
    q['hooks']['GmRawProbeReturn']=dict(pc=0xb8d6,offset=at-16,bytes=list(raw[at:at+8]),bank=24,bank_SHA256=sha256(raw[16+24*8192:16+25*8192]).hexdigest())
    return q


OBSERVER=r'''
local gmFilterProof={marker={},solid={},raw={},calls=0}
flower.side_filter_candidate=gmFilterProof
local filterPending
hook('GmSideProbeEnter',function()
 local sp,ret=stackReturn();filterPending={sp=sp,ret=ret}
end)
hook('GmRawProbeReturn',function()
 if not filterPending then return end
 if sideWindow()and#gmFilterProof.raw<12 then
  gmFilterProof.raw[#gmFilterProof.raw+1]=sideSnapshot('new-raw-Body-RTS-before-side-filter')
 end
end)
hook('GmSideProbeReturn',function()
 if not filterPending then return end
 local p=filterPending;filterPending=nil;local sp,ret=stackReturn()
 assert(sp==p.sp and ret==p.ret,'New public Gimmick Side wrapper caller PC/SP')
 local tile=r('R3');local a=emu.getState()['cpu.a'];gmFilterProof.calls=gmFilterProof.calls+1
 assert(a==(tile==35 and 0 or tile),'Only side bounce-marker returns empty; raw R3 preserved')
 local dest=tile==35 and gmFilterProof.marker or(tile~=0 and gmFilterProof.solid or nil)
 if dest and#dest<8 then dest[#dest+1]=sideSnapshot('new-public-Side-return')end
end)
'''


@lru_cache(maxsize=1)
def controller(raw,key='mr_gimmick'):
    assert sha256(Path(Parent.__file__).read_bytes()).hexdigest()==PARENT_SOURCE
    old=Core.reference590(raw);original=Parent.controller(old,key);assert sha256(original.encode()).hexdigest()==PARENT_LUA
    prefix='local C='+Text.lua(Parent.bindings(old,key))+'\n';assert original.startswith(prefix)
    body=original[len(prefix):];marker="hook('GmMovement',function()"
    assert body.count(marker)==1;body=body.replace(marker,OBSERVER+marker,1)
    assert body.replace(OBSERVER,'',1)==original[len(prefix):]
    result='local C='+Text.lua(bindings(raw,key))+'\n'+body;Frozen.LuaRuntime().compile(result)
    assert not any(s in result for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return result


def metadata(raw,key='mr_gimmick'):
    q=Parent.metadata(Core.reference590(raw),key);q.update(ROM_SHA256=PIN,controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        parent_factory_SHA256=PARENT_SOURCE,parent_Lua_SHA256=PARENT_LUA,unchanged_ordinary_controls_and_assertions=True,
        relocated_raw_Body_RTS=0xb8d6,relocated_public_Side_RTS=0xb92c,maximum_new_rows=28,
        scope='Private7a80 read-only side-filter proof: marker raw35→A0, other actual tiles retain rawA, exact105ff controls; Flower clear remains open',outputs=0,Mesen_run=False)
    return q
