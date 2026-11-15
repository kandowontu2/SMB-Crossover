"""Strict571 per-class genuine M/F followed by native mature Star pickup."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import replay_ff_natural_oneup_current_1114 as Previous

R,ROM,PIN,W,N=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N
Frozen,normalize=Previous.Frozen,Previous.normalize
IDENTITIES={key.replace('-life','-star'):value for key,value in Previous.IDENTITIES.items()}
OLD_SHA='7dfe004b5fbe7cf25a0ab29526494cf067bce051a6914872a6f520ddd94a1fb8'


def parent(key):
    assert key in IDENTITIES
    return key.replace('-star','-life')


@lru_cache(maxsize=4)
def bindings(raw,key='fighter-star'):
    q=deepcopy(Previous.bindings(raw,parent(key)));q['key']=key
    b=dict(W.Symbols.bundle(),raw=raw)
    for name in('Player1ScoreDisplay','BoundingBox_UL_Corner','EnemyBoundingBoxCoord'):
        q['extra_ram'][name]=W.address(b,name)
    return q


@lru_cache(maxsize=4)
def controller(raw,key='fighter-star'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==OLD_SHA
    pk=parent(key);text=Previous.controller(raw,pk);once=Previous.once
    prefix='local C='+Frozen.lua(Previous.bindings(raw,pk))+'\n';assert text.startswith(prefix)
    text='local C='+Frozen.lua(bindings(raw,key))+'\n'+text[len(prefix):]
    text=once(text,"validateGroup(1); enterPhase('stock-life'); transition=true","validateGroup(1); enterPhase('flower'); transition=true")
    text=once(text,"validateGroup(2); enterPhase('attack'); transition=true","validateGroup(2); enterPhase('stock-star'); transition=true")
    text=once(text,'stock_oneup=stock,','stock_star=stock,')
    text=once(text,"local function actor(i)",r'''
local function stockScore()
 local n=0;for i=0,5 do local d=r('Player1ScoreDisplay',i);assert(d<10,'Numeric current score');n=n*10+d end;return n
end
local function stockBox(name,i)local a={};for j=0,3 do a[#a+1]=r(name,(i or 0)*4+j)end;return a end
local function actor(i)''')
    text=once(text,'  if not gameplay or bindingChecked then return end',
        '  if not gameplay then return end\n  stock.actual_FF_entries=(stock.actual_FF_entries or 0)+1\n  if bindingChecked then return end')
    branch=r'''
  elseif phase=='stock-star'then
   assert(step<1800 and active(s),'Bounded active natural Star continuation')
   assert(s.power==2 and s.earned==2 and s.charges==(variant==1 and 3 or 0),'Keep individually earned Flower gear')
   if stock.collected then
    bits=0
    stock.resume=stock.actual_FF_entries-stock.collected.actual_FF_entries
    assert(stock.resume<=25 and s.star>0,'Bounded actual protected FF entries')
    stock.final_score=stockScore()
    if stock.final_score>=stock.collector.score+1000 then stock.score_awarded=stock.score_awarded or{player=s,score=stock.final_score}end
    if stock.resume==25 then
     assert(stock.score_awarded,'Actual native Star1000 credit after normal popup delay')
     requestFinish(true,'Natural FF M/F/Star collector and25 actual post-collector FF entries');return
    end
   elseif item then
    assert(item.kind==2,'Actual ordinary Star kind2')
    if not stock.born then assert(item.x==1616,'Authored ordinary Star block');stock.born={player=s,actor=item}end
    if item.state>=128 then stock.mature=stock.mature or{player=s,actor=item}end
    local gap=item.x-s.x;bits=(gap>3 and 1 or 0)|(gap< -3 and 2 or 0)
    if math.abs(gap)<40 and item.y<s.y-16 and s.state==0 and step-(stock.jump or -100)>40 then
     bits=bits|128;stock.jump=step;desiredJumpReason='stock-star-item-jump'
    end
   elseif s.x<1608 then
    bits=1
    if s.state==0 and step-(stock.jump or -100)>40 then
     local pit=1346<=s.x and s.x<1424
     local near=false
     for _,v in ipairs(a)do
      if v.flag==1 and(v.id==0 or v.id==3 or v.id==6)and v.state<2 and v.x-s.x>=60 and v.x-s.x<=90 and math.abs(v.y-s.y-8)<24 then near=true;break end
     end
     if pit or near then
      stock.jump=step;bits=bits|128;desiredJumpReason=pit and'stock-star-pit'or'stock-star-live-enemy'
     end
    end
   else
    local gap=1610-s.x;bits=(gap>2 and 1 or 0)|(gap< -2 and 2 or 0)
    if math.abs(gap)<=2 and s.state==0 and step-(stock.jump or -100)>40 then
     stock.jump=step;bits=bits|128;desiredJumpReason='stock-star-block'
    end
   end
'''
    text=once(text,"  elseif phase=='stock-life'then",branch+"  elseif phase=='stock-life'then")
    install=r'''
 hook(0xbb60,private,'StockStarFfHostCollect',function(cpu)
  if not gameplay or phase~='stock-star'then return end
  local i=cpu['cpu.x'];local a=actor(i);local s=state()
  assert(stock.born and stock.mature and a.flag==1 and a.id==46 and a.kind==2 and a.state>=128,'Actual mature named-class Star collector')
  assert(s.star==0,'No prior Star timer')
  local q={player=s,actor=a,slot=i,score=stockScore(),player_box=stockBox('BoundingBox_UL_Corner'),item_box=stockBox('EnemyBoundingBoxCoord',i)}
  stock.collector=q
  onReturn(cpu,'stock-star-collect',q,function(before,returned)
   local p=returned['cpu.ps']or returned['cpu.p'];local after=state()
   assert(p&1~=0 and r('Enemy_Flag',before.slot)==0 and r('FloateyNum_Control',before.slot)==6 and r('Square2SoundQueue')==32,'Real native Star erase/control6/cue32')
   assert(after.star==35 and r('AreaMusicQueue')==64,'Real native Star timer/music producers')
   assert(after.active==0 and after.timer==0 and after.lives==2,'Star has no powerup freeze or life grant')
   assert(after.power==before.player.power and after.earned==before.player.earned and after.charges==before.player.charges,'Star preserves genuine class gear')
   stock.collected={before=before,after=after,cue=32,music=64,actual_FF_entries=assert(stock.actual_FF_entries)}
  end)
 end)
'''
    text=once(text," hook(0x82d9,function(pc) return native(pc,126) end,'GameLoop'",install+"\n hook(0x82d9,function(pc) return native(pc,126) end,'GameLoop'")
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='fighter-star'):
    q=Previous.metadata(raw,parent(key))
    q.update(identity=key,controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        prior_factory_SHA256=OLD_SHA,
        scope='Named-class real M/F/freeze then mature native Star/timer/music/erase/score and25 actual post-collector FF entries; expiry/protected-hit/fullstage/graphics separate')
    return q
