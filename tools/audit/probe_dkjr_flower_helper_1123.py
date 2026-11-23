"""Source-only ordinary M→Flower attempt on the separate15-row proposal."""
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
import io,json
import compose_dkjr_flower_helper_1123 as C
import probe_dkjr_flower_route_1123 as Original

Check,Head,H=C.Check,C.Check.Head,C.H
N,W=Check.N,Check.W

POLICY=r'''
local flower={phase='align',attempts=0,events={}}
local function flowerSet(p)
 flower.phase=p;flower.since=updates
 flower.events[#flower.events+1]={phase=p,Main=updates,x=x(),y=read(0xbd)}
 remember('flower-'..p,currentTop(1264))
 events[#events].source_y=ram(2,0x210)
 events[#events].facing=ram(2,0x6d)
end
local function flowerItem()
 for i=0,5 do if read(0x10+i)~=0 and read(0x17+i)==46 and read(0x34+i)==1 then
  return{slot=i,x=pos(0x76,0x5d,i),y=read(0xbe+i),state=read(0x1f+i)}
 end end
end
local function flowerPolicy()
 if x()<1224 then return nil end
 if not flower.started then flower.started=updates end
 assert(updates-flower.started<1500,'Finite organic Flower acquisition')
 local status=read(PLAYER_STATUS)
 if status==2 then flower.phase='awarded';return 0 end
 assert(status==1 and read(0x75f)==2 and ram(2,0x68)==0,'Earned M and health retained at Flower')
 local player,y=x(),read(0xbd);local top=currentTop(1264);local a=flowerItem()
 assert(top,'Actual Flower helper remains live')
 local ride=ram(2,0x6b)==1 and ram(2,0x6c)==1 and y+32==top and ram(2,0x210)==y+15
 -- Native state2 can coexist with a genuine committed original carry.
 -- Match the frozen full route's grounded-or-observed-carry launch rule.
 local ground=ram(2,0x6b)==1 and (read(0x1e)==0 or ride)
 local released=(ram(2,0x14)&128)==0
 if a and flower.phase~='settle'and flower.phase~='side'and flower.phase~='side-hop'and flower.phase~='side-position'and flower.phase~='left-jump'then
  assert(a.x==1248,'Actual authored Flower actor');flowerSet('settle')
 end
 if flower.phase=='align'or flower.phase=='head'then
  if player<1260 then return 1 elseif player>1261 then return 2 end
  if ride and top<=180 and ground and released and flower.phase=='align'then
   flowerSet('head');flower.hold=updates+8;flower.attempts=flower.attempts+1
  elseif not ride and ground and top>=192 and top<=208 and updates>=(flower.rearm or 0)then
   flower.hold=updates+8;flower.rearm=updates+47
  end
  return updates<(flower.hold or 0)and 128 or 0
 end
 if flower.phase=='settle'then
  assert(a,'Flower is present while original underside response settles')
  if ground and ram(2,0x6c)==1 and ram(2,0x210)==y+15 and released then
   flowerSet('side')
  end
  return 0
 end
 if flower.phase=='side'then
  assert(a,'Flower is present until real collection')
  -- A plain walk can remain leased to a descending lift below the floor.
  -- Leave with a fresh native jump before its top crosses floor Y208.
  if ride and ground and released and top>=196 and top<=200 then
   flowerSet('side-hop');flower.takeoff=updates;return 129
  end
  return 0
 end
 if flower.phase=='side-hop'then
  assert(updates-flower.takeoff<130,'Finite ordinary jump to the clear-side floor')
  if updates-flower.takeoff>=8 and ground and ram(2,0x6c)==1 then
   flowerSet('side-position');return 0
  end
  return 1|(updates-flower.takeoff<8 and 128 or 0)
 end
 if flower.phase=='side-position'then
  assert(a,'Flower is present at the clear-side staging point')
  assert(player<=1304,'Finite clear-side staging position')
  if player<1291 then return 1 elseif player>1293 then return 2 end
  if ram(2,0x6d)~=1 then return 1 end
  if a.state&128~=0 and ride and ground and released and top>=146 and top<=160 then
   flowerSet('left-jump');flower.takeoff=updates
   flower.events[#flower.events].top=top;flower.events[#flower.events].facing=ram(2,0x6d)
   return 130
  end
  return 0
 end
 if flower.phase=='left-jump'then
  if not a then return 0 end
  if ground and y==112 then return player>1256 and 2 or 0 end
  assert(updates-flower.takeoff<120,'One clear-side Flower row mount')
  return 2|(updates-flower.takeoff<8 and 128 or 0)
 end
 error('Unknown Flower phase '..flower.phase)
end
'''


