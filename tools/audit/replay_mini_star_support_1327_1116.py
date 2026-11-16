"""Genuine current Mini Star from ordinary existing raised support."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_mini_oneup_support_contact_1327_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,H,Current=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.H,Previous.Current
BASE_SHA='118ed54d324f13f35e84a8c43cc5ae76a2de2d12bb2c7623a954047ee15f5579'

def once(text,old,new):assert text.count(old)==1,old;return text.replace(old,new,1)

@lru_cache(maxsize=1)
def bindings(raw):
    c=deepcopy(Previous.Previous.bindings(raw));c.update(kind='star',stock_type=2,target_x=1616,target_y=144);b=Current.bindings(raw)['bundle']
    for n in('StarInvincibleTimer','AreaMusicQueue'):c['ram'][n]=W.address(b,n)
    pc,at=W.address(b,'MarioSourcePowerupCollision'),W.location(b,'MarioSourcePowerupCollision');timer,music=c['ram']['StarInvincibleTimer'],c['ram']['AreaMusicQueue']
    pattern=bytes((0xa9,35,0x8d,timer&255,timer>>8,0xa9,64,0x8d,music&255,music>>8,0x60));hits=[i for i in range(120-len(pattern))if raw[at+i:at+i+len(pattern)]==pattern];assert len(hits)==1
    d=hits[0];assert raw[at+d-4:at+d-1]==bytes.fromhex('c903f0');bank=(at-16)//8192
    c['hooks']['ActualStarEffect']=dict(pc=pc+d,offset=at+d-16,work=False,bytes=list(raw[at+d:at+d+8]),bank_SHA256=H(raw[16+bank*8192:16+(bank+1)*8192]));return c

@lru_cache(maxsize=1)
def controller(raw,key='star'):
    assert key=='star' and H(Path(Previous.__file__).read_bytes())==BASE_SHA
    _,body=Previous.controller(raw).split('\n',1)
    body=once(body,"if item.phase=='travel'and x<960 then","if item.phase=='travel'and x<C.target_x-72 then")
    body=once(body,"r('FloateyNum_Control',5)==(M.scope_passed and 11 or 6)","r('FloateyNum_Control',5)==6")
    body=once(body," and item.life_credit)"," and item.native_effect and item.star35_writer)")
    body=once(body,"r('NumberofLives')==3 and r('PlayerStatus')==1","r('NumberofLives')==2 and r('StarInvincibleTimer')>0 and r('PlayerStatus')==1")
    body=once(body,"Natural Mini M then original-admitted supportedhidden1UP/wholeC1/realINC/cue64/25 original+public returns","Natural Mini M then original-admitted supportedStar/wholeC1/nativeC0/35/music64/1000/25 original+public returns")
    body=once(body,"if qx<960 or qx>=1072 then return end","if qx<1552 or qx>=1680 then return end")
    body=once(body,"frame<14000 and mainEntries<4200,'Bounded natural Mini M/hidden1UP'","frame<20000 and mainEntries<6000,'Bounded natural Mini M/Star'")
    observer="""hook('ActualStarEffect',function()
 if not pendingCollect or not M.scope_passed then return end
 local z=emu.getState();assert(z['cpu.ps']&1==0,'Original native kind2 CMP3 effectC0')
 item.native_effect={PC=z['cpu.pc'],SP=z['cpu.sp'],P=z['cpu.ps'],state=state()}
end)
emu.addMemoryCallback(guard(function(_,v)
 if pendingCollect and M.scope_passed and v==35 then
  local z=emu.getState();assert(z['cpu.ps']&1==0,'Actual native Star timer35 writerC0')
  item.star35_writer={PC=z['cpu.pc'],SP=z['cpu.sp'],P=z['cpu.ps'],value=v,state=state()}
 end
end),emu.callbackType.write,C.ram.StarInvincibleTimer)
"""
    body=once(body,"hook('GameLoop',function()",observer+"hook('GameLoop',function()")
    body=once(body,"item.resumed_steps=steps-item.credit.steps;item.resumed_moves=moves-item.credit.moves","item.resumed_steps=steps-item.credit.steps;item.resumed_moves=moves-item.credit.moves")
    text='local C='+Text.lua(bindings(raw))+'\n'+body;LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'));return text

def metadata(raw,key='star'):
    assert key=='star';q=Previous.metadata(raw);q.update(factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw,key).encode()),parent_support_contact_SHA256=BASE_SHA,scope='Actual1327 M/guarded fixed lifts/ordinary pits, existing UpSelect at genuineStar; native legal >=6 physical admission/wholeC1, actual nativeC0/35/music64/1000 then25 returned MiniStep/public; no128 claim unless reached');return q

def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
