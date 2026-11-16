"""Strict cb95 ordinary hidden1UP/Star after the frozen native-qualified M."""
from pathlib import Path
from functools import lru_cache
from types import SimpleNamespace
from copy import deepcopy
import replay_gb_pit_right_clear_stock_1116 as Prefix
import replay_gb_pit_flower_1116 as Config

R,ROM,W,N,H,Current=Prefix.R,Prefix.ROM,Prefix.W,Prefix.N,Prefix.H,Prefix.Current
PIN=Current.Rogue.CANDIDATE
BASE_SHA='6335c0798811bfc6c034fa9f0ab9863864f79aa9ba7886a668a1a3e57dbcad2d'
M_CONTROL_SHA='cbf5a81a1d13db6a7f194a78498ff4d8fd636895f6147dd60998a40361804ed5'
CONFIG_SHA='611fe3446205a34a2e043cc0084f5e83eb22006b228b44598094e2181247403b'
TEMPLATE=Config.TEMPLATE
TEMPLATE_SHA='5af8cb1b2aa3820b723c71e3612c0df2440098bfa4ea94159d6b8893520b507b'
KINDS={'oneup':(3,1024,128),'star':(2,1616,144)}

def once(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)

@lru_cache(maxsize=2)
def bindings(raw,kind='oneup'):
    assert H(raw)==PIN,'Actual owning cb95 GB Pit stock only'
    assert H(Path(Config.__file__).read_bytes())==CONFIG_SHA
    t,x,y=KINDS[kind];c=deepcopy(Config.bindings(raw));c.update(kind=kind,stock_type=t,target_x=x,target_y=y)
    b=Current.bindings(raw)['bundle'];pc,at=W.address(b,'MarioSourcePowerupCollision'),W.location(b,'MarioSourcePowerupCollision')
    for name in('MmBlockAttack','MmSavedPlayer','MmSlot','MmBulletType','MmBulletX','MmBulletPage','MmBulletY'):c['ram'][name]=W.address(b,name)
    timer=c['ram']['StarInvincibleTimer'];needle=b'\xa9\x23\x8d'+timer.to_bytes(2,'little')+b'\xa9\x40'
    hits=[i for i in range(120-len(needle))if raw[at+i:at+i+len(needle)]==needle];assert len(hits)==1
    for name,n in(('StarBefore',hits[0]),('StarAfter',hits[0]+5)):
        bank=(at-16)//8192;c['hooks'][name]=dict(pc=pc+n,offset=at+n-16,bank=bank,bytes=list(raw[at+n:at+n+8]),bank_SHA256=H(raw[16+bank*8192:16+(bank+1)*8192]))
    return c