def controller(raw):
    parent=C.inverse(raw)
    prior=C.Previous.controller(parent,route=True)
    lo=prior.index('local slotAdmissionWait,slotAdmissionReady');hi=prior.index('local function drive()\n',lo)
    adapter=Check.Replay.one(prior[lo:hi],"if r('PlayerStatus')==1 then","if r('PlayerStatus')>=1 then")
    text=C.full_controller(raw)
    fields=W.Symbols.bundle();policy=POLICY.replace('PLAYER_STATUS',str(W.address(fields,'PlayerStatus')))
    text=Check.Replay.one(text,'local function drive()\n',adapter+policy+'\nlocal function drive()\n')
    text=Check.Replay.one(text,' lastUpdate=updates\n',''' lastUpdate=updates
 local firstBits=mushroomPolicy();if firstBits~=nil then bits=firstBits;return end
 local flowerBits=flowerPolicy();if flowerBits~=nil then bits=flowerBits;return end
''')
    assert not any(q in text for q in ('emu.write','emu.setState','io.open','takeScreenshot','loadState','saveState'))
    Check.LuaRuntime().compile(text)
    return text


class Complete(Exception):pass


def run(raw):
    text=controller(raw);m,opening=Head.cold(raw)
    hooks={(((W.location(m.bundle,n)-16)//8192)|128,W.address(m.bundle,n)):n
        for n in ('HandlePowerUpCollision','GuestPowerupUpdate','NativeRarePlayerHeadCollisionCore')}
    watched={pc for tag,pc in hooks}|{0xb8f0,0xa2e8,0xaf2d,0xd1f0}
    pending=None;collected=None;birth=None;mature=None;frozen=None;work=None
    steps=0;ages=set();returns=0;post=0;events=[];recent=[];credit=None;end=None
    row_jump=[];row_jump_min=256;prior_motion=None
    def token(cpu):return((m[0x101+cpu.sp]+256*m[0x102+cpu.sp]+1)&65535,cpu.sp+2)
    def actor(i):return dict(Head.actor(m,i),kind=N.get(m,'PowerUpType',i),owner=N.get(m,'InvPickupOwner',i),stamp=N.get(m,'InvPickup',i))
    def observe(memory,cpu):
        nonlocal pending,collected,work,returns,post,frozen
        pc=cpu.pc
        if pc not in watched and (not work or pc!=work['token'][0])and(not pending or pc!=pending['token'][0]):return
        point=Head.point(cpu);tag,pc=point
        if point==(3,0xb8f0):
            assert work is None;work=dict(token=token(cpu),move=False,clock=False)
        if work and point==(3,0xa2e8):work['move']=True
        if work and point==(3,0xaf2d):work['clock']=True
        if work and(pc,cpu.sp)==work['token']:
            assert work['move']and work['clock'];returns+=1
            if collected:post+=1
            work=None
        name=hooks.get(point)
        if name=='NativeRarePlayerHeadCollisionCore'and Head.state(m)['x']>1200:
            events.append(dict(event='actual_head_effect',hero=Head.state(m),tile=cpu.a,
                source_y=m.ram[2][0x210],source_box=list(m.ram[2][0x42:0x46]),
                actual_box=[m[a] for a in range(0x658,0x65c)]))
        if name=='HandlePowerUpCollision'and cpu.x<6 and N.get(m,'Enemy_ID',cpu.x)==46 and N.get(m,'PowerUpType',cpu.x)==1:
            a=actor(cpu.x);assert birth and mature and birth['slot']==mature['slot']==cpu.x
            assert a['state']&128 and a['owner']==40 and a['stamp']==252
            pending=dict(token=token(cpu),actor=a,before_score=Check.score(m),hero=Head.state(m))
        if pending and(pc,cpu.sp)==pending['token']:
            assert not N.get(m,'Enemy_Flag',pending['actor']['slot'])
            collected=dict(pending,returned=Head.state(m));pending=None
        if name=='GuestPowerupUpdate'and collected and N.get(m,'GuestPowerupActive'):
            age=N.get(m,'GuestPowerupAge');assert age not in ages and 0<=age<60;ages.add(age)
            value=bytes(m.ram[2][:2048])
            if frozen is None:frozen=value
            assert frozen==value
        if point==(2,0xd1f0)and cpu.x<6:
            a=Head.actor(m,cpu.x)
            if a['id']in(37,40)and a['x']>=1200:
                events.append(dict(event='native_helper_birth',hero=Head.state(m),actor=a,ordinal=m.ram[2][0x8fd],slots=Head.actors(m)))
    def after(memory):
        nonlocal steps,birth,mature,credit,end,row_jump_min,prior_motion
        steps+=1;s=Head.state(m)
        if s['x']>=1216:
            recent.append(dict(step=steps,hero=s,actors=Head.actors(m),pad=m.controller_pad,
                source_y=m.ram[2][0x210],fall_limit=m.ram[2][0x7b],
                native_state=N.get(m,'Player_State'),box=list(m.ram[2][0x42:0x46])))
            if len(recent)>8:recent.pop(0)
        for i in range(6):
            if N.get(m,'Enemy_Flag',i)and N.get(m,'Enemy_ID',i)==46 and N.get(m,'PowerUpType',i)==1:
                a=actor(i)
                if birth is None:birth=a
                if a['state']&128 and mature is None:mature=a
        if mature and s['x']>=1248 and s['y']<144:
            row_jump_min=min(row_jump_min,s['y'])
            motion=(s['source'],s['prior'],N.get(m,'Player_State'))
            if motion!=prior_motion and len(row_jump)<16:
                row_jump.append(dict(step=steps,hero=s,native_state=motion[2],source_y=m.ram[2][0x210]))
            prior_motion=motion
        if collected and N.get(m,'GuestPowerupActive')==0 and s['status']==2:
            if credit is None:
                credit=Check.score(m);assert credit==collected['before_score']+1000
            if post>=25 and s['source']==s['prior']==1 and N.get(m,'Player_State')==0:
                assert s['lives']==2 and s['hurt']==0 and ages==set(range(60))and work is None
                end=s;raise Complete
    output=io.StringIO()
    try:
        with patch.object(Check.Route.Frames,'frame',Check.normal_frame):
            with redirect_stdout(output):result=Check.Route.route(m,raw,6500,controller_text=text,observe_extra=observe,after_frame=after)
    except Complete:result=None
    receipt=(result or {}).get('receipt') or {}
    q=dict(passed=end is not None,ROM_SHA256=H(raw),controller_SHA256=H(text.encode()),opening_Main=opening,
        steps=steps,birth=birth,mature=mature,collected=collected,credit=credit,growth_ages=sorted(ages),
        completed_source_returns=returns,post_collection_source_returns=post,events=events,recent=recent,
        row_jump=row_jump,row_jump_min_y=row_jump_min,
        final=Head.state(m),reason=receipt.get('reason'),route_terminal=receipt.get('terminal'),
        policy_events=[e for e in receipt.get('events',[]) if e.get('event','').startswith('flower-')],outputs=0)
    return q


if __name__=='__main__':
    parent=C.Old.M.ROM.read_bytes();raw,proposal=C.proposal(parent)
    print('DK FLOWER PROPOSAL '+json.dumps(proposal,separators=(',',':')),flush=True)
    q=run(raw);q['source_SHA256']=H(Path(__file__).read_bytes())
    print('DK FLOWER ATTEMPT '+json.dumps(q,separators=(',',':')),flush=True)
    print('RECEIPT '+H(json.dumps(q,sort_keys=True,separators=(',',':')).encode()),flush=True)
