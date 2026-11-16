"""Separate Bowser Star policy: leave the actual roof, return beneath block."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import replay_bowser_natural_stock_bc5_1115 as Previous

R,ROM,PIN,W,N,Current=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current
PARENT_SHA='2d4fe5399d4da143fcfb8d1db40d62315bec5403ed65073eaf7c9d3d9cdfd48f'

DROP=r'''
 if BStock.kind==2 and stock.phase=='align'and s.y<160 then
  stock.drop_from=s;local row=s.y+32;local exit
  stock.roof_cells={}
  for wx=((s.x+8)//16)*16,((s.x+8)//16)*16+192,16 do
   local t=tile(wx,row);stock.roof_cells[#stock.roof_cells+1]={x=wx,y=row,tile=t,solid=solid(wx,row),floor=tile(wx,208)}
   if not solid(wx,row)then exit=wx+1;break end
  end
  assert(exit and solid(exit+8,208),'Actual adjacent roof edge and safe native floor')
  stock.drop_target=exit;stock.phase='drop-east'
 end
 if stock.phase=='drop-east'then
  pad=s.x<stock.drop_target and 1 or 0
  if s.x>=stock.drop_target and s.native_state==0 and s.y==176 then
   stock.ground_after_drop=s;stock.phase='align';stock.release=nil
  end
  return
 end
'''

@lru_cache(maxsize=2)
def controller(raw,identity=0):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT_SHA
    text=Previous.controller(raw,identity,'star')
    marker=" if stock.phase=='align'then"
    text=Previous.once(text,marker,DROP+'\n'+marker)
    Previous.Old.Base.LuaRuntime().compile(text);return text

def metadata(raw,identity=0):
    q=Previous.metadata(raw,identity,'star');q.update(controller_SHA256=sha256(controller(raw,identity).encode()).hexdigest(),
        successor_factory_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),
        scope='Same retained earned M/F/traversal; one actual roof-edge drop/ground return before fresh Star head jump')
    return q
