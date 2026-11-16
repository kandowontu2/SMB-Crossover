"""Same-control causal1UP lifecycle observer; no game edits or item waiver."""
from functools import lru_cache
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import replay_bowser_natural_stock_bc5_1115 as Previous

R,ROM,PIN,W,N,Current=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current
PARENT_SHA='2d4fe5399d4da143fcfb8d1db40d62315bec5403ed65073eaf7c9d3d9cdfd48f'

@lru_cache(maxsize=2)
def bindings(raw,identity=0):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT_SHA
    q=deepcopy(Previous.bindings(raw,identity,'oneup'));b=Current.bundle(raw);image=Current.frozen_image()
    for name in('BwConstruct','BwEnsure','BwSelectPlayer','BwPlayerNew'):
        pc=W.address(b,name);q['hooks'][name]=dict(pc=pc,offset=3*8192+(pc&8191),space='work',bytes=list(image[pc&8191:(pc&8191)+8]))
    q['lifecycle']={name:W.address(b,name)for name in('BwTier','BwPersistent','BwHP','BwPlayerKey')}
    return q

OBSERVER=r'''
stock.lifecycle={}
local function lifecycle(name)
 local cpu=emu.getState();stock.lifecycle[#stock.lifecycle+1]={event=name,s=sample(),pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],x=cpu['cpu.x'],a=cpu['cpu.a']}
end
hook('BwEnsure',function()if stock.life_credit and not stock.reconstructed then lifecycle('Ensure after INC')end end)
hook('BwConstruct',function()
 if not stock.life_credit or stock.reconstructing then return end
 stock.reconstructing=true;lifecycle('Construct from genuine life increase')
 returning(function(t)
  stock.reconstructed={s=sample(),pc=t.pc,sp=t.sp}
  finish(false,'Causal diagnostic: genuine1UP invokes fresh Bowser constructor and clears earned tier')
 end)
end)
hook('BwSelectPlayer',function()if stock.reconstructing then lifecycle('SelectPlayer')end end)
hook('BwPlayerNew',function()if stock.reconstructing then lifecycle('PlayerNew')end end)
for _,at in ipairs({BStock.lifecycle.BwTier,BStock.lifecycle.BwPersistent+1,BStock.lifecycle.BwPersistent+2})do
 emu.addMemoryCallback(guard(function(address,value)
  if not stock.reconstructing then return end
  local mapped=emu.convertAddress(address)
  if not mapped or mapped.memType~=emu.memType.nesWorkRam or mapped.address//8192~=3 then return end
  assert(#stock.lifecycle<12,'Narrow bounded lifecycle writer trace')
  local cpu=emu.getState();stock.lifecycle[#stock.lifecycle+1]={event='write',address=address,before=read(address),value=value,pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],a=cpu['cpu.a'],x=cpu['cpu.x']}
 end),emu.callbackType.write,at)
end
'''

@lru_cache(maxsize=2)
def controller(raw,identity=0):
    text=Previous.controller(raw,identity,'oneup');prefix='local BStock='+Previous.Text.lua(Previous.bindings(raw,identity,'oneup'))+'\n'
    assert text.startswith(prefix);body=text[len(prefix):]
    marker='-- Observe every actual GameLoop return, including the native catch-up caller.'
    body=Previous.once(body,marker,OBSERVER+'\n'+marker)
    text='local BStock='+Previous.Text.lua(bindings(raw,identity))+'\n'+body
    Previous.Old.Base.LuaRuntime().compile(text);return text

def metadata(raw,identity=0):
    q=Previous.metadata(raw,identity,'oneup');q.update(controller_SHA256=sha256(controller(raw,identity).encode()).hexdigest(),
        observer_factory_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),scope='Same-controls genuine1UP first constructor/clear writer; causal diagnostic only')
    return q
