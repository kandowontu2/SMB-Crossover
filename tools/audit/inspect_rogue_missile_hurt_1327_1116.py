"""Passive exact hurt/gravity writer on the unchanged first missile mount."""
from collections import Counter,deque
from pathlib import Path
from unittest.mock import patch
import argparse,json
import current_rogue_missile_stock_1327_1116 as J
from check_ff_stdout_controller_source_1110 import LuaRuntime

N,W,Frames=J.N,J.W,J.Frames


def run(raw,limit=3800):
    q=J.bindings(raw);m=J.cold(raw);lua=LuaRuntime(unpack_returned_tuples=True);body=J.policy_text(raw);choose=lua.execute(body)
    counts=Counter();pending=[];events=[];tail=deque(maxlen=6);birth=None;mature=None;target=None;credit=None;done=False;fault=None;stock='tank';completed=[];phase_changes=[]
    returned=[];grants=[];popups=[];sound=Counter();source_requests=[];head=[];score_events=[];first_reset=None
    fields=q['fields'];score_at=fields['Player1ScoreDisplay'];base=N.NesMPU;ctx={'inside':False};objects=[]
    r=lambda n,i=0:N.get(m,n,i)
    def score():return int(''.join(str(m[score_at+i])for i in range(6)))
    def state():
        return dict(Main=counts['GameLoop_returned'],motor=counts['RdControlStep_returned'],
            x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),native_state=r('Player_State'),
            vx=r('Player_X_Speed'),vy=r('Player_Y_Speed'),action=r('RdAction'),source_x=r('RdX')+256*r('RdRoomHi'),
            source_y=r('RdY'),source_vy=r('RdVY'),held=r('RdHeld'),fresh=r('RdFresh'),
            health_raw=[r('RdHealthLo'),r('RdHealthHi')],tanks=r('RdTanks'),gear=r('RdGear'),
            missiles=r('RdMissiles'),max_missiles=r('RdMaxMissiles'),status=r('PlayerStatus'),lives=r('NumberofLives'),
            engine=r('GameEngineSubroutine'),score=score(),star=r('StarInvincibleTimer'),
            timer_control=r('TimerControl'),hosted_growth=r('GuestPowerupActive'))
    def actor(i):
        return dict(slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),kind=r('PowerUpType',i),state=r('Enemy_State',i),
            x=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),y=r('Enemy_Y_Position',i),yhigh=r('Enemy_Y_HighPos',i),
            private=r('InvPickup',i),owner=r('InvPickupOwner',i),saved_raw=r('InvPickupSaveLo',i),rise=r('InvRisePhase',i))
    def actors():return[a for i in range(6)if(a:=actor(i))['flag']]
    def tag(pc):return m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
    def token(c):
        pc=(m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1)&65535
        return pc,(c.sp+2)&255,tag(pc)
    watched=('GameLoop','RdControlStep','RdLifeMovement','HandlePowerUpCollision','RdHsCollectActor','RdHsGrantType','RdItPickup','RdItPrepare','AddToScore')
    points={(q['hooks'][n]['tag'],q['hooks'][n]['PC']):n for n in watched+('PlayerHeadCollision','SetupFloateyNumber','EraseEnemyObject','DecNumTimer')}
    score_timer=None
    calibration=dict(armed=None,stop=None,zero_writer=None,first_blocked_up=None,first_solid_query=None,hurt_entry=None,gravity38_writer=None)
    probe_pending=[]
    probe_points={}
    for n in('RdHostMoveUp','RdTxLoadedCell','RdStopVertical','RdControlHurtLaunch'):
        pc,at=W.address(m.bundle,n),W.location(m.bundle,n)
        probe_points[((at-16)//8192)|128,pc]=n
    def cal_state():
        s=state();s.update(camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'),source_VX=r('RdVX'),
            gravity=r('RdGravity'),facing=r('RdFacing'),hurt_clock=r('RdHurtClock'),hurt_direction=r('RdHurtDirection'),hit=r('RdHit'),requested_pad=m.controller_pad)
        return s
    def cell_grid():
        return [[x,y,r('Block_Buffer_1',(x//256)%2*208+((y-32)//16)*16+(x%256)//16)]
            for y in(128,144,160,176)for x in range(1184,1296,16)]
    def context():
        s=state();c=dict(frame=s['Main'],poll=s['Main'],char=2,variant=1,r=r,x=s['x'],y=s['y'],yHigh=r('Player_Y_HighPos'),
            state=s['native_state'],vx=s['vx'],vy=s['vy'],status=s['status'],world=r('WorldNumber'),level=r('LevelNumber'),
            area=r('AreaPointer'),areaType=r('AreaType'),engine=s['engine'],camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'),
            lastA=bool(r('RdHeld')&128),grounded=s['native_state']==0)
        c['block']=lambda x,y:0 if y<32 or y>=240 else r('Block_Buffer_1',(int(x)//256)%2*208+((int(y)-32)//16)*16+(int(x)%256)//16)
        def enemy():
            near=[]
            for a in actors():
                dx=a['x']-s['x']
                if a['flag']<128 and(a['id']<21 or a['id']in(45,51))and a['state']<32 and not(a['id']==6 and a['state']>=2)and-160<dx<160:
                    near.append(dict(slot=a['slot'],id=a['id'],x=a['x'],y=a['y'],state=a['state'],dx=dx))
            return lua.table_from(min(near,key=lambda a:abs(a['dx'])))if near else None
        c['enemy']=enemy;return lua.table_from(c)
    def after_main():
        nonlocal birth,mature,done,target,credit,stock
        s=state();aa=actors()
        assert r('SelectedCharacter')==2 and r('RdVariant')==1
        assert r('WorldNumber')==r('LevelNumber')==r('CheatInvincible')==r('CheatStartLevel')==0
        assert s['lives']==2 and s['engine']!=11 and sum(s['health_raw'])>0,('Actual Rogue death',s)
        for a in aa:
            if a['id']==46:
                assert a['private']==(216 if stock.startswith('tank')else 217)and a['owner']==2 and a['saved_raw']==(0 if stock.startswith('tank')else 1),('Natural authored tank/missile classification',a)
                if birth is None:birth=dict(actor=a,player=s)
                if a['state']&128 and mature is None:mature=dict(actor=a,player=s)
        if credit:
            delta={n:counts[n+'_returned']-credit['returned'][n]for n in('RdControlStep','RdLifeMovement','GameLoop')}
            entered={n:counts[n+'_entered']-credit['entered'][n]for n in('RdControlStep','RdLifeMovement','GameLoop')}
            if all(v>=25 for v in delta.values())and all(v>=25 for v in entered.values()):
                assert not pending and target and birth and mature and s['tanks']==1 and s['status']==1
                assert s['gear']==0
                if stock=='tank-credit':assert s['health_raw']==[153,25]and(s['missiles'],s['max_missiles'])==(0,0)
                else:assert(s['missiles'],s['max_missiles'])==(5,5)
                assert first_reset is None
                credit.update(postcredit_returned=delta,postcredit_entered=entered,
                    postcollector_returned={n:counts[n+'_returned']-target['returned'][n]for n in('RdControlStep','RdLifeMovement','GameLoop')})
                completed.append(dict(stock=stock,birth=birth,mature=mature,collector=target,credit=credit,terminal=s))
                if stock=='tank-credit':
                    stock='missile';birth=None;mature=None;target=None;credit=None
                else:done=True;m.controller_pad=0;return
        pad=choose(context(),stock,lua.table_from([lua.table_from(a)for a in aa]))
        if len(phase_changes)<20 and(not phase_changes or phase_changes[-1]['stock']!=stock):phase_changes.append(dict(stock=stock,player=s))
        m.controller_pad=sum(v for n,v in(('right',1),('left',2),('down',4),('up',8),('start',16),('select',32),('b',64),('a',128))if pad[n])
        tail.append(dict(player=s,pad=m.controller_pad,items=[a for a in aa if a['id']==46]))
        assert counts['GameLoop_returned']<3600,'Bounded genuine tank-to-missile route'
    class CPU(base):
        def __init__(self,*a,**kw):super().__init__(*a,**kw);objects.append(self)
        def settle(self):
            nonlocal target,credit,stock
            while pending and(self.pc,self.sp,tag(self.pc))==pending[-1]['return']:
                p=pending.pop();name=p['name'];counts[name+'_returned']+=1
                if name=='GameLoop':after_main()
                elif name=='RdHsCollectActor':
                    assert len(returned)<8;returned.append(dict(C=self.p&1,A=self.a,before=p['before'],after=state()))
                elif name=='RdHsGrantType':
                    assert len(grants)<8;grants.append(dict(A=p['A'],C=self.p&1,before=p['before'],after=state()))
                elif name=='HandlePowerUpCollision'and p['actor']['id']==46 and not r('Enemy_Flag',p['actor']['slot']):
                    assert target is None and birth and mature and p['actor']['state']&128
                    assert returned and returned[-1]['C']==1 and grants and grants[-1]['A']==(8 if stock=='tank'else 9)and grants[-1]['C']==1
                    s=state();assert(s['tanks'],s['status'])==(1,1)
                    if stock=='tank':assert s['health_raw']==[153,25]
                    else:assert s['health_raw']==p['before']['health_raw']and(s['missiles'],s['max_missiles'])==(5,5)
                    stock+='-credit'
                    assert 6 in popups and sound[32]and source_requests
                    target=dict(actor=p['actor'],player_before=p['before'],player_after=s,physical_boxes=p['boxes'],
                        returned={n:counts[n+'_returned']for n in('RdControlStep','RdLifeMovement','GameLoop')},
                        erase_seen=bool(counts['target_erase']),C=returned[-1]['C'])
                    assert target['erase_seen']
                elif name=='AddToScore'and p.get('timer'):
                    assert score()==p['score']+1000 and len(p['writes'])==6,('Actual timer43 thousand writer',p,score())
                    assert target is not None
                    credit=dict(writer=dict(PC=q['hooks']['AddToScore']['PC'],tag=q['hooks']['AddToScore']['tag'],
                        timer=p['timer'],before=p['score'],after=score(),six_decimal_writes=p['writes']),state=state(),
                        returned={n:counts[n+'_returned']for n in('RdControlStep','RdLifeMovement','GameLoop')},
                        entered={n:counts[n+'_entered']for n in('RdControlStep','RdLifeMovement','GameLoop')})
        def step(self):
            nonlocal score_timer
            self.settle()
            if calibration['armed']:
                while probe_pending and(self.pc,self.sp,tag(self.pc))==probe_pending[-1]['return']:
                    z=probe_pending.pop()
                    if z['name']=='RdTxLoadedCell'and self.p&1 and calibration['first_solid_query']is None:
                        calibration['first_solid_query']=dict(**z,A=self.a,C=self.p&1,after=cal_state())
                    if z['name']=='RdHostMoveUp'and not(self.p&1)and calibration['first_blocked_up']is None:
                        calibration['first_blocked_up']=dict(**z,A=self.a,C=self.p&1,after=cal_state())
                pn=probe_points.get((tag(self.pc),self.pc))
                if pn=='RdControlHurtLaunch'and calibration['hurt_entry']is None:
                    calibration['hurt_entry']=dict(PC=self.pc,tag=tag(self.pc),SP=self.sp,before=cal_state())
                if pn=='RdStopVertical'and r('RdVY')>=128 and calibration['stop']is None:
                    calibration['stop']=dict(PC=self.pc,tag=tag(self.pc),SP=self.sp,before=cal_state(),actual_grid=cell_grid())
                if pn in('RdHostMoveUp','RdTxLoadedCell')and r('RdVY')>=128:
                    if pn!='RdTxLoadedCell'or m[0x5c35]==0:
                        probe_pending.append({'name':pn,'return':token(self),'before':cal_state(),
                            'query':dict(world_x=m[0x5c31]*256+m[0x5c33],y=m[0x5c32],axis=m[0x5c35])})
            name=points.get((tag(self.pc),self.pc))
            if name:
                counts[name+'_entered']+=1
                if name=='PlayerHeadCollision':
                    if len(head)<8 and 300<=state()['x']<=380:head.append(dict(tile=self.a,player=state()))
                elif name=='SetupFloateyNumber':
                    if len(popups)<16:popups.append(self.a)
                elif name=='EraseEnemyObject':
                    if self.x<6 and actor(self.x)['id']==46:counts['target_erase']+=1
                elif name=='DecNumTimer':
                    if self.a==43 and self.y==6 and birth and self.x==birth['actor']['slot']:
                        assert r('FloateyNum_Timer',self.x)==43
                        score_timer=dict(slot=self.x,oldtimer=43,control=6,Main=counts['GameLoop_returned'])
                else:
                    p=dict(name=name,return_=token(self),A=self.a);p['return']=p.pop('return_')
                    if name in('RdHsGrantType','RdHsCollectActor','HandlePowerUpCollision'):p['before']=state()
                    if name=='HandlePowerUpCollision':
                        p['actor']=actor(self.x);at=fields['BoundingBox_UL_Corner'];ofs=(self.x+1)*4
                        p['boxes']=dict(player=list(m[at:at+4]),item=list(m[at+ofs:at+ofs+4]))
                    if name=='AddToScore':p.update(score=score(),timer=score_timer,writes=[]);score_timer=None
                    pending.append(p)
            ctx.update(inside=True,PC=self.pc,tag=tag(self.pc),opcode=m[self.pc])
            try:return super().step()
            finally:ctx['inside']=False
    old_write=type(m).__setitem__
    def write(bus,at,value):
        nonlocal first_reset
        if bus is m and ctx['inside']and isinstance(at,int):
            if at==W.address(m.bundle,'RdGravity')and calibration['armed']and value==56 and calibration['gravity38_writer']is None:
                calibration['gravity38_writer']=dict(PC=ctx['PC'],tag=ctx['tag'],opcode=ctx['opcode'],old=m[at],new=value,before=cal_state())
            if at==fields['RdVY']and stock=='missile':
                s=state()
                if calibration['armed']is None and value>=128 and m[at]<128 and 1180<=s['x']<1230 and s['y']>=170:
                    calibration['armed']=dict(PC=ctx['PC'],tag=ctx['tag'],old=m[at],new=value,before=cal_state())
                elif calibration['armed']and calibration['zero_writer']is None and m[at]>=128 and value==0:
                    calibration['zero_writer']=dict(PC=ctx['PC'],tag=ctx['tag'],opcode=ctx['opcode'],old=m[at],new=value,before=cal_state())
            if at==fields['Square2SoundQueue']and value in(32,64):sound[value]+=1
            if at==fields['RdSfx']+4 and value&64 and len(source_requests)<4:
                source_requests.append(dict(PC=ctx['PC'],tag=ctx['tag'],old=m[at],new=value,Main=counts['GameLoop_returned']))
            if score_at<=at<score_at+6:
                for p in reversed(pending):
                    if p['name']=='AddToScore':
                        if p.get('timer'):p['writes'].append(dict(offset=at-score_at,old=m[at],new=value,PC=ctx['PC'],tag=ctx['tag']))
                        break
            if target and first_reset is None and at in(fields['RdTanks'],fields['PlayerStatus'])and value==0:
                first_reset=dict(PC=ctx['PC'],tag=ctx['tag'],address=at,old=m[at],new=value,player=state())
        return old_write(bus,at,value)
    try:
        with patch.object(N,'NesMPU',CPU),patch.object(type(m),'__setitem__',write):
            for tick in range(limit):
                Frames.frame(m,whole_pass=True)
                for c in objects:c.settle()
                assert not pending,('Incomplete public frame scopes',[p['name']for p in pending])
                objects.clear()
                if done or calibration['stop']or calibration['zero_writer']:break
                if tick%300==299:print('PROGRESS '+json.dumps(dict(Main=counts['GameLoop_returned'],state=state(),birth=bool(birth),mature=bool(mature),collector=bool(target),credit=bool(credit))),flush=True)
    except Exception as error:fault=dict(error=repr(error),context=dict(ctx),state=state(),actors=actors(),pending=[p['name']for p in pending])
    result=dict(passed=done and fault is None,fault=fault,owning_SHA256=J.PIN,kind='authored raw0 D8 then powered raw1 D9 missile tank',
        policy_SHA256=J.H(body.encode()),facade_SHA256=J.H(Path(J.__file__).read_bytes()),grant_SHA256=J.GRANT_SHA,
        counts=dict(counts),birth=birth,mature=mature,collector=target,score_credit=credit,grants=grants,
        actual_private_collect_returns=returned,native_popups=popups,native_sound_writes=dict(sound),source_music_requests=source_requests,
        first_unexpected_resource_reset=first_reset,head=head,terminal=state(),tail=list(tail),
        controller_only=True,no_gameplay_or_resource_or_actor_seeds=True,no_60_growth_requirement=True,
        original_BCD_image_only=True,completed_natural_gates=completed,stock_phase=stock,phase_changes=phase_changes,calibration=calibration,outputs=0,native=False)
    result['receipt_SHA256']=J.H(json.dumps(result,sort_keys=True,separators=(',',':')).encode());return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--limit',type=int,default=3800);a=p.parse_args();assert 3601<=a.limit<=4500
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Source natural tank attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,a.limit)
    compact=dict(diagnostic_complete=bool(q['calibration']['zero_writer']and q['calibration']['gravity38_writer']),gameplay_passed=q['passed'],original_input_policy_SHA256=q['policy_SHA256'],
        owning_SHA256=q['owning_SHA256'],original_F_negative='6ab3b7a9782b9ff01d9b75718be7f089a61e1354e9d27a6d3d20df53f2e4742c',
        calibration=q['calibration'],Main=q['counts']['GameLoop_returned'],terminal=q['terminal'],fault=q['fault'],
        no_game_or_input_changes=True,outputs=0,full_internal_receipt_SHA256=q['receipt_SHA256'])
    compact['receipt_SHA256']=J.H(json.dumps(compact,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(compact,separators=(',',':')),flush=True)








