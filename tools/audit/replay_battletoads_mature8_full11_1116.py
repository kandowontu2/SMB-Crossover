"""Actual91dc full route facade; completed original-worker endpoint."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import current_battletoads_mature8_1116 as Current
import replay_battletoads_stair_progress_1115 as Frozen
import replay_battletoads_mature8_food_1116 as Food

C,R,ROM,PIN,W,N=Current.C,Current.R,Current.ROM,Current.PIN,Current.W,Current.N
Text=Food.Text

def once(text,old,new):assert text.count(old)==1,old;return text.replace(old,new,1)

@lru_cache(maxsize=2)
def reference(raw):return Current.Previous.reference(Current.reference(raw))

@lru_cache(maxsize=2)
def bindings(raw,key='rash'):
    q=deepcopy(Frozen.bindings(reference(raw),key));q['sha']=PIN
    for name,h in q['hooks'].items():
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes']),name
        if'bank'in h:h['bank_SHA256']=C.digest(raw[16+h['bank']*8192:16+(h['bank']+1)*8192])
    q['private_hook']['bytes']=list(raw[C.CACHE+(q['private_hook']['pc']&8191):C.CACHE+(q['private_hook']['pc']&8191)+8])
    q.update(cache_hex=raw[C.CACHE:C.CACHE+0x1fe0].hex(),cookie=raw[C.COOKIE:C.COOKIE+16].hex(),constructor_pc=0xae11)
    return q

@lru_cache(maxsize=2)
def controller(raw,key='rash'):
    parent=reference(raw);text=Frozen.controller(parent,key);prefix,body=text.split('\n',1);assert prefix.startswith('local C=')
    text='local C='+Text.lua(bindings(raw,key))+'\n'+body
    old='local btMoves,btNext,btHeld,btDirty,btMin=0,0,0,false,255'
    text=once(text,old,old+'\nlocal btEntries,btReturns,btLast=0,0,0\nlocal pendingBt\nlocal btDynamic={}\nlocal readback={}')
    marker='emu.addMemoryCallback(guard(function()\n local h=C.private_hook;'
    helper="""local function btReturning(fn)
 local sp=emu.getState()['cpu.sp'];local pc=(emu.read(256+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(256+((sp+2)&255),emu.memType.nesDebug)+1)&65535
 local q={pc=pc,sp=(sp+2)&255}
 if not btDynamic[pc]then btDynamic[pc]={};emu.addMemoryCallback(guard(function()
  local sp=emu.getState()['cpu.sp'];local list=btDynamic[pc]
  for i=#list,1,-1 do local t=list[i];if t.sp==sp then table.remove(list,i);t.fn(t)end end
 end),emu.callbackType.exec,pc)end
 q.fn=fn;btDynamic[pc][#btDynamic[pc]+1]=q;return q
end
emu.addMemoryCallback(guard(function()
 local p=emu.convertAddress(C.constructor_pc)
 if readback.constructor or not p or p.memType~=emu.memType.nesWorkRam or p.address~=3*8192+(C.constructor_pc&8191)then return end
 for i=1,#C.cache_hex,2 do assert(emu.read(3*8192+(i-1)//2,emu.memType.nesWorkRam)==tonumber(C.cache_hex:sub(i,i+1),16),'Entire owning cache before first constructor')end
 for i=1,32,2 do assert(emu.read(3*8192+0x1fe0+(i-1)//2,emu.memType.nesWorkRam)==tonumber(C.cookie:sub(i,i+1),16),'Full16 owning cookie')end
 readback.constructor={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],bytes=8160,cookie=true}
end),emu.callbackType.exec,C.constructor_pc)
"""
    text=once(text,marker,helper+marker)
    old=' if first and active()and identity()then\n  assert('
    new=""" for i,v in ipairs(h.bytes)do assert(emu.read(h.pc+i-1,emu.memType.nesDebug)==v,'Current original-worker bytes')end
 assert(not pendingBt,'Previous original worker returned');btEntries=btEntries+1
 pendingBt=btReturning(function(t)pendingBt=nil;btReturns=btReturns+1 end)
 readback.first_worker=readback.first_worker or{pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp']}
 if first and active()and identity()then
  assert("""
    text=once(text,old,new)
    text=once(text,' pendingReturn=nil;updates=updates+1',' pendingReturn=nil;updates=updates+1\n local btDelta=btReturns-btLast;btLast=btReturns')
    text=once(text,'   nextUpdates=nextUpdates+1',"   if btDelta>0 then assert(btDelta==1 and not pendingBt,'One completed original worker at returned Main');nextUpdates=nextUpdates+1 end")
    text=once(text," if finished then return end;finished=true", " if reason=='full-1-1-and25grounded-1-2'then assert(not pendingBt and btEntries==btReturns and entries==updates,'All actual Main/worker returns balanced')end\n if finished then return end;finished=true")
    text=once(text,'Bt_source_steps=btMoves,Bt_1_2_steps=btNext,','Bt_source_steps=btMoves,Bt_1_2_steps=btNext,Bt_original_entries=btEntries,Bt_original_returns=btReturns,readback=readback,')
    Food.Previous.Previous.Previous.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    return text

def metadata(raw,key='rash'):
    text=controller(raw,key)
    return dict(ROM_SHA256=PIN,parent_SHA256=C.PIN,identity=key,controller_SHA256=C.digest(text.encode()),
        factory_SHA256=C.digest(Path(__file__).read_bytes()),scope='Unchanged ordinary route; flag/castle/entrance then25 grounded completed original workers at actual Main return',
        strict_actual91dc=True,gameplay_seeds=0,outputs=0,Mesen=False)
