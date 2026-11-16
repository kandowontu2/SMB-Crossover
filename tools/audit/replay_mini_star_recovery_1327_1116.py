"""Natural Mini Star after actual ordinary injury and completed recovery."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_mini_star_support_1327_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,H,Current=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.H,Previous.Current
BASE_SHA='43499d81eb1cf9488e02c17de2ea9e865c424ebe1d3ec855cacd71901bfa9f3a'

def once(text,old,new):assert text.count(old)==1,old;return text.replace(old,new,1)

@lru_cache(maxsize=1)
def bindings(raw):
    c=deepcopy(Previous.bindings(raw));b=Current.bindings(raw)['bundle']
    for n in('ObjectOffset','InjuryTimer'):c['ram'][n]=W.address(b,n)
    pc,at=W.address(b,'ForceInjury'),W.location(b,'ForceInjury');bank=(at-16)//8192
    c['hooks']['ForceInjury']=dict(pc=pc,offset=at-16,work=False,bytes=list(raw[at:at+8]),bank_SHA256=H(raw[16+bank*8192:16+(bank+1)*8192]));return c

@lru_cache(maxsize=1)
def controller(raw,key='star'):
    assert key=='star' and H(Path(Previous.__file__).read_bytes())==BASE_SHA
    _,body=Previous.controller(raw).split('\n',1)
    body=once(body,"assert(r('PlayerStatus')==1 and work(0xc244)==1,'Retain genuinely earned M tier before hidden1UP')","assert((r('PlayerStatus')==1 and work(0xc244)==1)or(route.injury and r('PlayerStatus')==0 and work(0xc244)<=1),'Genuinely earned M or actual original injury/recovery')")
    body=once(body,"s.y<=160 and s.held&128==0","s.y<=(r('PlayerStatus')==1 and 160 or 144)and s.held&128==0")
    body=once(body,"r('StarInvincibleTimer')>0 and r('PlayerStatus')==1 and work(0xc244)==1","r('StarInvincibleTimer')>0 and route.injury and route.injury.returned and r('PlayerStatus')==0 and work(0xc244)==0")
    body=once(body,"Natural Mini M then original-admitted supportedStar/wholeC1/nativeC0/35/music64/1000/25 original+public returns","Natural Mini M then actualinjury/recovery/supportedStar/wholeC1/nativeC0/35/music64/1000/25 original+public returns")
    observer="""hook('ForceInjury',function()
 if not M.scope_passed or r('PlayerStatus')~=1 or route.injury then return end
 local z=emu.getState();local i=r('ObjectOffset')
 route.injury={PC=z['cpu.pc'],SP=z['cpu.sp'],state=state(),actor=actor(i),ObjectOffset=i,player_box=box('BoundingBox_UL_Corner'),enemy_box=box('EnemyBoundingBoxCoord',i)}
 returning(function(t)route.injury.returned={PC=t.pc,SP=t.sp,state=state(),timer=r('InjuryTimer')}end)
end)
"""
    body=once(body,"hook('GameLoop',function()",observer+"hook('GameLoop',function()")
    text='local C='+Text.lua(bindings(raw))+'\n'+body;LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'));return text

def metadata(raw,key='star'):
    q=Previous.metadata(raw,key);q.update(factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw,key).encode()),parent_powered_Star_factory_SHA256=BASE_SHA,scope='Same M/ordinary travel; actual original injury and recovery, form-aware existing support rise/freshA, real naturalStar/C0/wholeC1/35/music64/1000/25 returns; unpoweredStar, no poweredStar claim');return q

def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
