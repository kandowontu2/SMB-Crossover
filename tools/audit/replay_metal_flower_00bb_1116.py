"""Exact00bb natural original weapon pickup and real upgraded-shot use."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_metal_life_00bb_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='59e4c1093d116349c5784c70abc9a76ab6847e19c06b0bb43d553096f48bb534'


def once(text,old,new):assert text.count(old)==1,old;return text.replace(old,new,1)


@lru_cache(maxsize=1)
def bindings(raw):
    assert digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    c=deepcopy(Previous.bindings(raw,'oneup'));c.update(kind='flower',stock_type=1,target_x=1248,target_y=144)
    b=Current.bundle(raw);_,_,extra,_=Current.payload(raw)
    for name in('HandleEnemyFBallCol','ShellOrBlockDefeat'):
        pc,at=W.address(b,name),W.location(b,name);bank=(at-16)//8192
        c['hooks'][name]=dict(pc=pc,space='prg',bank=bank,offset=at-16,bytes=list(raw[at:at+8]),bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    needle=b'\x20'+W.address(b,'HandleEnemyFBallCol').to_bytes(2,'little');hits=[i for i in range(len(extra)-16)if extra[i:i+3]==needle];assert len(hits)==1
    ret=0xd900+hits[0]+3;assert extra[hits[0]+3:hits[0]+11]==bytes.fromhex('ae29c8a9009d10c5')
    c['shot_return']=ret
    pc=ret+8;at=pc-0xd900;c['hooks']['ShotRetired']=dict(pc=pc,space='wram',bank=2,offset=2*8192+(pc&8191),bytes=list(extra[at:at+8]))
    return c


@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower';c=bindings(raw);_,body=Previous.controller(raw,'oneup').split('\n',1)
    body=once(body,"local M={phase=0};local stock={phase='pipes',pipe=1}","local M={phase=0};local stock={phase='pipes',pipe=1};local shot={births={},motion={},contacts={}}\nlocal shotDrive,observeShots,shotEndpoint,pendingShot")
    body=once(body,'physical_frames=frame,input_polls=polls,M=M','physical_frames=frame,input_polls=polls,shot=shot,M=M')
    body=once(body,' if C.stock_type==2 then\n  stock.gap',' if C.stock_type==1 then\n  stock.gap')
    body=once(body,'if stock.gap<=2 then','if stock.gap<=1 then')
    body=once(body,'local center=C.target_x-6','local center=C.target_x+4')
    body=once(body,"if C.stock_type==3 then assert(stock.authored_tile==96,'Real hidden60')end","assert(stock.authored_tile==193,'Actual native Flower blockC1')")
    body=once(body,"assert(src(0x5d0)==M.earned.armor and src(0x718)==M.earned.weapon and r('PlayerStatus')==M.earned.power,'Earned Metal armor/weapon/form retained')","assert(src(0x5d0)==M.earned.armor and src(0x718)==(stock.collected and 128 or M.earned.weapon)and r('PlayerStatus')==(stock.collected and 2 or M.earned.power),'Real earned Metal armor/weapon/form retained')")
    body=once(body,' if stock.collected then buttons={};return end',' if stock.flower_scope_passed then buttons=shotDrive(context());return end\n if stock.collected then buttons={};return end')
    body=once(body,"stock.phase='collect';local dx=a.x-c.x;buttons={right=dx>3,left=dx< -3,b=true}\n  if c.grounded and a.y<c.y-12 and math.abs(dx)<48 and(not stock.chaseJump or stepOK-stock.chaseJump>55)then stock.chaseJump=stepOK end\n  if stock.chaseJump and stepOK-stock.chaseJump<35 then buttons.a=true end", """stock.phase='collect'
  if not stock.Flaunch then
   if c.x>1180 then buttons={left=true,b=true};return end
   if not c.grounded then buttons={b=true};return end
   stock.Flaunch={since=stepOK,request=state()}
  end
  assert(stepOK-stock.Flaunch.since<120,'One retained ordinary Flower retreat/running jump')
  buttons={right=c.x<1252,b=true,a=stepOK-stock.Flaunch.since<40}""")
    body=once(body,'local function endpoint()\n','local function endpoint()\n if stock.flower_scope_passed then shotEndpoint();return end\n')
    body=once(body,"assert(src(0x5d0)==M.earned.armor and src(0x718)==M.earned.weapon and r('PlayerStatus')==M.earned.power,'Real inventory retained after credit')","assert(src(0x5d0)==M.earned.armor and src(0x718)==128 and r('PlayerStatus')==2,'Original armor retained and real item0 weapon/native tier2 earned')")
    body=once(body,"if C.stock_type==2 then assert(stock.native_effect and stock.star35_writer and r('StarInvincibleTimer')>0,'Actual native StarC0/35/music')else assert(stock.life_credit and r('NumberofLives')==3,'Actual delayed life3')end","assert(stock.native_item0 and r('GuestPowerupActive')==0 and r('GuestPowerupAge')==0,'Immediate original item0, no hosted growth')")
    body=once(body,"finish(true,'Natural Metal M then '..C.kind..' and25 accepted returned movement+HostStep at completedMain')","stock.flower_scope_passed=true;stock.flower_earned=state();shot.since=originalReturns;buttons={b=true}")
    body=once(body,"if kind==0 then assert(src(0x5d0)==128 and r('PlayerStatus')==1,'Actual Metal armor effect')elseif kind==2 then assert(r('StarInvincibleTimer')==35 and r('AreaMusicQueue')==64,'Actual Star35/music64')end","if kind==0 then assert(src(0x5d0)==128 and r('PlayerStatus')==1,'Actual Metal armor effect')elseif kind==1 then assert(src(0x5d0)==128 and src(0x718)==128 and src(0x717)==0 and src(0x43c)==0 and r('PlayerStatus')==2,'Actual original weapon item0 and independent armor');q.native_item0=true end")
    helper="""local function projectile(i)return{slot=i,active=src(0x510+i),type=src(0x528+i),x=src(0x480+i)+256*src(0x498+i),y=src(0x4b0+i),pageY=src(0x4c8+i),vx=src(0x558+i),vy=src(0x570+i),life=src(0x600+i),state=src(0x4e0+i)}end
