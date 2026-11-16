"""Strict actual91dc food replay; frozen6a3 ordinary controls remain intact."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import current_battletoads_mature8_1116 as Current
import replay_battletoads_food_intercept_6a3_1116 as Previous

C,R,ROM,PIN,W,N=Current.C,Current.R,Current.ROM,Current.PIN,Current.W,Current.N
BASE_SHA='f8c48c4a1d1e1e6fc433846e69788efb7eee232fcc09a0bb9dbf41753c269fbe'
Text=Previous.Previous.Previous.Text

@lru_cache(maxsize=4)
def bindings(raw,key='rash',kind='mushroom'):
    assert C.digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    parent=Current.reference(raw);q=deepcopy(Previous.Previous.bindings(parent,key,kind));b=Current.bundle(raw)
    q.update(sha=PIN,cookie=raw[C.COOKIE:C.COOKIE+16].hex(),cache_hex=raw[C.CACHE:C.CACHE+0x1fe0].hex())
    for name,h in q['hooks'].items():
        at=C.CACHE+(h['pc']&8191)if h.get('work')else 16+h['offset']
        assert raw[at:at+len(h['bytes'])]==bytes(h['bytes']),name
        if'bank'in h:q['hooks'][name]['bank_SHA256']=C.digest(raw[16+h['bank']*8192:16+(h['bank']+1)*8192])
    q['hooks']['BtMature8']=dict(pc=0xb603,offset=3*8192+0x1603,work=True,bytes=list(raw[C.CACHE+0x1603:C.CACHE+0x160b]))
    name='NrPickupCollision';at=W.location(b,name);bank=(at-16)//8192
    q['hooks'][name]=dict(pc=W.address(b,name),offset=at-16,bytes=list(raw[at:at+8]),bank=bank,
        bank_SHA256=C.digest(raw[16+bank*8192:16+(bank+1)*8192]))
    pc,at=W.address(b,'PowerUpObjHandler'),W.location(b,'PowerUpObjHandler');code=raw[at:at+256]
    needle=bytes.fromhex('205a0190032096a44c04a5');hits=[i for i in range(len(code)-len(needle)+1)if code[i:i+len(needle)]==needle];assert len(hits)==1
    q['mature_caller_return']=pc+hits[0]+3
    return q

@lru_cache(maxsize=4)
def controller(raw,key='rash',kind='mushroom'):
    parent=Current.reference(raw);text=Previous.controller(parent,key,kind)
    old='local C='+Text.lua(Previous.Previous.bindings(parent,key,kind))+'\n';assert text.startswith(old)
    text='local C='+Text.lua(bindings(raw,key,kind))+'\n'+text[len(old):]
    marker='local age=0';assert text.count(marker)==1
    observer="""food.admission={growing=0,mature=0,returned=0,samples={}}
hook('NrPickupCollision',function()
 local sp=emu.getState()['cpu.sp']
 local pc=(read(256+((sp+4)&255))+256*read(256+((sp+5)&255))+1)&65535
 assert(pc==C.mature_caller_return,'Actual public maturity client is C-only PowerUpObjHandler caller')
 food.admission.client={pc=emu.getState()['cpu.pc'],sp=sp,caller=pc}
end)
hook('BtMature8',function()
 local cpu=emu.getState();local a=actor(cpu['cpu.x']);local mature=a.state>=128
 local q={state=state(),actor=a,pc=cpu['cpu.pc'],sp=cpu['cpu.sp']}
 assert(read(0x16c)+256*read(0x16d)==0xa045,'Only existing private service23 ingress')
 if mature then food.admission.mature=food.admission.mature+1 else food.admission.growing=food.admission.growing+1 end
 returning(function(t)
  local c=emu.getState()['cpu.ps']&1
  assert(c==(mature and active()and 1 or 0),'Actual returned maturity/active carry')
  food.admission.returned=food.admission.returned+1;q.C=c;q.return_pc=t.pc;q.return_sp=t.sp
  if#food.admission.samples<6 then food.admission.samples[#food.admission.samples+1]=q end
 end)
end)
"""
    text=text.replace(marker,observer+marker,1)
    Previous.Previous.Previous.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    return text

def metadata(raw,key='rash',kind='mushroom'):
    text=controller(raw,key,kind)
    return dict(ROM_SHA256=PIN,parent_SHA256=C.PIN,identity=key,kind=kind,controller_SHA256=C.digest(text.encode()),
        factory_SHA256=C.digest(Path(__file__).read_bytes()),composer_SHA256=C.digest(Path(C.__file__).read_bytes()),
        grant_SHA256=C.GRANT_SHA,actual_candidate_execution=True,preservation=Current.preservation(raw),
        frozen_controls_reference_SHA256=BASE_SHA,scope='Genuine mature food/native effect/1000 and25 returned original workers at actual Main return',
        gameplay_seeds=0,outputs=0,Mesen_run=False)

def family(kind='mushroom'):
    from types import SimpleNamespace
    return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,key,kind),metadata=lambda raw,key:metadata(raw,key,kind))
