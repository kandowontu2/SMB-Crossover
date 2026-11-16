"""Strict current Celeste natural Flower and original safe earned dash."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile
import json,re
import replay_celeste_stock_00bb_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
GRANT=R/'docs/qa/allocations/celeste-flower-source-root-1116.json'
GRANT_SHA='52a351d5d8900a47db049ddcb30806ae4b96b643a2140757af3d44c36120b06e'
BASE_SHA='1b77f95a6eb079c667098fc4b3332e9fbe52d233b58b3d50ebc59f0bd46960c2'
TEMPLATE_SHA='9b96123005a74795ac264e95746ca94a1a3e9448f6bfd7cae4c08893d9d2817e'


def once(text,old,new):assert text.count(old)==1,old;return text.replace(old,new,1)


@lru_cache(maxsize=1)
def controls():
    assert digest(GRANT.read_bytes())==GRANT_SHA;g=json.loads(GRANT.read_bytes());assert g['ROM_SHA256']==PIN and g['source_in_memory_gameplay_authorized']and not g['game_bytes_physical_ROM_native_Downloads_authorized']
    packet=Current.Inventory.PACKET;assert digest(packet.read_bytes())==Current.Inventory.PACKET_SHA
    rows=[];proof=[]
    with ZipFile(packet)as z:
        for name,var,parent in(('celeste_upgrades_11_v8.lua','flowerBase','sunnyM'),('celeste_small_upgrades_11_v2.lua','flowerPolicy','flowerBase')):
            path='tools/playthroughs/'+name;raw=z.read(path);assert raw==(R/path).read_bytes()and digest(raw)==g['immutable_control_SHA256'][name]
            text=raw.decode();text,n=re.subn(r"local root=assert\(ROSTER_CONFIG\.out:match\('[^\n]*\n",'',text);assert n==1
            text,n=re.subn(r"local (travel|route)=assert\(dofile\([^\n]*\n",lambda m:'local '+m[1]+'='+parent+'\n',text);assert n==1
            rows.append('local '+var+'=(function()\n'+text+'\nend)()');proof.append(dict(path=path,SHA256=digest(raw)))
    return '\n'.join(rows),proof


@lru_cache(maxsize=1)
def bindings(raw):
    controls();assert digest(Path(Previous.__file__).read_bytes())==BASE_SHA and digest(Previous.TEMPLATE.read_bytes())==TEMPLATE_SHA
    c=deepcopy(Previous.bindings(raw,'oneup'));c.update(kind='flower',stock_type=1,target_x=1248,target_y=144);b=Current.bundle(raw)
    for name in('CmFresh','CmDashReady','CmDashTimer','CmDashDir','CmCooldown','CmBoost','CmBBuffer','CmPreviousAB','CmState','Square1SoundQueue'):
        c['ram'][name]=W.address(b,name)
    for name in('CmWeapons','CmDash'):
        pc,at=W.address(b,name),W.location(b,name);bank=(at-16)//8192
        c['hooks'][name]=dict(pc=pc,bank=bank,offset=at-16,bytes=list(raw[at:at+8]),bank_SHA256=digest(raw[16+bank*8192:16+(bank+1)*8192]))
    return c


@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower';config=bindings(raw);_,body=Previous.controller(raw,'oneup').split('\n',1)
    body=once(body,"local M,stock,readback={},{phase='travel'},{ }","local M,stock,readback={},{phase='travel'},{ }\nlocal dash={calls={},motion={},entries=0,returns=0,weapons_entries=0,weapons_returns=0};local dashEndpoint,pendingWeapons,pendingDash")
    body=once(body,'M=M,stock=stock,readback=readback','M=M,stock=stock,dash=dash,readback=readback')
    body=once(body,'pendingMain=pendingMain~=nil,pendingMove=', 'pendingWeapons=pendingWeapons~=nil,pendingDash=pendingDash~=nil,pendingMain=pendingMain~=nil,pendingMove=')
    body=once(body,"pose=r('CmPose')}","pose=r('CmPose'),sourceState=r('CmState'),previousAB=r('CmPreviousAB'),fresh=r('CmFresh'),dashTimer=r('CmDashTimer'),dashReady=r('CmDashReady'),dashDir=r('CmDashDir'),cooldown=r('CmCooldown'),boost=r('CmBoost')}")
    body=once(body,'local function travel(c)',controls()[0]+'\nlocal function travel(c)')
    start=body.index('local function drive()');end=body.index('local function endpoint()',start)
    drive="""local function drive()
 if not menuDone then return end
 if not active()or pendingCollect then buttons={};return end
 identity()
 if opening<16 then if moves>openingLastMoves then opening=opening+1;openingLastMoves=moves end;buttons={};return end
 routeCalls=routeCalls+1;observe(M,0,336);if M.scope_passed then observe(stock,1,1248)end
 if(not M.scope_passed and M.collected)or(stock.collected and not stock.flower_scope_passed)then buttons={};return end
 local c=context();buttons=flowerPolicy(c)
 if stock.flower_scope_passed and buttons.b and r('CmPreviousAB')&64==0 and not dash.request then
  assert(c.grounded and c.y>=176 and r('TimerControl')==0 and r('CmDashStock')==1 and r('CmTier')==2,'Original safe freshB dash admission')
  local cells={};for dx=0,112,16 do local f,h=c.block(c.x+dx,208),c.block(c.x+dx,176);assert(f~=0 and f~=35 and h==0,'Clear native floor/head for112px');cells[#cells+1]={x=c.x+dx,floor=f,head=h}end
  local enemy=c.enemy();assert(not enemy or math.abs(enemy.dx)>=96,'Clear native enemy interval96')
  dash.request={state=state(),cells=cells,buttons=buttons}
 end
 if stock.flower_scope_passed then assert(moves-dash.since<1200,'One bounded safe earned dash')end
end
"""
    body=body[:start]+drive+body[end:]
    body=once(body,'local function endpoint()\n','local function endpoint()\n if stock.flower_scope_passed then dashEndpoint();return end\n')
    body=once(body,"assert(q.leaf_return.C==0 and q.fallback_calls==1 and r('CmTier')==q.collector.state.tier,'Exact native fallback and retained real tier')","assert(q.leaf_return.C==1 and q.fallback_calls==0 and r('CmTier')==2 and r('PlayerStatus')==2,'Actual Flower C1 original tier2, no native fallback')")
    body=once(body,"if C.stock_type==3 then assert(q.life_credit and r('NumberofLives')==3 and r('CmLife')==3)else assert(q.native_effect and q.star35_writer and r('StarInvincibleTimer')>0)end","assert(r('PlayerSize')==1 and q.collector.state.tier==1,'Real M then Flower, always small')")
    body=once(body,"finish(true,'Natural Celeste M then '..C.kind..'/native credit/25 returned movement+postBG+clock at actual Main')","stock.flower_scope_passed=true;stock.flower_earned=state();dash.since=moves;buttons={}")
    body=once(body,"if kind==0 then assert(q.leaf_return.C==1 and q.fallback_calls==0 and r('CmTier')==1)elseif kind==2 then assert(r('StarInvincibleTimer')==35 and r('AreaMusicQueue')==64)end","if kind<2 then assert(q.leaf_return.C==1 and q.fallback_calls==0 and r('CmTier')==(kind==0 and 1 or 2)and r('PlayerSize')==1,'Immediate original Celeste tier pickup')end")
    helper="""dashEndpoint=function()
 if pendingMain or pendingMove or pendingBG or pendingCollect or pendingLeaf or pendingScore or pendingWeapons or pendingDash then return end
 if not dash.started or not dash.moved or dash.distance<16 then return end
 identity();assert(r('CmTier')==2 and r('PlayerSize')==1 and r('NumberofLives')==2)
 assert(stock.resumed_move==25 and stock.resumed_BG==25 and stock.resumed_clock==25 and mainEntries==mainReturns and moveEntries==moves and bgEntries==bgs and moves==clocks and dash.entries==dash.returns and dash.weapons_entries==dash.weapons_returns)
 dash.actual_Main_return={PC=emu.getState()['cpu.pc'],SP=emu.getState()['cpu.sp'],state=state()}
 finish(true,'Genuine small Celeste M/Flower/1000/25 then original earned freshB dash consumes stock and moves16px')
end
hook('CmWeapons',function()
 if not stock.flower_scope_passed then return end;assert(not pendingWeapons);dash.weapons_entries=dash.weapons_entries+1;local before=state()
 pendingWeapons=returning(function(t)
  dash.weapons_returns=dash.weapons_returns+1
  local after=state()
  if before.dash==1 and after.dash==0 then
   assert(dash.request and not dash.started and before.fresh&64~=0,'One real freshB consumes earned dash stock')
   assert(after.sourceState==6 and after.dashTimer==12 and after.dashReady==4 and after.size==1 and after.tier==2)
   dash.started={PC=t.pc,SP=t.sp,before=before,after=after}
  end
  pendingWeapons=nil
 end)
end)
hook('CmDash',function()
 if not stock.flower_scope_passed then return end;assert(dash.started and not pendingDash);dash.entries=dash.entries+1;local cpu=emu.getState();local before=state()
 pendingDash=returning(function(t)
  dash.returns=dash.returns+1
  local after=state();local q={PC=cpu['cpu.pc'],entrySP=cpu['cpu.sp'],returnPC=t.pc,returnSP=t.sp,before=before,after=after}
  if#dash.calls<12 then dash.calls[#dash.calls+1]=q end
  if after.x~=before.x then dash.moved=true;if#dash.motion<4 then dash.motion[#dash.motion+1]=q end end
  dash.distance=after.x-dash.started.after.x;pendingDash=nil
 end)
end)
hook('BlockBufferColli_Head',function()
 if not M.scope_passed or stock.born then return end;local cpu=emu.getState()
 if cpu['cpu.y']~=14 or r('Player_Y_Speed')<128 then return end
 local x=pos('Player_X_Position','Player_PageLoc')+8;if x<1248 or x>=1264 then return end
 stock.head_probe=stock.head_probe or{};if#stock.head_probe>=3 then return end
 local q={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],state=state(),query_x=x,query_y=r('Player_Y_Position')+18};stock.head_probe[#stock.head_probe+1]=q
 returning(function(t)q.returned={PC=t.pc,SP=t.sp,A=emu.getState()['cpu.a'],P=emu.getState()['cpu.ps']}end)
end)
"""
    body=once(body,"hook('GameLoop',function()",helper+"hook('GameLoop',function()")
    body=once(body,"mainEntries<4500,'Bounded ordinary Celeste S/L'","mainEntries<3400,'Bounded ordinary Celeste Flower/dash'")
    text='local C='+Text.lua(config)+'\n'+body;LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'));return text


def metadata(raw,key='flower'):
    return dict(ROM_SHA256=PIN,factory_SHA256=digest(Path(__file__).read_bytes()),controller_SHA256=digest(controller(raw).encode()),
        facade_SHA256=digest(Path(Current.__file__).read_bytes()),parent_factory_SHA256=BASE_SHA,parent_template_SHA256=TEMPLATE_SHA,
        grant_SHA256=GRANT_SHA,additional_immutable_controls=controls()[1],base_controls=Previous.policy()[1],
        scope='Actual00bb real small M then mature Flower C1/1000/tier2/25 returned owners, then original CmWeapons stock consumption/State6/Timer12 and reached CmDash real16px motion',
        outputs=0,Mesen=False,gameplay_seeds=0,game_bytes_changed=0)


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