observeShots=function()
 if not stock.collected then return end
 for i=2,3 do local p=projectile(i)
  if p.active>=128 and p.type==129 then
   local key='slot'..i;shot.births[key]=shot.births[key]or{state=state(),projectile=p}
   local first=shot.births[key];if p.x~=first.projectile.x or p.y~=first.projectile.y then shot.motion[key]=shot.motion[key]or{state=state(),projectile=p}end
  end
 end
end
shotDrive=function(c)
 assert(originalReturns-shot.since<1000 and c.x<1900,'Finite original upgraded-shot use')
 if not shot.pitPassed then
  if not shot.jump and c.x>=1344 and c.grounded and not lastA then shot.jump={since=stepOK,request=state()};assert(c.block(1376,208)==0 and c.block(1424,208)~=0,'Actual second pit')end
  if shot.jump then
   if c.x>=1424 and c.grounded then shot.pitPassed=state();return{right=true,b=true}end
   return{right=true,b=true,a=stepOK-shot.jump.since<35}
  end
 end
 return{right=true,b=true}
end
shotEndpoint=function()
 if pendingMain or pendingMove or pendingStep or pendingFrame or pendingShot then return end
 for _,hit in ipairs(shot.contacts)do
  if hit.defeated and hit.retired and shot.births['slot'..hit.shot.slot]and shot.motion['slot'..hit.shot.slot]then
   assert(mainEntries==mainReturns and originalEntries==originalReturns and moveEntries==moveReturns and stepEntries==stepReturns)
   assert(stock.resumed_original==25 and stock.resumed_move==25 and stock.resumed_step==25 and src(0x5d0)==128 and src(0x718)==128 and r('PlayerStatus')==2 and r('NumberofLives')==2)
   shot.actual_Main_return={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],state=state()};finish(true,'Genuine Metal M/Flower/1000/25 and moving original type81 shot defeats a natural native enemy');return
  end
 end
end
hook('HandleEnemyFBallCol',function()
 if not stock.collected then return end
 local cpu=emu.getState();local sp=cpu['cpu.sp'];local ret=read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1
 if ret~=C.shot_return then return end
 local i=src(0x829);assert(i==2 or i==3);local p=projectile(i);assert(p.active>=128 and p.type==129 and src(0x718)==128)
 local enemy=actor(cpu['cpu.x']);local q={pc=cpu['cpu.pc'],sp=sp,state=state(),shot=p,enemy=enemy};shot.contacts[#shot.contacts+1]=q;assert(#shot.contacts<=4);pendingShot=q
 returning(function(t)q.returned={pc=t.pc,sp=t.sp,state=state(),enemy=actor(enemy.slot)};q.defeated=q.defeat_call and(q.returned.enemy.flag==0 or q.returned.enemy.state&32~=0)end)
end)
hook('ShellOrBlockDefeat',function()if pendingShot then local cpu=emu.getState();assert(cpu['cpu.x']==pendingShot.enemy.slot);pendingShot.defeat_call={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],state=state()}end end)
hook('ShotRetired',function()if pendingShot then local q=pendingShot;assert(src(0x510+q.shot.slot)==0);q.retired={state=state(),projectile=projectile(q.shot.slot)};pendingShot=nil end end)
"""
    body=once(body,'C.hooks.OriginalFrame=',helper+'\nC.hooks.OriginalFrame=')
    body=once(body,'originalReturns=originalReturns+1;pendingFrame=nil end)','originalReturns=originalReturns+1;pendingFrame=nil;observeShots()end)')
    text='local C='+Text.lua(c)+'\n'+body;LuaRuntime().compile(text)
    assert not any(n in text for n in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'));return text


def metadata(raw,key='flower'):
    return dict(ROM_SHA256=PIN,controller_SHA256=digest(controller(raw).encode()),factory_SHA256=digest(Path(__file__).read_bytes()),
        current_facade_SHA256=digest(Path(Current.__file__).read_bytes()),parent_factory_SHA256=BASE_SHA,
        scope='Actual00bb compiled Metal/M prefix/natural mature Flower original item0/1000/25 returned MsFrame+Movement+HostStep and real moving type81/native enemy defeat',
        native_shot_caller_return=bindings(raw)['shot_return'],gameplay_seeds=0,game_state_writes=False,outputs=0,Mesen=False)


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
