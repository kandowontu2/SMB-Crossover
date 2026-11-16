"""Use the clear right face of the Flower row, away from its falling Goomba."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_smb1_toad_flower_emerge_91dc_1116 as Previous

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='c83cdd3018a37014bdabb51ebd4a22ab2ecf710e7a07d8eab467e5d26a96c33d'


@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key)
    old="""   local edge=C.target_x;local row={}
   for _=1,8 do
    local tile=c.block(edge-16,C.target_y);row[#row+1]={x=edge-16,tile=tile}
    if tile==0 then break end;edge=edge-16
   end
   local clear=edge-24;assert(clear>c.camera,'Actual left-side head clearance remains visible')"""
    new="""   local edge=C.target_x+16;local row={}
   for _=1,8 do
    local tile=c.block(edge,C.target_y);row[#row+1]={x=edge,tile=tile}
    if tile==0 then break end;edge=edge+16
   end
   local clear=edge+16
   assert(clear>c.camera and clear<1376 and c.block(clear,208)~=0,'Actual right-face ground before second pit')"""
    assert text.count(old)==1;text=text.replace(old,new,1)
    Previous.Previous.Previous.Previous.Previous.LuaRuntime().compile(text);return text


def metadata(raw,key='flower'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),right_mount_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_falling_Goomba_jump_negative='d2beea9cf46604e5646a16c9a4cbb5135d1cd7d087b7d0a70bcb04d7f35b7355',
        ordinary_change='Actual right row edge and supported clear ground; avoid measured left-face fallingGoomba, same original verticalA/onto-row controls')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
