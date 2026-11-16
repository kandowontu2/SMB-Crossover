"""Walk off the measured left row edge, return underneath, native crouch-A."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_supermaaa_stock_91dc_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='97c8f76baba1e0ed133de8fac75b6aeb1a0e37d284852d8dfec311e19e5bbb1b'
CONTROL="""local function groundStar(c)
 local q=stock.star_ground
 if not q and(stock.phase=='travel'or stock.phase=='align')and c.x>=C.target_x-56 and c.y<160 and c.grounded then
  local edge=C.target_x;local row={}
  for _=1,12 do local tile=c.block(edge-16,C.target_y);row[#row+1]={x=edge-16,tile=tile};if tile==0 then break end;edge=edge-16 end
  local clear=edge-24
  assert(clear>c.camera+1 and c.block(clear,208)~=0 and c.block(clear+13,C.target_y)==0,'Actual visible supported left row-clear column')
  q={phase='off',since=guestReturns,edge=edge,clear=clear,row=row,roof=state()};stock.star_ground=q
 end
 if not q or q.phase=='done'then return end
 assert(guestReturns-q.since<400,'One actual row drop and ground return')
 if q.phase=='off'then
  if c.grounded and c.y>=160 and c.x<q.edge then q.landing=state();q.phase='back'else return{left=true,b=true}end
 end
 local center=C.target_x-6;assert(center>c.camera+1,'Actual Star column remains in camera')
 local v=c.vx<128 and c.vx or c.vx-256;local stop=c.x+v*math.abs(v)/32
 if c.grounded and c.y>=160 and math.abs(c.x-center)<=2 and math.abs(v)<=1 and not lastA then
  q.stand=state();q.phase='done';stock.phase='align';stock.phaseStart=guestReturns;stock.settle=0;return{}
 end
 return{right=stop<center-1,left=stop>center+1,b=c.x<center-64}
end
local function chooseStock(c)
 local ground=groundStar(c);if ground then return ground end
"""


@lru_cache(maxsize=1)
def controller(raw,key='star'):
    assert key=='star'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key);old='local function chooseStock(c)\n';assert text.count(old)==1;text=text.replace(old,CONTROL,1)
    old='   b={a=true}';assert text.count(old)==1;text=text.replace(old,'   b={a=true,down=true}',1)
    old='  return{a=guestReturns-stock.headAt<24}';assert text.count(old)==1;text=text.replace(old,'  return{a=guestReturns-stock.headAt<24,down=guestReturns-stock.headAt<24}',1)
    b=Current.bundle(raw);h={};pc,at=W.address(b,'MarioSourcePowerupCollision'),W.location(b,'MarioSourcePowerupCollision')
    timer,music=W.address(b,'StarInvincibleTimer'),W.address(b,'AreaMusicQueue');pattern=bytes((0xa9,35,0x8d,timer&255,timer>>8,0xa9,64,0x8d,music&255,music>>8,0x60))
    hits=[i for i in range(120-len(pattern))if raw[at+i:at+i+len(pattern)]==pattern];assert len(hits)==1
    delta=hits[0];assert raw[at+delta-4:at+delta-1]==bytes.fromhex('c903f0');bank=(at-16)//8192
    h=dict(pc=pc+delta,offset=at+delta-16,bank=bank,bytes=list(raw[at+delta:at+delta+8]),bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    observer='C.hooks.ActualStarEffect='+Text.lua(h)+"\n"+"""hook('MarioSourceInjuryStart',function()
 if not food.M_scope_passed or stock.injury then return end
 local cpu=emu.getState();local i=r('ObjectOffset');local a=actor(i);a.direction=r('Enemy_MovingDir',i)
 stock.injury={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],state=state(),actor=a,player_box=box('BoundingBox_UL_Corner'),enemy_box=box('EnemyBoundingBoxCoord',i)}
end)
hook('ActualStarEffect',function()
 if not pendingStock then return end;local cpu=emu.getState();assert(cpu['cpu.ps']&1==0,'Actual kind2 CMP3 C0')
 stock.native_effect={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],P=cpu['cpu.ps'],state=state()}
end)
emu.addMemoryCallback(guard(function(_,v)
 if pendingStock and v==35 then local cpu=emu.getState();assert(cpu['cpu.ps']&1==0,'Actual Star timer35 writerC0')
  stock.star35_writer={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],P=cpu['cpu.ps'],value=v,state=state()}
 end
end),emu.callbackType.write,C.ram.StarInvincibleTimer)
"""
    marker="hook('GameLoop',function()";assert text.count(marker)==1;text=text.replace(marker,observer+marker,1)
    old=" assert(i==5 and a.flag==1 and a.id==46 and a.kind==C.stock_type and a.state>=128,'Actual mature expected stock')"
    new=" stock.first_admission=stock.first_admission or{pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],state=state(),actor=a,player_box=box('BoundingBox_UL_Corner'),item_box=box('EnemyBoundingBoxCoord',i)}\n"+old
    assert text.count(old)==1;text=text.replace(old,new,1)
    old="assert(r('StarInvincibleTimer')>0 and r('PlayerStatus')==1 and r('NumberofLives')==2,'Real Star and firstM retained')"
    new="assert(stock.native_effect and stock.star35_writer and r('StarInvincibleTimer')>0 and r('PlayerStatus')==1 and r('NumberofLives')==2,'Actual StarC0/35writer, retainedM and life2')"
    assert text.count(old)==1;text=text.replace(old,new,1);LuaRuntime().compile(text);return text


def metadata(raw,key='star'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),ground_star_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_rooftop_head_negative='b8bee6225f2fe7d0e07ac919fcd00a24d452fbd468564962c093a59abbc57e5d',
        ordinary_change='Actual visible left edge walkoff, supported ground return below target, original Down+A; actual Star C0/35 writer')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
