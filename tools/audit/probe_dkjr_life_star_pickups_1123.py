"""Controller-only natural pickups on private f0ed; no emulator/file outputs."""
import argparse
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
from unittest.mock import patch

import compose_dkjr_life_star_helpers_1123 as C

H,Check,Head,N,W=C.H,C.Check,C.Head,C.N,C.W
OUT=C.Joined.Native.R/'build/dkjr-life-star-pickups-1123'
COMPOSER_SHA='1eb19a037e06d7012ccfeba73e78da4a2fc38e5d1804461aaafd7efb7af9bb75'
ROM_SHA=C.WITH_GOKU

POLICY=r'''
local function lpSet(p)
 LP.phase=p;LP.since=updates;remember('stock-'..p,currentTop(LPC.helper))
 events[#events].source_y=ram(2,0x210);events[#events].actors=approachActors()
end
local function lpItem()
 for i=0,5 do if read(0x10+i)~=0 and read(0x17+i)==46 and read(0x34+i)==LPC.kind then
  return {slot=i,x=pos(0x76,0x5d,i),y=read(0xbe+i),state=read(0x1f+i),
   owner=read(LPC.owner+i),stamp=read(LPC.stamp+i),Main=updates}
 end end
end
local function lpScore()
 local value=0;for i=0,5 do local d=read(LPC.score+i);assert(d<10);value=value*10+d end;return value
end
local function lpSnap()
 return {Main=updates,x=x(),y=read(0xbd),source=ram(2,0x6b),prior=ram(2,0x6c),
  native=read(0x1e),source_y=ram(2,0x210),lives=read(0x75f),score=lpScore(),
  top=currentTop(LPC.helper),origin=ram(2,0x76),hurt=ram(2,0x68)}
end
local function lpScan()
 local a=lpItem()
 if a then
  if not LP.birth then
   assert(LP.head and a.x==LPC.target and a.state>0,'Actual actor follows the authored block hit');LP.birth=a
  end
  assert(a.slot==LP.birth.slot,'Same natural item slot')
  if a.owner==40 and a.stamp==252 then LP.prepared=LP.prepared or a end
  if a.state&128~=0 then LP.mature=LP.mature or a end
 end
 return a
end
local function lpPolicy()
 if x()<LPC.helper-16 and not LP.started then return nil end
 if not LP.started then LP.started=updates;lpSet('align')end
 assert(updates-LP.started<1600,'Finite natural life or Star pickup')
 local p,y=x(),read(0xbd);local top=currentTop(LPC.helper);local a=lpScan()
 local prior_top=LP.previous_top;LP.previous_top=top
 assert(top,'Actual existing candidate pickup lift remains live')
 local ride=ram(2,0x6b)==1 and ram(2,0x6c)==1 and y+32==top and ram(2,0x210)==y+15
 local ground=ram(2,0x6b)==1 and(read(0x1e)==0 or ride)
 local released=ram(2,0x14)&128==0
 if LP.collected and LP.phase~='exit'and LP.phase~='exit-jump'and LP.phase~='follow'then lpSet('exit')end
 if LP.phase=='align'then
  if p<LPC.head_x then return 1 elseif p>LPC.head_x+1 then return 2 end
  local direction_ok=prior_top and(LPC.kind==3 and top>prior_top or LPC.kind==2 and top<prior_top)
  if ride and ground and released and direction_ok and top>=LPC.head_low and top<=LPC.head_high then
   LP.hold=updates+8;LP.rearm=updates+50;lpSet('head');return 128
  elseif ground and not ride and released and updates>=(LP.rearm or 0)and top>=192 and top<=208 then
   LP.hold=updates+8;LP.rearm=updates+50
  end
  return updates<(LP.hold or 0)and 128 or 0
 end
 if LP.phase=='head'then
  if a then lpSet('settle');return 0 end
  assert(updates-LP.since<100,'One actual underside launch produces the item')
  return updates<(LP.hold or 0)and 128 or 0
 end
 if LP.phase=='settle'then
  assert(a,'Natural item remains after the genuine head response')
  if ground and released then lpSet('side')end
  return 0
 end
 if LP.phase=='side'then
  assert(a,'Natural actor remains during clear-side movement')
  if p<LPC.side then return 1 elseif p>LPC.side+1 then return 2 end
  if LPC.kind==3 then
   if ground and ride and released and top>=196 and top<=200 then
    LP.hold=updates+8;LP.takeoff=updates;lpSet('collect-exit');return 129
   end
   if ground and y==176 and not ride then lpSet('intercept-floor');return p<LPC.helper+48 and 1 or 0 end
   return 0
  end
  if ground and ride and released and top<=LPC.mount_top and a.x-p>=-20 and a.x-p<=36 then
   LP.hold=updates+8;LP.takeoff=updates;lpSet('seek-jump');return 128
  end
  assert(updates-LP.since<500,'Finite clear-side live-item intercept')
  return 0
 end
 if LP.phase=='seek-jump'then
  assert(a or LP.collected,'Real actor persists until actual collision')
  if updates-LP.takeoff>=8 and ground then lpSet('side');return 0 end
  assert(updates-LP.takeoff<130,'Finite original pickup intercept jump')
  return updates<(LP.hold or 0)and 128 or 0
 end
 if LP.phase=='collect-exit'then
  assert(a or LP.collected,'Actual Life remains during low floor intercept')
  if updates-LP.takeoff>=8 and ground and y==176 then lpSet('intercept-floor');return 0 end
  assert(updates-LP.takeoff<130,'Finite low live-Life intercept jump')
  return 1|(updates<(LP.hold or 0)and 128 or 0)
 end
 if LP.phase=='intercept-floor'then
  assert(a or LP.collected,'Actual Life reaches the authored floor intercept')
  assert(p<1090,'Intercept remains before the ordinary first pit')
  return p<LPC.helper+48 and 1 or 0
 end
 if LP.phase=='exit'then
  if ground and y==176 and not ride then lpSet('follow');return 1 end
  if ground and ride and released and top>=196 and top<=200 then
   LP.hold=updates+8;LP.takeoff=updates;lpSet('exit-jump');return 129
  end
  return 0
 end
 if LP.phase=='exit-jump'then
  if updates-LP.takeoff>=8 and ground and y==176 then lpSet('follow');return 1 end
  assert(updates-LP.takeoff<130,'Safe low original jump onto authored floor')
  return 1|(updates<(LP.hold or 0)and 128 or 0)
 end
 if LP.phase=='follow'then return p<LPC.helper+48 and 1 or 0 end
 error('Unknown stock pickup phase')
end
'''

