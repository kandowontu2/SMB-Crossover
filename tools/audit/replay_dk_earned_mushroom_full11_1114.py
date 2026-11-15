"""Exact571 DK full1-1 after the native-qualified real first mushroom."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import replay_dk_natural_mushroom_1114 as Previous

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,IDENTITIES,normalize=Previous.Frozen,Previous.IDENTITIES,Previous.normalize
OLD_SOURCE_SHA='e9a7663e6e11b91c20a6867c90a0785f7391cbb4082c782a965a9653d35e8bcb'
OLD_LUA_SHA='40bc915efc8de359b246537a92aece7c4a31f5f5fdaf8548875642daa1054591'


@lru_cache(maxsize=1)
def bindings(raw,key='donkey_kong'):
    q=deepcopy(Previous.bindings(raw,key));b=dict(W.Symbols.bundle(),raw=raw)
    for name in('DkSpawnBarrel','DkHostInjury'):
        at=W.location(b,name);pc=W.address(b,name);bank=(at-16)//8192
        q['hooks'][name]=dict(pc=pc,offset=at-16,bytes=list(raw[at:at+8]),bank=bank)
        size=int(b['syms'][name]['size'],0);assert 0<size<256
        exits=[i for i in range(size)if raw[at+i]==0x60];assert exits
        for i,delta in enumerate(exits):
            q['hooks'][name+'Exit'+str(i)]=dict(pc=pc+delta,offset=at+delta-16,
                bytes=list(raw[at+delta:at+delta+8]),bank=bank)
    for h in q['hooks'].values():
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes'])
        if'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q


@lru_cache(maxsize=1)
def controller(raw,key='donkey_kong'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==OLD_SOURCE_SHA
    text=Previous.controller(raw,key);assert sha256(text.encode()).hexdigest()==OLD_LUA_SHA
    prefix='local C='+Frozen.lua(Previous.bindings(raw,key))+'\n';assert text.startswith(prefix)
    text='local C='+Frozen.lua(bindings(raw,key))+'\n'+text[len(prefix):]
    once=Previous.once
    old=next(line for line in text.splitlines()if line.startswith(' local ok='))
    base=Previous.Previous.controller(raw,key)
    new=next(line for line in base.splitlines()if line.startswith(' local ok='))
    new+=' and dkMush.born and dkMush.mature and dkMush.grant and dkMush.collected and dkMush.erase and dkMush.score and dkMush.cue and dkMush.resume==25 and dkMush.ready'
    text=once(text,old,new)
    marker='local dkMushPending,dkGrantPending,dkCollector'
    text=once(text,marker,marker+'\nlocal dkBarrelProof={count=0,rows={}}\nlocal dkInjuryProof={count=0,rows={}}\nlocal dkSpawnPending,dkInjuryPending')
    text=once(text,'natural_mushroom=dkMush,','natural_mushroom=dkMush,actual_barrel_spawns=dkBarrelProof,actual_injuries=dkInjuryProof,')
    old='if not first or not identity()or not active()then return end'
    assert text.count(old)==2
    text=text.replace(old,'if not first or not identity()or not active()or dkMush.collected then return end')
    old='if a.flag==1 and a.id==46 then';assert text.count(old)==2
    text=text.replace(old,'if a.flag==1 and a.id==46 and not dkMush.collected then')
    text=once(text,'if dkMush.collected and dkMoves~=dkMush.lastMoves and active()then',
        'if dkMush.collected and dkMush.resume<25 and dkMoves~=dkMush.lastMoves and active()then')
    text=once(text,"if dkMush.resume==25 then finish('natural-mushroom-tier-and25-resume');return end",
        'if dkMush.resume==25 then dkMush.ready=state();dkMush.final_score=dkScore()end')
    text=once(text,'if dkMush.collected then return{}end',
        'if dkMush.collected then if dkMush.resume<25 then return{}else return choose(c)end end')
    text=once(text,'if frame>=6000 or updates>=2600','if frame>=16000 or updates>=10000')
    insert=r'''
local function dkKeep(proof,row)
 proof.count=proof.count+1;proof.rows[#proof.rows+1]=row
 if #proof.rows>8 then table.remove(proof.rows,5)end
end
hook('DkSpawnBarrel',function()
 if not identity()or not active()or r('DkSpawn')~=1 then return end
 assert(not dkSpawnPending,'One actual native barrel spawn in flight')
 local sp,ret=dkCall();local old={};for i=0,2 do old[i+1]=r('DkShots',12*i)end
 dkSpawnPending={sp=sp,ret=ret,old=old}
end)
hook('DkHostInjury',function()
 if not identity()or not active()or r('InjuryTimer')~=0 then return end
 local sp,ret=dkCall();dkInjuryPending={sp=sp,ret=ret,tier=r('DkTier'),before=state()}
end)
for name in pairs(C.hooks)do
 if name:match('^DkSpawnBarrelExit')then hook(name,function()
  if not dkSpawnPending then return end
  local sp,ret=dkCall();assert(sp==dkSpawnPending.sp and ret==dkSpawnPending.ret,'Actual barrel-spawn caller return')
  if emu.getState()['cpu.ps']&1~=0 then
   local found
   for i=0,2 do local at=12*i;if dkSpawnPending.old[i+1]==0 and r('DkShots',at)~=0 then
    assert(not found,'One physical barrel per successful spawn');found=true
    dkKeep(dkBarrelProof,{state=state(),slot=i,kind=r('DkShots',at),x=r('DkShots',at+4)+256*r('DkShots',at+5),
     y=r('DkShots',at+6),direction=r('DkShots',at+7),tier=r('DkTier'),actual_Cset=true})
   end end
   assert(found,'Actual successful spawn publishes a new native shot')
  end
  dkSpawnPending=nil
 end)
 elseif name:match('^DkHostInjuryExit')then hook(name,function()
  if not dkInjuryPending then return end
  local sp,ret=dkCall();assert(sp==dkInjuryPending.sp and ret==dkInjuryPending.ret,'Actual injury caller return')
  assert(dkInjuryPending.tier>0 and r('DkTier')==dkInjuryPending.tier-1
   and r('InjuryTimer')==90 and r('NumberofLives')==2,'Earned tier absorbs one ordinary hit')
  dkKeep(dkInjuryProof,{before=dkInjuryPending.before,after=state(),timer=r('InjuryTimer')})
  dkInjuryPending=nil
 end)end
end
'''
    text=once(text,"hook('DkMovement',function()",insert+"hook('DkMovement',function()")
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='donkey_kong'):
    return dict(ROM_SHA256=PIN,identity=key,controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        parent_natural_collector_SHA256=OLD_LUA_SHA,normal_controls_only=True,gameplay_seeds=0,outputs=0,Mesen_run=False,
        scope='Native-qualified first mature mushroom and25 resumed DK calls, then full nonshortcut1-1 and25 living grounded1-2; real barrels and ordinary nonfatal injury allowed')