@lru_cache(maxsize=2)
def controller(raw,kind='oneup'):
    assert kind in KINDS and H(Path(Prefix.__file__).read_bytes())==BASE_SHA
    assert H(Prefix.CONTROL.read_bytes())==M_CONTROL_SHA and H(TEMPLATE.read_bytes())==TEMPLATE_SHA
    _,body=Prefix.controller(raw,'mushroom').split('\n',1)
    body=once(body,'local function read(at)',"local stock={phase='travel'};food.stock=stock\nlocal function read(at)")
    body=once(body,"kind='mushroom'",'kind=C.kind')
    body=once(body,"and r('NumberofLives')==2 and","and r('NumberofLives')==(stock.life_credit and 3 or 2)and")
    body=once(body,'local function drive()\n','local stockDrive\nlocal function drive()\n if food.M_scope_passed then stockDrive();return end\n')
    body=once(body,'local function endpoint()\n','local function foodEndpoint()\n if food.M_scope_passed then return end\n')
    body=once(body,"  finish(true,'Natural GB Pit M/1000/60tick tier1 and25 returned Pit movements at completedMain')",
        "  assert(food.actual_head_setup and food.actual_head and food.actual_head.returned,'Frozen genuineM head proof');food.M_scope_passed=true;stock.since=guestReturns;buttons={}")
    body=once(body,"hook('HandlePowerUpCollision',function()\n","hook('HandlePowerUpCollision',function()\n if food.M_scope_passed then return end\n")
    body=once(body,"hook('GuestPowerupUpdate',function()\n","hook('GuestPowerupUpdate',function()\n if food.M_scope_passed then return end\n")
    body=once(body,"frame<5000 and mainEntries<3000,'Bounded firstM fixture'","frame<15000 and mainEntries<6500,'Bounded actual cb95 GB Pit natural stock'")
    stock=TEMPLATE.read_text().replace("hook('MarioSourcePowerupUpdate'","hook('GuestPowerupUpdate'").replace('SMB1 Toad','GB Pit')
    stock=once(stock,'  if a.state<128 then return{}end',r'''  if a.state<128 then
   local goal=a.x-32
   stock.emergence_follow=stock.emergence_follow or{first={state=state(),actor=a,goal=goal,camera=c.camera},samples={}}
   local q=stock.emergence_follow;q.last={state=state(),actor=a,goal=goal,camera=c.camera}
   if #q.samples<8 and(not q.last_sample or guestReturns-q.last_sample>=8)then q.samples[#q.samples+1]=q.last;q.last_sample=guestReturns end
   return{right=c.x<goal,left=c.x>goal+2}
  end''')
    stock=once(stock,"  stock.phase='collect';local dx=a.x-c.x;local b={right=dx>3,left=dx< -3}",r'''  stock.phase='collect';local dx=a.x-c.x;local b={right=dx>3,left=dx< -3}
  stock.chase_trace=stock.chase_trace or{};stock.chase_min_y=math.min(stock.chase_min_y or c.y,c.y)
  if #stock.chase_trace<8 and(not stock.chase_trace_at or guestReturns-stock.chase_trace_at>=8)then
   stock.chase_trace[#stock.chase_trace+1]={state=state(),actor=a,camera=c.camera,lastA=lastA,player_box=box('BoundingBox_UL_Corner'),item_box=box('EnemyBoundingBoxCoord',a.slot)};stock.chase_trace_at=guestReturns
  end''')
    stock=once(stock,"  if c.grounded and a.y<c.y-12 and math.abs(dx)<48 and(not stock.chaseJump", "  if C.stock_type~=3 and c.grounded and a.y<c.y-12 and math.abs(dx)<48 and(not stock.chaseJump")
    stock=once(stock,'  if stock.chaseJump and guestReturns-stock.chaseJump<24 then b.a=true end','  if C.stock_type~=3 and stock.chaseJump and guestReturns-stock.chaseJump<24 then b.a=true end')
    stock=once(stock,"stock.born={state=state(),actor=a}end", "stock.born={state=state(),actor=a};if stock.actual_head then stock.actual_head.first_completed_Main_after_trigger=state()end end")
    stock=once(stock,'or pendingMain or pendingGuest or pendingStock then return end','or pendingMain or pendingGuest or pendingStock or pendingPit then return end')
    stock=once(stock,'if not stock.resumeBase then stock.resumeBase=guestReturns end','if not stock.resumeBase then stock.resumeBase=guestReturns;stock.pitBase=pitReturns end')
    stock=once(stock,"assert(stock.sound.writes20>0 and mainEntries==mainReturns and guestEntries==guestReturns,'Actual cue and balanced Main/native movement')",
        "assert(stock.sound.writes20>0 and mainEntries==mainReturns and guestEntries==guestReturns and pitEntries==pitReturns and pitReturns-stock.pitBase>=25,'Actual cue and25 balanced returned movement/ability atMain');assert(stock.actual_head_setup and stock.actual_head and stock.actual_head.returned,'Actual authored head→stock setup')")
    stock=once(stock,"elseif C.stock_type==2 then assert(r('StarInvincibleTimer')>0", "elseif C.stock_type==2 then assert(stock.star_before and stock.star_write,'Actual inherited Star C0 and35 writer');assert(r('StarInvincibleTimer')>0")
    observers=r'''local stockHeadPending
hook('PlayerHeadCollision',function()
 if not food.M_scope_passed or stock.born then return end
 local s=state();if s.x<C.target_x-24 or s.x>C.target_x+16 or s.y>=176 then return end
 assert(not stockHeadPending);local z=emu.getState();local sp=z['cpu.sp']
 local rp=(read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1)&65535;local map=emu.convertAddress(rp)
 local marker=r('MmBlockAttack');local saved={};for i=0,6 do saved[#saved+1]=r('MmSavedPlayer',i)end
 local caller={PC=rp,SP=(sp+2)&255,physical=map and map.address or-1,memType=map and map.memType or-1,bytes={}}
 for i=-3,7 do caller.bytes[#caller.bytes+1]=read(rp+i)end
 local q={PC=z['cpu.pc'],SP=sp,A=z['cpu.a'],X=z['cpu.x'],Y=z['cpu.y'],query_state=s,saved_input=r('SavedJoypadBits'),caller=caller,
  MmBlockAttack=marker,classification=marker==1 and'projectile block transaction with borrowed query coordinates'or'native head dispatcher without projectile marker',
  saved_player=saved,restored_player=marker==1 and{x=saved[1]+256*saved[2],y=saved[3],high=saved[4],size=saved[5],crouch=saved[6],vy=saved[7]}or s,
  projectile={slot=r('MmSlot'),kind=r('MmBulletType'),x=r('MmBulletX')+256*r('MmBulletPage'),y=r('MmBulletY')}};stock.actual_head=q
 stockHeadPending=returning(function(t)q.returned={PC=t.pc,SP=t.sp,state=state()};stockHeadPending=nil end)
end)
hook('SetupPowerUp',function()
 if not stockHeadPending or stock.born then return end
 local z=emu.getState();stock.actual_head_setup={PC=z['cpu.pc'],SP=z['cpu.sp'],A=z['cpu.a'],X=z['cpu.x'],Y=z['cpu.y'],state=state(),inside_actual_head=true}
end)
hook('StarBefore',function()
 if C.stock_type~=2 or not pendingStock then return end
 local z=emu.getState();assert(z['cpu.ps']&1==0 and r('PowerUpType',z['cpu.x'])==2,'Actual inherited Star branch C0')
 stock.star_before={PC=z['cpu.pc'],SP=z['cpu.sp'],C=z['cpu.ps']&1,state=state()}
end)
hook('StarAfter',function()
 if C.stock_type~=2 or not pendingStock then return end
 local z=emu.getState();assert(stock.star_before and r('StarInvincibleTimer')==35 and z['cpu.a']==35,'Actual Star35 writer completed')
 stock.star_write={PC=z['cpu.pc'],SP=z['cpu.sp'],A=z['cpu.a'],state=state()}
end)
hook('InjurePlayer',function()
 if not food.M_scope_passed or stock.injury then return end
 local z=emu.getState();local i=r('ObjectOffset');stock.injury={PC=z['cpu.pc'],SP=z['cpu.sp'],state=state(),actor=actor(i),player_box=box('BoundingBox_UL_Corner'),enemy_box=box('EnemyBoundingBoxCoord',i)}
end)
'''
    body=once(body,"hook('GameLoop',function()",stock+'\n'+observers+"hook('GameLoop',function()")
    text='local C='+Prefix.M.Previous.Text.lua(bindings(raw,kind))+'\n'+body
    Prefix.M.Previous.LuaRuntime().compile(text)
    assert not any(v in text for v in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'));return text

def metadata(raw,kind='oneup'):
    return dict(ROM_SHA256=PIN,kind=kind,factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw,kind).encode()),
        M_factory_SHA256=BASE_SHA,M_control_SHA256=M_CONTROL_SHA,stock_template_SHA256=TEMPLATE_SHA,hooks=bindings(raw,kind)['hooks'],
        retained_stationary_emergence_L_negative='6fc6f70abbf6fcc11e9b60ec5803b7af2fbedc84bd4a210ada9a8275b189a09b',
        retained_ground_chase_L_negative='30052bdad5602ac15448e368383dcf5c969b8b3cc8396b97e96ae27fe269dde2',
        retained_chase_trace_negative='6378731cacc250c6ef5b6531f7120354584f18c5476543b962833358e24956f9',
        ordinary_control_delta='Safe32px emergence approach then ground-only1UPchase; Star keeps ordinary jump. Mature-only collector and actualcredit25 unchanged. Trigger records body/projectile classification, caller and actualrestoredhero.',
        scope='Actualcb95 frozen genuineM+25, authored natural stock via originalbody/arrow blockdispatch, birth/maturity/positivephysicalcontact/erase/cue, actualdelayedscore orlifecredit, then25returned ExpandedMovement+PitFlight atactualMain',
        gameplay_seeds=0,game_bytes_changed=0,outputs=0,Mesen=False)

def family(kind='oneup'):return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,kind),metadata=lambda raw,key:metadata(raw,kind))
