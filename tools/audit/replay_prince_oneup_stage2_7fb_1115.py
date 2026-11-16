"""Ordinary2-1 authored coin-ledge/hidden1UP route, strict candidate only."""
from functools import lru_cache
import re
import replay_prince_hidden_ground_up_aligned_7fb_1115 as Previous
from replay_prince_natural_stock_40a_1115 import lua,LuaRuntime
import current_prince_hidden_point67_ace_1115 as Current

C,PIN,W=Previous.C,Previous.PIN,Current.W

def authored(raw):
    data=bytearray()
    for line in(C.R/'src/level_tiles.s').read_text().split('L_GroundArea9:',1)[1].splitlines():
        if'.byte'in line:
            data.extend(int(v,16)for v in re.findall(r'\$([\da-fA-F]{2})',line.split(';')[0]))
            if data[-1]==253:break
    blob=bytes(data);assert C.digest(blob)=='7cf28339e173b9719127b9df1ad2de2ff6597f6c4c65b61ddd6c9e64c42c4e85'and raw.count(blob)==1
    assert blob[14:18]==bytes.fromhex('c303c702')
    return dict(stage='2-1',offset=raw.index(blob),bytes=len(blob),SHA256=C.digest(blob),hidden1UP=[448,80],hidden_coin=[448,144])

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    assert mode=='oneup'and jump==8 and C.digest(raw)==PIN
    text=Previous.controller(raw,mode,jump)
    assert C.digest(text.encode())=='6bf1f9f709d7f5218446c8eb6775ac2e941b62fc693064a512f3d1eb661ff851'
    def change(a,b):
        nonlocal text
        assert text.count(a)==1,a[:100];text=text.replace(a,b,1)
    lines=text.splitlines(keepends=True);i=next(i for i,line in enumerate(lines)if line.startswith('local STOCK='))
    for a,b in(('['+'"x"'+']=1024','['+'"x"'+']=448'),('['+'"y"'+']=128','['+'"y"'+']=80')):
        assert lines[i].count(a)==1;lines[i]=lines[i].replace(a,b,1)
    text=''.join(lines)
    a=text.index('stock.authored_level=');b=text.index('\n',a);text=text[:a]+'stock.authored_level='+lua(authored(raw))+text[b:]
    change('local start=STOCK.kind==3 and late.fourth_practical_cap and s.y>=175 and floor(s)or STOCK.kind==2 and earnedStage and s.x>=1530','local start=true')
    change("stockPhase(STOCK.kind==3 and'approach'or'left-drop',0)","stockPhase('two1-platform-approach',1)")
    change("stock.prince_returns-stock.start.Prince_returns<1100","stock.prince_returns-stock.start.Prince_returns<2600")
    phases=r''' if stock.phase=='two1-platform-approach'then
  pad=1;if s.x>=224 then stock.platform_contact=s;stockPhase('two1-platform-settle',0)end
  assert(age<300,'Bounded ordinary approach to native first brick platform')
 elseif stock.phase=='two1-platform-settle'then
  pad=0;if idle(s)and s.action==0 then stockPhase('two1-platform-up',8)end
  assert(age<160,'Actual idle before original platform climb')
 elseif stock.phase=='two1-platform-up'then
  pad=8
  if s.action==8 and s.y<=114 then stock.platform_mount=s;stockPhase('two1-platform-release',0)end
  assert(age<420,'Original Up must mount the actual first platform')
 elseif stock.phase=='two1-platform-release'then
  pad=0
  if idle(s)and s.action==0 then
   assert(math.abs(s.y-112)<=2,'Actual brick-platform height before legal jump')
   stock.platform_idle=s;stockPhase('two1-platform-wait',0)
  end
  assert(age<180,'Actual platform reach returns to idle')
 elseif stock.phase=='two1-platform-wait'then
  pad=0;local threat=false
  for i=0,5 do local a=stockActor(i);if a.flag~=0 and a.id<7 and a.x<448 then threat=true end end
  if age>=64 and not threat then stock.platform_wait_done=s;stockPhase('two1-platform-left',2)end
  assert(age<360,'Finite genuine early-actor wait on existing platform')
 elseif stock.phase=='two1-platform-left'then
  pad=2;if s.x<=248 then stockPhase('two1-platform-neutral',0)end
  assert(age<120,'Ordinary platform runway setup')
 elseif stock.phase=='two1-platform-neutral'then
  pad=0
  if idle(s)and s.action==0 then
   assert(math.abs(s.y-112)<=2,'Runway retains actual platform support')
   stock.platform_runway=s;stockPhase('two1-platform-run',1)
  end
  assert(age<180,'Actual runway idle after normal Left')
 elseif stock.phase=='two1-platform-run'then
  pad=1
  if s.action==1 and s.mode==1 and s.pose>=6 and s.pose<=13 and s.lock==0 then stock.jump_request=s;stockPhase('two1-platform-A',129)end
  assert(age<100,'Actual original platform running pose gate')
 elseif stock.phase=='two1-platform-A'then
  pad=129
  if s.action==4 then stock.jump_admission=s;stockPhase('two1-platform-flight',1)end
  assert(age<90,'Actual original running jump4 required')
 elseif stock.phase=='two1-platform-flight'then
  pad=s.x<400 and 1 or 0
  if s.x>=400 and floor(s)and idle(s)and s.action==0 then stock.farbank=s;stockPhase('approach',0)end
  assert(age<300,'Bounded legal first-pit jump and actual farbank')
 elseif stock.phase=='coin-ledge-approach'then
  pad=1;if s.x>=432 then stockPhase('coin-ledge-settle',0)end
  assert(age<140,'Ordinary approach to genuinely revealed coin ledge')
 elseif stock.phase=='coin-ledge-settle'then
  pad=0;if idle(s)and s.action==0 then stockPhase('coin-ledge-up',8)end
  assert(age<160,'Actual idle before coin-ledge climb')
 elseif stock.phase=='coin-ledge-up'then
  pad=8
  if s.action==8 and s.y<=114 then stock.coin_mount=s;stockPhase('coin-ledge-release',0)end
  assert(age<420,'Original Up mounts only genuinely revealed native coin block')
 elseif stock.phase=='coin-ledge-release'then
  pad=0
  if idle(s)and s.action==0 then
   assert(math.abs(s.y-112)<=2,'Actual coin ledge height beneath hidden1UP')
   stock.coin_cap=s;stockPhase('approach',0)
  end
  assert(age<180,'Actual coin-ledge reach release')
 elseif stock.phase=='left-drop'then'''
    change(" if stock.phase=='left-drop'then",phases)
    old="if age>100 and floor(s)and idle(s)then stock.landing=s;final=s;finish(false,'Directed grounded Up completed without hidden1UP birth')end"
    new=r'''if age>100 and floor(s)and idle(s)then
   stock.landing=s
   if not stock.coin_revealed then
    local t=tile(448,144);assert(t~=0 and t~=95 and t~=96 and read(0xef36+t)&1~=0,'Actual first Up reveals solid native coin block')
    stock.coin_revealed={state=s,tile=t};stockPhase('coin-ledge-approach',0)
   else final=s;finish(false,'Coin-ledge Up completed without hidden1UP birth')end
  end'''
    change(old,new)
    # Real title/options/level setting for the future native replay. The
    # source driver separately declares its compiled input-mailbox unit.
    change('  press(16,54)\n  assert(read(0x7307)==2',
        "  press(4,34);press(16,54);assert(read(0x7307)==4,'Actual Options page')\n  press(4,34);press(4,34);press(16,54);assert(read(0x7307)==6,'Actual level settings page')\n  press(4,34);for i=1,4 do press(1,34)end\n  assert(read(0x7ffb)==0 and read(0x7ffc)==36,'Only actual2-1 level setting changed')\n  press(64,54);press(64,54);press(16,54)\n  assert(read(0x7307)==2")
    change("assert(read(0x7ffb)==0 and read(0x7ffc)==0,'No invincibility or level cheats')",
        "assert(read(0x7ffb)==0 and read(0x7ffc)==36,'Actual2-1 setting and all gameplay cheats off');assert(read(0x764)==1 and read(0x761)==0,'Actual2-1 stage')")
    # Aggregate only state changes/phase milestones; never per-frame files.
    b=dict(W.Symbols.bundle(),raw=raw);direction=W.address(b,'Enemy_MovingDir')
    observer=r'''
stock.stage2_actor_milestones={};stock.stage2_hp_writes={}
local function stage2Actors()
 local rows={};for i=0,5 do local a=stockActor(i);if a.flag~=0 then a.direction=read(@DIR@+i);rows[#rows+1]=a end end;return rows
end
emu.addMemoryCallback(guarded(function(at,value)
 if not stock.active or not mapped(0xc6cf,2)or source(0x6cf)==value or #stock.stage2_hp_writes>=8 then return end
 local cpu=emu.getState();stock.stage2_hp_writes[#stock.stage2_hp_writes+1]={reported_PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],before=source(0x6cf),after=value,state=stockState(),actors=stage2Actors(),phase=stock.phase}
end),emu.callbackType.write,0xc6cf)
'''.replace('@DIR@',str(direction))
    change('local function naturalStockTick()\n',observer+'\nlocal function naturalStockTick()\n')
    change(' local age=stock.prince_returns-stock.since\n',
        " local age=stock.prince_returns-stock.since\n if stock.last_stage2_phase~=stock.phase and #stock.stage2_actor_milestones<32 then stock.last_stage2_phase=stock.phase;stock.stage2_actor_milestones[#stock.stage2_actor_milestones+1]={phase=stock.phase,state=s,actors=stage2Actors(),coin=tile(448,144),hidden=tile(448,80)}end\n")
    LuaRuntime().compile(text)
    assert not any(token in text for token in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),required_native_variant=3,
        stage='2-1',authored_hidden1UP=[448,80],authored_hidden_coin=[448,144],
        actual_native_level_menu_controls=True,all_gameplay_cheats_off=True,
        genuine_actor_birth_mature_overlap_erase_delayed_INC_cue64_and25returns_required=True,
        no_gameplay_seeds=True,no_helpers_added=True,outputs=0,Mesen=False)
