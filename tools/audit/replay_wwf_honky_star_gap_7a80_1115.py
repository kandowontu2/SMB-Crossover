"""Honky-only later static-floor edge, retaining the existing native helper."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import replay_wwf_natural_star_7a80_1115 as Previous
import replay_smb1_alts_full11_1114 as Text

R,ROM,W,N,PIN,IDENTITIES=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN,Previous.IDENTITIES
Frozen,normalize=Previous.Frozen,Previous.normalize
PARENT='15ec414644b7f4b1e6ad3de85e8ae385862dcae12df9741b1a31ee6bc63ba640'
once=Previous.once


@lru_cache(maxsize=6)
def bindings(raw,key='honky'):
    old=Previous.bindings(raw,key)
    if key!='honky':return old
    q=deepcopy(old);b=dict(W.Symbols.bundle(),raw=raw)
    q['ram']['PlatformCollisionFlag']=W.address(b,'PlatformCollisionFlag')
    name='PositionPlayerOnHPlat';at=W.location(b,name);bank=(at-16)//8192
    q['hooks'][name]=dict(pc=W.address(b,name),offset=at-16,bytes=list(raw[at:at+8]),bank=bank,
        bank_SHA256=sha256(raw[16+bank*8192:16+(bank+1)*8192]).hexdigest())
    return q


@lru_cache(maxsize=6)
def controller(raw,key='honky'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT
    text=Previous.controller(raw,key)
    if key!='honky':return text
    prefix='local C='+Text.lua(Previous.bindings(raw,key))+'\n';assert text.startswith(prefix)
    body=text[len(prefix):]
    body=once(body,'local pit=s.x>=1346 and s.x<1424','local pit=false')
    body=once(body,'if pit or not solid(s.x+12,216)or solid(s.x+28,s.y+24)then',
        'if pit or not solid(s.x+8,216)or solid(s.x+28,s.y+24)then')
    observe=r'''
hook(C.hooks.PositionPlayerOnHPlat,function()
 local cpu=emu.getState();local i=cpu['cpu.x'];if i<0 or i>5 then return end
 local a=actor(i)
 if stock.active and a.flag~=0 and a.id==40 then
  assert(r('PlatformCollisionFlag',i)<128,'Actual admitted native horizontal helper passenger')
  stock.helper_carries=(stock.helper_carries or 0)+1
  stock.first_helper_carry=stock.first_helper_carry or{state=state(),actor=a,passenger=r('PlatformCollisionFlag',i),PC=cpu['cpu.pc'],SP=cpu['cpu.sp']}
 end
end)
'''
    body=once(body,'local function drive()',observe+'\nlocal function drive()')
    body=once(body,"observeStock(s);assert(completed<4600,'WWF stock completedMain bound')",r'''
observeStock(s)
 if stock.active and s.x>=1328 and s.x<=1450 and completed%4==0 then
  stock.gap_trace=stock.gap_trace or{};local t=stock.gap_trace;local aa={}
  for i=0,5 do local a=actor(i);if a.flag~=0 and a.id==40 then aa[#aa+1]={actor=a,passenger=r('PlatformCollisionFlag',i)}end end
  t[#t+1]={state=s,pad=pad,AB=r('A_B_Buttons'),previousAB=r('PreviousA_B_Buttons'),helpers=aa}
  if#t>24 then table.remove(t,13)end
 end
 assert(completed<4600,'WWF stock completedMain bound')''')
    body=once(body,"finish(true,'Natural WWF '..C.stock_name..' and25 actual post-credit WWF movement entries');return",
        "assert((stock.helper_carries or 0)>0,'Real existing native helper carried Honky through the authored gap');finish(true,'Natural WWF '..C.stock_name..' and25 actual post-credit WWF movement entries');return")
    result='local C='+Text.lua(bindings(raw,key))+'\n'+body;Frozen.LuaRuntime().compile(result)
    assert not any(s in result for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return result


def metadata(raw,key='honky'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),parent_factory_SHA256=PARENT,
        honky_only_later_edge=key=='honky',helper_geometry_unchanged=True,
        helper=dict(stage='1-1/area25',initial_left=1376,initial_center=1400,initial_Y=208,width=48,actor=40),
        scope='Honky later real-floor x+8 edge instead of early1346 trigger; actual native carry required, same genuine M/F/Star/producers/25-call gates. Other roles exact frozen parent controls; native pending')
    return q


def family():return SimpleNamespace(R=R,ROM=ROM,W=W,N=N,PIN=PIN,IDENTITIES=IDENTITIES,Frozen=Frozen,normalize=normalize,bindings=bindings,controller=controller,metadata=metadata)