OBSERVER=r'''
local lpWork,lpPickup
local lpFollows={}
local function lpMapped(pc,kind,at)
 local m=emu.convertAddress(pc);return m and m.memType==kind and m.address==at
end
local function lpPrivate(pc)return lpMapped(pc,emu.memType.nesWorkRam,3*8192+(pc&8191))end
local function lpHook(key)local h=LPC.hooks[key];return lpMapped(h.pc,emu.memType.nesPrgRom,h.offset)end
local function lpReady()return active()and ram(2,0x8fe)==2 and read(0x764)==0 and read(0x761)==0 end
local function lpToken()
 local c=emu.getState();local sp=c['cpu.sp'];local pc=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535
 local m=emu.convertAddress(pc);return {pc=pc,sp=(sp+2)&255,kind=m and m.memType,address=m and m.address}
end
local function lpMatches(t,c)
 if not t or t.pc~=c['cpu.pc']or t.sp~=c['cpu.sp']then return false end
 if t.kind then assert(lpMapped(t.pc,t.kind,t.address),'Actual mapped source/native return')end;return true
end
local function lpFinish()
 assert(LP.head and LP.birth and LP.prepared and LP.collected and LP.credit and LP.post_credit>=25 and LP.grounded>=25,
  'Natural authored head,real actor,handler,credit and25 grounded source movements')
 done=true;bits=0;LP.terminal=lpSnap();LP.passed=true
 print('SMB_NATIVE_RECEIPT '..json({passed=true,reason='Natural DK Jr life or Star with25 grounded returns',
  ROM_SHA256=LPC.sha,stock=LP,controller_only=true,outputs=0}));emu.stop(0)
end
local function lpFollow(pc)
 if lpFollows[pc]then return end;lpFollows[pc]=true
 emu.addMemoryCallback(guarded('stock actual return',function()
  local c=emu.getState()
  if lpMatches(lpPickup,c)then
   local q=lpPickup;lpPickup=nil
   assert(read(0x10+q.slot)==0,'Actual collected native actor erased')
   q.after=lpSnap();q.control=read(LPC.floatey+q.slot);q.star=read(LPC.star);q.music=read(LPC.music)
   assert(q.control==(LPC.kind==3 and 11 or 6),'Actual native reward popup')
   if LPC.kind==2 then assert(q.star==35 and q.music==64,'Actual Star protection and music')end
   LP.collected=q;LP.allow_life=LPC.kind==3
  end
  if lpMatches(lpWork,c)then
   local q=lpWork;lpWork=nil;assert(q.move and q.clock,'Actual original Move and Clock both returned')
   LP.returns=LP.returns+1;assert(lpLives(read(0x75f))and ram(2,0x6b)~=5 and ram(2,0x68)==0,'Healthy actual original continuation')
   lpScan()
   if LP.collected then
    LP.post=LP.post+1
    if not LP.credit and(LPC.kind==3 and read(0x75f)==3 or LPC.kind==2 and lpScore()>=LP.collected.score+1000)then LP.credit=lpSnap()end
    if LP.credit then LP.post_credit=LP.post_credit+1 end
    local g=LP.credit and x()>=LPC.helper+48 and read(0xbd)==176 and read(0x1e)==0
     and ram(2,0x6b)==1 and ram(2,0x6c)==1 and ram(2,0x210)==191
    LP.grounded=g and LP.grounded+1 or 0
    if LP.grounded>=25 then lpFinish()end
   end
  end
 end),emu.callbackType.exec,pc)
end
emu.addMemoryCallback(guarded('stock source entry',function()
 if not lpReady()or not lpPrivate(0xb8f0)then return end
 assert(not lpWork);lpWork=lpToken();lpFollow(lpWork.pc)
end),emu.callbackType.exec,0xb8f0)
emu.addMemoryCallback(function()if lpWork and lpPrivate(0xa2e8)then lpWork.move=true end end,emu.callbackType.exec,0xa2e8)
emu.addMemoryCallback(function()if lpWork and lpPrivate(0xaf2d)then lpWork.clock=true end end,emu.callbackType.exec,0xaf2d)
emu.addMemoryCallback(guarded('stock authored head',function()
 if not lpReady()or not lpHook('head')then return end
 local c=emu.getState();local left=ram(2,0x42)+camera()
 if left~=LPC.target or c['cpu.a']~=LPC.tile then return end
 assert(not LP.head and ram(2,0x43)==LPC.row and ram(2,0x45)==LPC.row+15 and ram(2,0x6b)==4,
  'Exact original underside and authored native head effect')
 LP.head=lpSnap();LP.head.tile=c['cpu.a'];LP.head.cell={left,LPC.row,left+15,LPC.row+15}
end),emu.callbackType.exec,LPC.hooks.head.pc)
emu.addMemoryCallback(guarded('stock real pickup',function()
 if not lpReady()or not lpHook('pickup')then return end
 local c=emu.getState();local i=c['cpu.x'];if i>5 or read(0x17+i)~=46 or read(0x34+i)~=LPC.kind then return end
 local a=lpScan();assert(LP.head and LP.birth and LP.prepared and a and a.slot==i and a.owner==40 and a.stamp==252,
  'Real naturally born DK-owned stock actor')
 assert(not LP.collected and not lpPickup);lpPickup=lpToken();lpPickup.slot=i;lpPickup.actor=a
 lpPickup.before=lpSnap();lpPickup.score=lpScore();lpFollow(lpPickup.pc)
end),emu.callbackType.exec,LPC.hooks.pickup.pc)
'''


