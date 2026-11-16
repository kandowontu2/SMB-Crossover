"""Ordinary5-1 controls for its authored ground-reach hidden1UP row144."""
from functools import lru_cache
import re
import replay_prince_oneup_stage2_stair67_1115 as Previous
from replay_prince_natural_stock_40a_1115 import LuaRuntime,lua

C,PIN=Previous.C,Previous.PIN

def authored(raw):
    data=bytearray()
    for line in(C.R/'src/level_tiles.s').read_text().split('L_GroundArea11:',1)[1].splitlines():
        if'.byte'in line:
            data.extend(int(v,16)for v in re.findall(r'\$([\da-fA-F]{2})',line.split(';')[0]))
            if data[-1]==253:break
    blob=bytes(data);assert raw.count(blob)==1 and bytes.fromhex('37634703')in blob
    return dict(stage='5-1',label='L_GroundArea11',offset=raw.index(blob),bytes=len(blob),SHA256=C.digest(blob),hidden1UP=[2368,144],
        scope='Exact authored blob; reachability requires the actual ordinary route')

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    text=Previous.controller(raw,mode,jump)
    assert C.digest(text.encode())=='e96b11e20dc5a7f697eb00cce5f1e34749885db60da2b608eb13f70b3f412796'
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:100];text=text.replace(a,b,1)
    lines=text.splitlines(keepends=True);i=next(i for i,v in enumerate(lines)if v.startswith('local STOCK='))
    assert lines[i].count('["x"]=448')==1 and lines[i].count('["y"]=80')==1
    lines[i]=lines[i].replace('["x"]=448','["x"]=2368').replace('["y"]=80','["y"]=144');text=''.join(lines)
    a=text.index('stock.authored_level=');b=text.index('\n',a);text=text[:a]+'stock.authored_level='+lua(authored(raw))+text[b:]
    change("stockPhase('two1-platform-approach',1)","stockPhase('five1-run',1)")
    change('stock.prince_returns-stock.start.Prince_returns<2600','stock.prince_returns-stock.start.Prince_returns<3900')
    a=text.index(" if stock.phase=='two1-platform-approach'then");b=text.index(" elseif stock.phase=='coin-ledge-approach'then",a)
    text=text[:a]+r''' if stock.phase=='five1-run'then
  pad=1;stock.travel=stock.travel or{maximum=s.x,last_advance=stock.prince_returns,walls={},jumps={}}
  local t=stock.travel
  if s.x>t.maximum then t.maximum=s.x;t.last_advance=stock.prince_returns end
  if s.x>=2384 and s.y<=114 then stockPhase('five1-drop-ready',0);return true end
  local running=s.action==1 and s.mode==1 and s.pose>=6 and s.pose<=13 and s.lock==0
  local threat
  for i=0,5 do local e=stockActor(i);local gap=e.x-s.x
   if e.flag~=0 and e.id<7 and gap>=110 and gap<=142 and math.abs(e.y-s.y)<=32 then threat=e;break end
  end
  local hole=s.y>=174 and tile(s.x+32,208)==0
  if running and(threat or hole)and s.phase&3<=1 then
   t.jumps[#t.jumps+1]={request=s,enemy=threat,hole=hole};stockPhase('five1-A',129)
  elseif s.action==1 and stock.prince_returns-t.last_advance>=28 then
   local wall={request=s,cells={}};t.walls[#t.walls+1]=wall
   for x=(s.x//16)*16,(s.x//16)*16+80,16 do local c={x=x};for y=80,208,16 do local v=tile(x,y);if v~=0 then c[#c+1]={y=y,tile=v}end end;wall.cells[#wall.cells+1]=c end
   assert(#t.walls<=8,'Finite authored5-1 walls');stockPhase('five1-wall-ready',0)
  end
  assert(stock.prince_returns-t.last_advance<350,'Ordinary5-1 route must advance')
 elseif stock.phase=='five1-wall-ready'then
  pad=0
  if idle(s)and s.action==0 then stock.travel.walls[#stock.travel.walls].stance=s;stockPhase('five1-Up',8)end
  assert(age<150,'Actual idle before original wall Up')
 elseif stock.phase=='five1-Up'then
  pad=8;local w=stock.travel.walls[#stock.travel.walls]
  if s.action==9 or s.action==10 or s.mode==2 or s.mode==6 then w.hang=w.hang or s end
  if w.hang and s.action==10 and idle(s)and s.y<=w.stance.y-20 then
   if w.stance.x>=2320 then
    if s.y<=114 then w.cap=s;stockPhase('five1-drop-ready',0)end
   else
    w.partial_cap=s;stock.travel.jumps[#stock.travel.jumps+1]={request=s,kind='wall-cap'};stockPhase('five1-A',128)
   end
  elseif w.hang and idle(s)and s.y<=w.stance.y-8 then w.cap=s;stock.travel.last_advance=stock.prince_returns;stockPhase('five1-run',1)end
  assert(age<200,'Original Up must admit real wall climb')
 elseif stock.phase=='five1-A'then
  if s.action==3 or s.action==4 then
   local j=stock.travel.jumps[#stock.travel.jumps];j.admission=s;j.minimum_y=s.y
   stockPhase('five1-air',129)
  end
  assert(age<75,'Original running or standing jump admission')
 elseif stock.phase=='five1-air'then
  pad=129;local j=stock.travel.jumps[#stock.travel.jumps];j.minimum_y=math.min(j.minimum_y,s.y)
  if s.action==9 or s.mode==2 or s.mode==6 then j.hang=j.hang or s end
  if j.hang then
   pad=8
   if s.action==10 and idle(s)then j.hoist=s;stockPhase('five1-air-release',0)end
  elseif age>=45 and s.action~=3 and s.action~=4 and s.action~=9 and s.action~=10 then
   j.landing=s;stock.travel.last_advance=stock.prince_returns;stockPhase('five1-run',1)
  end
  assert(age<210,'Bounded ordinary5-1 jump/grab')
 elseif stock.phase=='five1-air-release'then
  pad=0;if idle(s)and s.action==0 then stock.travel.last_advance=stock.prince_returns;stockPhase('five1-run',1)end
  assert(age<180,'Actual idle after original airborne grab')
 elseif stock.phase=='five1-drop-ready'then
  pad=0
  if idle(s)and s.action==0 then stock.last_column_cap=s;stockPhase('five1-drop',1)end
  assert(age<160,'Actual final authored-column roof idle')
 elseif stock.phase=='five1-drop'then
  pad=s.x<2400 and 1 or 0
  if s.x>=2400 then stock.drop_release=stock.drop_release or s end
  assert(s.x<2432,'Ordinary drop remains before authored hole2432')
  if s.y>=175 and idle(s)and s.action==0 then stock.ground_right_of_column=s;stockPhase('approach',0)end
  assert(age<220,'Actual legal drop to ground beside hidden1UP')
'''+text[b:]
    change('for i=1,4 do press(1,34)end','for i=1,16 do press(1,34)end')
    change("assert(read(0x7ffb)==0 and read(0x7ffc)==36,'Only actual2-1 level setting changed')",
        "assert(read(0x7ffb)==0 and read(0x7ffc)==48,'Only actual5-1 level setting changed')")
    change("assert(read(0x7ffb)==0 and read(0x7ffc)==36,'Actual2-1 setting and all gameplay cheats off');assert(read(0x764)==1 and read(0x761)==0,'Actual2-1 stage')",
        "assert(read(0x7ffb)==0 and read(0x7ffc)==48,'Actual5-1 setting and all gameplay cheats off');assert(read(0x764)==4 and read(0x761)==0,'Actual5-1 stage')")
    change("assert(read(verifiedHooks.ram.CheatInvincible)==0 and read(verifiedHooks.ram.CheatStartLevel)==36,'Actual2-1 selection with all gameplay cheats off')",
        "assert(read(verifiedHooks.ram.CheatInvincible)==0 and read(verifiedHooks.ram.CheatStartLevel)==48,'Actual5-1 selection with all gameplay cheats off')")
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        stage='5-1',authored=authored(raw),exact_level_setting48_and_all_gameplay_flags_zero=True,
        ordinary_original_running_jumps_held_grab_and_Up=True,
        real_birth_mature_overlap_erase_delayed_INC_cue64_and25returns_required=True,
        source_UI_mailbox_unit_lacks_real_vblank=True,actual_current67_CPU=True,
        no_gameplay_seeds=True,no_helpers_added=True,outputs=0,Mesen=False)
