"""Ordinary native Toad mount preparation during genuine Flower emergence."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_smb1_toad_flower_mount_91dc_1116 as Previous

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='8d0463b64f2156bafd1256f208e077c104f45e072caa2e6c0b7111e6be95a8d3'


@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key);_,body=text.split('\n',1)
    config=deepcopy(Current.bindings(raw));h=config['hooks']['BmNativeMovement']
    config.update(kind='flower',stock_type=1,target_x=1248,target_y=144,movement_hex=raw[16+h['offset']:16+h['offset']+64].hex())
    b=Current.bundle(raw)
    for name in('ObjectOffset','Enemy_MovingDir','Enemy_Y_HighPos'):config['ram'][name]=W.address(b,name)
    name='MarioSourceInjuryStart';at,pc=W.location(b,name),W.address(b,name);bank=(at-16)//8192
    config['hooks'][name]=dict(pc=pc,offset=at-16,bank=bank,bytes=list(raw[at:at+8]),bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    old='  if a.state<128 then return{}end';assert body.count(old)==1
    body=body.replace(old,'  -- Ordinary preparation may move while the native item emerges; its real collector still requires state>=128.',1)
    observer="""hook('MarioSourceInjuryStart',function()
 if not food.M_scope_passed or stock.injury then return end
 local cpu=emu.getState();local i=r('ObjectOffset');local a=actor(i)
 a.direction=r('Enemy_MovingDir',i);a.high=r('Enemy_Y_HighPos',i)
 stock.injury={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],state=state(),actor=a,ObjectOffset=i,player_box=box('BoundingBox_UL_Corner'),enemy_box=box('EnemyBoundingBoxCoord',i)}
end)
"""
    marker="hook('GameLoop',function()";assert body.count(marker)==1;body=body.replace(marker,observer+marker,1)
    text='local C='+Previous.Previous.Previous.Previous.Text.lua(config)+'\n'+body
    Previous.Previous.Previous.Previous.LuaRuntime().compile(text);return text


def metadata(raw,key='flower'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),emergence_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_mature_wait_damage_negative='670ea985875d897ebe2a7fc477ef5a462db6099eaa652f3e523f664d554e5769',
        ordinary_change='Prepare actual left-edge mount during real emergence, without altering mature>=128 physical admission or growth/credit/25 gates')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
