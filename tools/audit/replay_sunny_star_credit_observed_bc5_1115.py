"""Separate same-input Sunny Star popup/writer diagnostic; old controller frozen."""
from functools import lru_cache
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import replay_sunny_natural_stock_bc5_1115 as Previous

R,ROM,PIN,W,N,Current=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current
PARENT_SHA='391f5303adea769e9447f29907f55e9893f053d6340df00c0565ea8e11c9be70'

def once(text,old,new):assert text.count(old)==1,old;return text.replace(old,new,1)

@lru_cache(maxsize=1)
def bindings(raw,key='star'):
    assert key=='star' and sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT_SHA
    q=deepcopy(Previous.bindings(raw,key));b=Current.bundle(raw)
    name='AddToScore';at,pc=W.location(b,name),W.address(b,name);bank=(at-16)//8192
    q['hooks'][name]=dict(pc=pc,offset=at-16,bytes=list(raw[at:at+8]),bank=bank,
        bank_SHA256=sha256(raw[16+bank*8192:16+(bank+1)*8192]).hexdigest())
    return q

@lru_cache(maxsize=1)
def controller(raw,key='star'):
    text=Previous.controller(raw,key);prefix='local C='+Previous.Text.lua(Previous.bindings(raw,key))+'\n'
    assert text.startswith(prefix);body=text[len(prefix):]
    body=once(body," if stock.collected then buttons={};return end",''' if stock.collected then
  buttons={}
  local i=stock.collector.actor.slot;local timer=r('FloateyNum_Timer',i);local control=r('FloateyNum_Control',i)
  stock.popup_samples=stock.popup_samples or{}
  if#stock.popup_samples<8 and(stock.lastTimer~=timer or stock.lastControl~=control)then
   if#stock.popup_samples<2 or timer<=44 then stock.popup_samples[#stock.popup_samples+1]={state=state(),timer=timer,control=control,pendingScore=pendingScore~=nil}end
  end
  stock.lastTimer=timer;stock.lastControl=control
  if guestReturns-stock.collected.state.guest>=80 then finish(false,'Same-controls popup/writer diagnostic complete')end
  return
 end''')
    body=once(body,"hook('FloateyNumbersCore',function()\n if C.kind~=2",'''hook('FloateyNumbersCore',function()
 if stock.collected then
  local i=emu.getState()['cpu.x'];stock.core_trace=stock.core_trace or{}
  if#stock.core_trace<8 then stock.core_trace[#stock.core_trace+1]={state=state(),slot=i,timer=r('FloateyNum_Timer',i),control=r('FloateyNum_Control',i),pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp']}end
 end
 if C.kind~=2''')
    body=once(body,"hook('LifeBefore',function()",'''hook('AddToScore',function()
 if not stock.collected then return end
 stock.score_writes=stock.score_writes or{};if#stock.score_writes>=8 then return end
 local before=state();returning(function(t)stock.score_writes[#stock.score_writes+1]={before=before,after=state(),pc=t.pc,sp=t.sp}end)
end)
hook('LifeBefore',function()''')
    text='local C='+Previous.Text.lua(bindings(raw,key))+'\n'+body
    Previous.LuaRuntime().compile(text);return text

def metadata(raw,key='star'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        observer_factory_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),bindings=bindings(raw,key),
        scope='Same original ordinary inputs; <=8 popup/core/score samples after physical Star collection; diagnostic only')
    return q
