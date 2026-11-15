"""Finite genuine ground/cap running-jump then Up-reach hidden1UP routes."""
from functools import lru_cache
import replay_prince_natural_stock_fast_40a_1115 as Previous

C,N,W,PIN=Previous.C,Previous.N,Previous.W,Previous.PIN

@lru_cache(maxsize=2)
def controller(raw,mode='oneup',jump=8,*,start='ground'):
    assert mode=='oneup'and jump==8 and start in('ground','cap')and C.digest(raw)==PIN
    text=Previous.controller(raw,mode,jump)
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:100];text=text.replace(a,b,1)
    old='STOCK.kind==3 and late.fourth_practical_cap and s.x>=980'
    change(old,'STOCK.kind==3 and late.fourth_practical_cap and s.x>='+('899'if start=='cap'else'960'))
    phase='cap-run'if start=='cap'else'ground-retreat'
    change("stockPhase(STOCK.kind==3 and'approach'or'left-drop',0)",f"stockPhase('{phase}',{1 if start=='cap'else 2})")
    a=text.index(" if stock.phase=='left-drop'then");z=text.index('\n return true\nend\n',a)
    policy=r'''
 if stock.phase=='ground-retreat'then
  pad=2
  if floor(s)and s.x<=948 then stockPhase('ground-run',1)end
 elseif stock.phase=='ground-run'or stock.phase=='cap-run'then
  pad=1
  local ready=s.action==1 and s.mode==1 and s.pose>=6 and s.pose<=13 and s.lock==0
  local at=stock.phase=='cap-run'and s.x>=921 and s.y>=111 and s.y<=114 or stock.phase=='ground-run'and floor(s)and s.x>=958
  if ready and at then stock.running_request=s;stockPhase('running-press',129)end
  assert(s.x<(stock.phase=='cap-run'and 944 or 1008),'Bounded genuine runway before running jump')
 elseif stock.phase=='running-press'then
  if s.action==4 then stock.running_admission=s;stock.minimum_y=s.y;stockPhase('running-reach',8)
  else pad=129;assert(age<48,'Actual original running-jump admission')end
 elseif stock.phase=='running-reach'then
  stock.minimum_y=math.min(stock.minimum_y,s.y);pad=age<96 and 8 or 0
  if age>120 and floor(s)and idle(s)and s.action==0 then
   stock.running_end=s;final=s;finish(false,'Running jump and held reach completed without hidden1UP birth')
  end
 end'''
    text=text[:a]+policy+text[z:]
    b=dict(W.Symbols.bundle(),raw=raw);head=W.address(b,'BlockBufferAdderData')+6
    change(' if s.pose~=78 and vy<128 then return end',
        f" if stock.phase~='running-reach'or cpu['cpu.y']~=read({head})or(s.pose~=78 and vy<128)then return end")
    Previous.LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8,*,start='ground'):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump,start=start).encode()),required_native_variant=3,
        genuine_start=start,ordinary_running_A_then_held_Up=True,no_gameplay_seeds=True,native_ready=False,outputs=0,Mesen=False)
