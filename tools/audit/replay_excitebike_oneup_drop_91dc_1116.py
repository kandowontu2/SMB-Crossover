"""Legal fourth-cap drop and source run-up beneath the authored hidden1UP."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_excitebike_stock_91dc_1116 as Previous

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='27c077a48a789ccc41e8866f9712c48a15c84734481a03e0e8783cedec8cc445'

@lru_cache(maxsize=1)
def controller(raw,key='oneup'):
    assert key=='oneup'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key);a=text.index('local function stockDrive()\n');b=text.index('\nlocal function drive()',a)
    text=text[:a]+"""local function stockDrive()
 identity();assert(r('GameEngineSubroutine')~=11,'Actual hidden route death')
 buttons=0;routeEpoch=routeEpoch+1;local s=state();local a=stockObserve()
 assert(mainReturns-stock.since<3500,'Bounded genuine hidden1UP route')
 stock.last=stock.last or{};stock.last[#stock.last+1]=s;if#stock.last>10 then table.remove(stock.last,1)end
 if stock.collected or not active()then return end
 -- Park after the real birth. The native1UP walks and falls into the bike;
 -- no synthetic chase jump, actor movement or collision outcome is supplied.
 if a then phase='stock-wait-natural-oneup';return end
 local function feet()return{state=state(),left=block(s.x+2,s.y+32),right=block(s.x+13,s.y+32),pipeLeft=block(912,144),pipeRight=block(928,144)}end
 if stock.phase=='travel'then
  phase='hidden-fourth-cap-approach';buttons=bits(travel())
  if s.x>=899 and s.x<944 and s.y<=113 and s.native==0 and s.air==0 then
   stock.phase='cap-drop';stock.cap=feet();travelJump=nil;buttons=1
  end
 elseif stock.phase=='cap-drop'then
  phase='hidden-legal-cap-drop';buttons=s.x<944 and 1 or 0
  if s.x>=944 and s.y>=176 and s.native==0 and s.air==0 then stock.phase='return-wall';stock.landing=feet();buttons=66 end
  assert(s.x<1088,'Drop must remain before real pit1104')
 elseif stock.phase=='return-wall'then
  phase='hidden-return-real-pipe';buttons=66
  if s.x<=960 then stock.phase='wall-coast';stock.coast=feet();buttons=0 end
 elseif stock.phase=='wall-coast'then
  phase='hidden-coast-at-real-pipe'
  if s.speed==0 and s.crash==0 and s.native==0 and s.air==0 then stock.phase='runup';stock.stand=feet();buttons=65 end
 elseif stock.phase=='runup'then
  phase='hidden-original-runup';buttons=65
  if s.x>=980 and s.native==0 and s.air==0 and s.crash==0 then
   stock.phase='prelean';stock.prelean=mainReturns;stock.prelean_request=feet();buttons=73
  end
 elseif stock.phase=='prelean'then
  phase='hidden-Up-prelean';buttons=73
  if mainReturns-stock.prelean>=4 then
   stock.phase='head';stock.head=mainReturns;stock.head_request=feet();stock.authored_tile=block(1024,128)
   assert(stock.authored_tile==96,'Actual authored hidden60');buttons=201
  end
 elseif stock.phase=='head'then
  phase='hidden-freshA-air-Up';local n=mainReturns-stock.head
  buttons=n<8 and 201 or n<36 and 8 or 0
  stock.minimum_y=math.min(stock.minimum_y or 255,s.y)
  assert(n<180,'One genuine source hidden-head attempt')
 else error('Unknown hidden route phase '..stock.phase)end
end
"""+text[b:]
    Previous.Previous.LuaRuntime().compile(text);return text

def metadata(raw,key='oneup'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),drop_factory_SHA256=digest(Path(__file__).read_bytes()),
        scope='GenuineM+25, legal fourth-cap drop/real-pipe run-up, hidden1UP physical lifecycle/delayedINC/cue64 then25 original returned updates',
        legal_support='Actual engine ground state and both foot cells recorded; one valid engine-supported foot is allowed')
    return q

def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