def prepare(installed):
    assert H(Path(C.__file__).read_bytes())==COMPOSER_SHA
    baseline,current,goku=C.current_parent(installed,OUT,with_goku=True)
    parent,binding=C.Probe.authenticate(baseline)
    private,_=C.proposal(baseline);raw,_=C.compose_current(current,private,goku)
    assert H(raw)==ROM_SHA
    base=C.controller(baseline,parent,raw)
    assert H(base.encode())=='69735144b80a39048bbfd380f4ab660870511dac3d73392a1d0aa215b07907a2'
    return raw,base


def controller(raw,base,kind,*,mount_top=150,life_timing='source-passed',star_top=178,star_reboard=False,
               star_helper=1632):
    assert H(raw)==ROM_SHA and kind in(2,3)
    bundle=dict(W.Symbols.bundle(),raw=raw)
    helper,target,row,tile,side,low,high=(1008,1024,128,96,1039,162,174)if kind==3 else(star_helper,1616,144,87,1631,star_top,star_top)
    assert star_helper in (1616,1632)
    assert 160<=star_top<=192
    assert life_timing in('source-passed','early161','early160','ascending162','ascending164')
    if kind==3 and life_timing!='source-passed':low=high=int(life_timing[-3:])
    head_x=target+12
    assert head_x+1<=target+15 and head_x+17>=target and side+1>target+15
    cfg=dict(sha=ROM_SHA,kind=kind,helper=helper,target=target,row=row,tile=tile,side=side,head_x=head_x,
        head_low=low,head_high=high,mount_top=mount_top,
        owner=W.address(bundle,'InvPickupOwner'),stamp=W.address(bundle,'InvPickup'),
        score=W.address(bundle,'Player1ScoreDisplay'),floatey=W.address(bundle,'FloateyNum_Control'),
        star=W.address(bundle,'StarInvincibleTimer'),music=W.address(bundle,'AreaMusicQueue'),hooks={})
    for key,name in(('head','NativeRarePlayerHeadCollisionCore'),('pickup','HandlePowerUpCollision')):
        cfg['hooks'][key]=dict(pc=W.address(bundle,name),offset=W.location(bundle,name)-16)
    text='local LP={returns=0,post=0,post_credit=0,grounded=0}\nlocal function lpLives(v)return v==2 or(LP.allow_life and v==3)end\nlocal LPC='+C.Joined.Native.lua(cfg)+'\n'+base
    count=text.count('read(0x75f)==2');assert count>=1
    text=text.replace('read(0x75f)==2','lpLives(read(0x75f))')
    text=Check.Replay.one(text,'local function drive()\n',POLICY+'\n'+OBSERVER+'\nlocal function drive()\n')
    text=Check.Replay.one(text,' lastUpdate=updates\n',' lastUpdate=updates\n local stockBits=lpPolicy();if stockBits~=nil then bits=stockBits;return end\n')
    if kind==2 and star_reboard:
        text=Check.Replay.one(text,"if a then lpSet('settle');return 0 end",
            "if a then lpSet('settle');return p<LPC.helper and 1 or 0 end")
        text=Check.Replay.one(text,"if ground and released then lpSet('side')end\n  return 0",
            "if ground and released then lpSet('side')end\n  return p<LPC.helper and 1 or 0")
    if kind==3 and life_timing.startswith('ascending'):
        text=Check.Replay.one(text,"LPC.kind==3 and top>prior_top", "LPC.kind==3 and top<prior_top")
    if kind==3 and life_timing.startswith('ascending') or kind==2 and star_helper==1616:
        text=Check.Replay.one(text,"if ground and released then lpSet('side')end",
            "if ground and released then lpSet('wait-early')end")
        text=Check.Replay.one(text," if LP.phase=='side'then",''' if LP.phase=='wait-early'then
  assert(a,'Real Life remains above the same lift')
  assert(updates-LP.since<180,'Finite live early-Life contact on the rising lift')
  return 0
 end
 if LP.phase=='side'then''')
        if kind==2:
            text=text.replace('Real Life remains above the same lift','Real Star remains above the same lift')
            text=text.replace('early-Life contact','early Star contact')
    if kind==3 and life_timing!='source-passed' or kind==2 and star_top!=178:
        text=Check.Replay.one(text,"LP.phase=p;LP.since=updates;remember('stock-'..p,currentTop(LPC.helper))",'''LP.phase=p;LP.since=updates;remember('stock-'..p,currentTop(LPC.helper))
 if p=='head'then LP.request={Main=updates,completed_source_returns=LP.returns,top=currentTop(LPC.helper),
  source_y=ram(2,0x210),origin=ram(2,0x76),held=ram(2,0x14),sample=ram(2,0x15),frame=frame}end''')
        text=Check.Replay.one(text,'LP.head=lpSnap();LP.head.tile=',
            'LP.head=lpSnap();LP.head.completed_source_returns=LP.returns;LP.head.tile=')
        text+='''
emu.addMemoryCallback(guarded('stock actual jump acknowledgement',function()
 if LP.phase=='head'and not LP.launch and lpPrivate(0xa2e8)and ram(2,0x6b)==3 and ram(2,0x7e)==0 then
  LP.launch=lpSnap();LP.launch.completed_source_returns=LP.returns
  LP.launch.held=ram(2,0x14);LP.launch.sample=ram(2,0x15);LP.launch.frame=frame
 end
end),emu.callbackType.exec,0xa2e8)
local lpOriginalFinish=finish
finish=function(ok,why)
 if ok then return lpOriginalFinish(ok,why)end
 local ready,s=pcall(lpSnap);LP.failure=why;LP.terminal=ready and s or {Main=updates,frame=frame}
 done=true;bits=0
 print('SMB_NATIVE_RECEIPT '..json({passed=false,reason=why,ROM_SHA256=LPC.sha,stock=LP,controller_only=true,outputs=0}))
 emu.stop(1)
end
'''
    assert not any(s in text for s in('emu.write','emu.setState','io.open','takeScreenshot','loadState','saveState'))
    Check.LuaRuntime().compile(text)
    if kind==3 and life_timing=='source-passed'and mount_top==150:
        assert H(text.encode())=='6b8718724db9ffd1e8d3450a5cf6a10ada468421e3a85801018becccb251cb22'
    return text,cfg


