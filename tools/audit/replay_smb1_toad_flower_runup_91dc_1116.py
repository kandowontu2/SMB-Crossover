"""Original native running-jump class funds the real right-face Flower mount."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_smb1_toad_flower_right_mount_91dc_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='ae9c837befedc084f7844a14116eab6de14e6eddc707bcf9f570fee7cbc840cd'


@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key);_,body=text.split('\n',1)
    a=body.index("  if q.phase=='back'then\n");z=body.index("  assert(q.phase=='onto','Actual mount phase')",a)
    body=body[:a]+"""  assert(c.x<1376,'Actual supported runway before pit1392')
  if q.phase=='back'then
   q.phase='out';q.out_request=state()
  end
  if q.phase=='out'then
   if c.x>=q.edge+72 and c.grounded then q.phase='charge';q.reverse=state();return{left=true,b=true}end
   return{right=true}
  elseif q.phase=='charge'then
   local v=c.vx<128 and c.vx or c.vx-256
   if c.x<=q.edge+40 and v<=-28 and c.grounded and not lastA then
    q.phase='onto';q.takeoff=guestReturns;q.stand=state();q.native_speed_class=r('Player_XSpeedAbsolute')
    assert(q.native_speed_class>=28,'Actual original native running-jump class4')
    return{left=true,b=true,a=true}
   end
   assert(c.x>=q.edge+24,'Real runway must fund native run class before row')
   return{left=true,b=true}
  end
"""+body[z:]
    c=deepcopy(Current.bindings(raw));h=c['hooks']['BmNativeMovement'];b=Current.bundle(raw)
    c.update(kind='flower',stock_type=1,target_x=1248,target_y=144,movement_hex=raw[16+h['offset']:16+h['offset']+64].hex())
    for name in('ObjectOffset','Enemy_MovingDir','Enemy_Y_HighPos','Player_XSpeedAbsolute'):c['ram'][name]=W.address(b,name)
    name='MarioSourceInjuryStart';at,pc=W.location(b,name),W.address(b,name);bank=(at-16)//8192
    c['hooks'][name]=dict(pc=pc,offset=at-16,bank=bank,bytes=list(raw[at:at+8]),bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    text='local C='+Text.lua(c)+'\n'+body
    LuaRuntime().compile(text);return text


def metadata(raw,key='flower'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),runup_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_standing_jump_mount_negative='ca24962bd5e95cfb342e1861071bc163c0fa9766ddd4333e6e7971808d5bf6f7',
        ordinary_change='Real supported right runway and actual native speed28 jump class4; fresh left+A/B, no physics writes')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