def run(raw,text,cfg,limit,*,head_input_lag=0):
    m,opening=Head.cold(raw);steps=0;recent=[];positions=[];minimum=256;last_source=None
    delayed=0;delay_remaining=None;input_witness=[]
    def frame(memory,observe=None):
        nonlocal delayed,delay_remaining
        s=Head.state(memory);requested=memory.controller_pad
        lift=next((a for a in Head.actors(memory)if a['id']==37 and a['x']==cfg['helper']),None)
        if (head_input_lag and delay_remaining is None and requested==128 and s['x']==cfg['head_x']
                and lift and lift['y']<180):delay_remaining=head_input_lag
        if delay_remaining and delay_remaining>0:
            memory.controller_pad=0;delay_remaining-=1;delayed+=1
            input_witness.append(dict(step=steps,requested=requested,actual=0,hero=s,top=lift and lift['y']))
        return Check.normal_frame(memory,observe)
    def after(memory):
        nonlocal steps,minimum,last_source
        steps+=1;s=Head.state(m)
        if s['x']>=cfg['helper']-20:
            a=[dict(Head.actor(m,i),kind=N.get(m,'PowerUpType',i),owner=N.get(m,'InvPickupOwner',i),stamp=N.get(m,'InvPickup',i))for i in range(6)if N.get(m,'Enemy_Flag',i)]
            top=next((a['y']for a in a if a['id']==37 and a['x']==cfg['helper']),None)
            if top is not None:minimum=min(minimum,top)
            row=dict(step=steps,hero=s,pad=m.controller_pad,top=top,source_y=m.ram[2][0x210],
                source_box=list(m.ram[2][0x42:0x46]),fall_limit=m.ram[2][0x7b],actors=a)
            recent.append(row)
            if len(recent)>12:recent.pop(0)
            if s['source']!=last_source and len(positions)<30:positions.append(row)
            last_source=s['source']
    try:
        with patch.object(Check.Route.Frames,'frame',frame),redirect_stdout(io.StringIO()):
            result=Check.Route.route(m,raw,limit,controller_text=text,after_frame=after)
    except Exception as error:result={'passed':False,'receipt':{'reason':type(error).__name__+': '+str(error)}}
    full_receipt=result.get('receipt')or{}
    receipt={k:full_receipt[k]for k in('passed','reason','terminal','stock')if k in full_receipt}
    receipt['policy_events']=[v for v in full_receipt.get('events',[])if v.get('event','').startswith('stock-')]
    receipt['helper_carry']=full_receipt.get('carries',{}).get(str(cfg['helper']))
    return dict(passed=bool(result.get('passed')),ROM_SHA256=H(raw),controller_SHA256=H(text.encode()),
        kind=cfg['kind'],opening_Main=opening,steps=steps,receipt=receipt,minimum_lift_top=minimum,
        state_transitions=positions,recent=recent,final=Head.state(m),outputs=0,gameplay_seeds=False,
        head_input_delay_fixture=dict(requested=head_input_lag,actual=delayed,witness=input_witness,
            scope='Only controller input is delayed; no gameplay memory changes. Model of observed native cached input, not a physical cadence claim.'))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--kind',choices=('life','star'),default='life')
    ap.add_argument('--mount-top',type=int,default=150);ap.add_argument('--limit',type=int,default=5200)
    ap.add_argument('--life-timing',choices=('source-passed','early161','early160','ascending162','ascending164'),default='source-passed')
    ap.add_argument('--star-top',type=int,default=178)
    ap.add_argument('--star-reboard',action='store_true')
    ap.add_argument('--head-input-lag',type=int,choices=range(5),default=0)
    ap.add_argument('--compile-only',action='store_true');args=ap.parse_args()
    assert 140<=args.mount_top<=170 and 1<=args.limit<=7000
    try:
        with C.Joined.cache(),patch.object(C.Probe,'OUT',OUT):
            raw,base=prepare(C.Joined.Native.ROM.read_bytes())
            text,cfg=controller(raw,base,3 if args.kind=='life'else 2,mount_top=args.mount_top,
                life_timing=args.life_timing,star_top=args.star_top,star_reboard=args.star_reboard)
            print('DK STOCK BINDING '+json.dumps(dict(ROM_SHA256=H(raw),controller_SHA256=H(text.encode()),source_SHA256=H(Path(__file__).read_bytes()),cfg=cfg),separators=(',',':')),flush=True)
            if args.compile_only:return
            q=run(raw,text,cfg,args.limit,head_input_lag=args.head_input_lag)
            print('DK STOCK SOURCE '+json.dumps(q,separators=(',',':')),flush=True)
            print('RECEIPT '+H(json.dumps(q,sort_keys=True,separators=(',',':')).encode()),flush=True)
    finally:
        if OUT.exists():assert not any(OUT.iterdir());OUT.rmdir()


if __name__=='__main__':main()
