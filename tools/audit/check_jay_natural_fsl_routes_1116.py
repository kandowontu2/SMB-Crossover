"""Actual current ordinary Jay F/S/L routes; shared Lua policy, zero outputs."""
from collections import Counter,deque
from pathlib import Path
from unittest.mock import patch
import argparse,json,re
import current_jay_natural_stock_7c0f_1116 as J
from check_ff_stdout_controller_source_1110 import LuaRuntime

N,W,Frames=J.N,J.W,J.Frames
POLICY=J.R/'tools/reference/jay_natural_fsl_policy_1116.lua'


def run(raw,kind,limit):
    q=J.bindings(raw);m=J.cold(raw);lua=LuaRuntime();P=lua.execute(POLICY.read_text());policy=P.new(kind)
    fields=q['fields'];score_at=W.address(m.bundle,'Player1ScoreDisplay');counts=Counter();events=[];tail=deque(maxlen=8);changes=deque(maxlen=8)
    collected=[];births=[];head=[];attack=[];life=[];sound=Counter();popups=[];objects=[];ctx={'inside':False};target=None;credit=None;done=False;fault=None
    def state():
        r=lambda n,i=0:N.get(m,n,i)
        return dict(x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),
            source_flags=m.ram[2][0x12],source_control=m.ram[2][0x13],grounded=not(m.ram[2][0x12]&4),
            hp=r('JnHealth'),maximum=r('JnMaxHearts'),tier=r('JnOwnedTier'),lives=r('NumberofLives'),
            status=r('PlayerStatus'),star=r('StarInvincibleTimer'),engine=r('GameEngineSubroutine'),
            camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'),score=int(''.join(str(m[score_at+i])for i in range(6))),
            weapon=m.ram[2][0x20],ammo=m.ram[2][0xbe],Main=counts['Main_returns'],motor=counts['motor_returns'])
    def actor(i):
        r=lambda n:N.get(m,n,i)
        return dict(slot=i,flag=r('Enemy_Flag'),id=r('Enemy_ID'),kind=r('PowerUpType'),state=r('Enemy_State'),
            x=r('Enemy_X_Position')+256*r('Enemy_PageLoc'),y=r('Enemy_Y_Position'),private=r('InvPickup'),owner=r('InvPickupOwner'),contact=r('PlatformCollisionFlag'))
    def actors():return[a for i in range(6)if(a:=actor(i))['flag']]
    def label(a):
        if a['owner']==16 and a['private']==129:return'mushroom'
        if a['owner']==16 and a['private']==130:return'flower'
        return{2:'star',3:'life'}.get(a['kind'],'other')
    def tag(pc):return m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
    def ret(c):
        pc=(m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1)&65535
        return pc,(c.sp+2)&255,tag(pc)
    base=N.NesMPU;points={(h['tag'],h['PC']):name for name,h in q['hooks'].items()if name in('GameLoop','JayIntegrate','HandlePowerUpCollision','PlayerHeadCollision','SetupFloateyNumber')}
    pc=W.address(m.bundle,'JnCollectPickup');at=W.location(m.bundle,'JnCollectPickup');points[((at-16)//8192)|128,pc]='JnCollectPickup'
    world=raw[1048592+234*1024+0x230:1048592+234*1024+0x2d4]
    match=list(re.finditer(b'\x98\xaa\x86.\x20(..)\x68\x85.\xae..\xa9\x1d\x4c',world,re.S));assert len(match)==1
    assert match[0].group()[3]==match[0].group()[9]==W.address(m.bundle,'ObjectOffset')
    attack_pc=int.from_bytes(match[0].group(1),'little');assert 0xb800<=attack_pc<0xbe30
    points[3,attack_pc]='JayCaptureAmmoDefeat'
    old_write=type(m).__setitem__;first_birth=set();private_returns=[];last_phase=None
    def after_main():
        nonlocal credit,done,last_phase
        s=state();aa=actors()
        assert s['lives']>=2 and s['hp']>0 and s['engine']!=11,('Actual Jay route injury/death',s)
        assert N.get(m,'SelectedCharacter')==16 and m[0x730b]&96==32
        assert N.get(m,'WorldNumber')==N.get(m,'LevelNumber')==N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
        assert tuple(bytes(m.ram[k][0x1fe0:0x1ff0])for k in(2,3))==(J.COOKIE,J.COOKIE)
        for a in aa:
            if a['id']==46:
                key=(a['slot'],label(a))
                if key not in first_birth:
                    assert len(births)<8;births.append(dict(label=label(a),actor=a,player=s));first_birth.add(key)
        if target and credit is None:
            if kind!='life'or(s['lives']==3 and life and sound[64]):
                credit=dict(Main=counts['Main_returns'],motor=counts['motor_returns'],state=s)
        if credit and counts['motor_returns']>=credit['motor']+25:
            if kind=='flower':
                done=bool(attack)and s['tier']==2 and s['maximum']==4 and s['hp']>0 and s['score']>=target['before']['score']+1000
            elif kind=='star':done=s['score']>=target['before']['score']+1000
            else:done=s['lives']==3
            if done:return
        st=lua.table_from(s);ar=lua.table_from([lua.table_from(a)for a in aa]);pad=policy.decide(policy,st,ar)
        assert isinstance(pad,int)and 0<=pad<=255
        phase=policy.phase
        if phase!=last_phase:changes.append(dict(Main=s['Main'],motor=s['motor'],phase=phase,x=s['x'],y=s['y']));last_phase=phase
        tail.append(dict(state=s,phase=phase,pad=pad,items=[a for a in aa if a['id']==46]))
        m.controller_pad=pad
    class CPU(base):
        def __init__(self,*a,**kw):super().__init__(*a,**kw);self.pending=[];objects.append(self)
        def settle(self):
            nonlocal target
            while self.pending and(self.pc,self.sp,tag(self.pc))==self.pending[-1]['return']:
                p=self.pending.pop();name=p['name'];counts[name+'_returned']+=1
                if name=='GameLoop':counts['Main_returns']+=1;after_main()
                elif name=='JayIntegrate':
                    counts['motor_returns']+=1
                    assert(self.pc,tag(self.pc))==(q['motion_callsite_PC']+11,3)
                elif name=='JnCollectPickup':private_returns.append(dict(C=self.p&1,Main=counts['Main_returns'],A=self.a))
                elif name=='HandlePowerUpCollision'and p['actor']['flag']and p['actor']['id']==46 and not N.get(m,'Enemy_Flag',p['actor']['slot']):
                    a=p['actor'];name=label(a);s=state();node=dict(label=name,item=a,before=p['before'],after=s,Main=counts['Main_returns'],motor=counts['motor_returns'])
                    assert len(collected)<8;collected.append(node);policy.collect(policy,name)
                    if name=='mushroom':
                        assert kind=='flower'and(s['hp'],s['maximum'],s['tier'])==(8,4,1)
                    if name==kind:
                        assert target is None and any(b['label']==kind for b in births),'Natural target birth before collector'
                        assert private_returns and private_returns[-1]['C']==int(kind=='flower'),'Actual owning private collector C1 or native fallback C0'
                        if kind=='flower':assert a['private']==130 and s['tier']==2 and s['maximum']==4 and 6 in popups and 32 in sound
                        elif kind=='star':assert s['star']==35 and N.get(m,'AreaMusicQueue')==64 and 6 in popups and 32 in sound
                        else:assert a['kind']==3 and 11 in popups and s['lives']==2,'Actual delayed native life admission'
                        target=node
                elif name=='JayCaptureAmmoDefeat'and target and kind=='flower':
                    a=p['victim'];after=actor(a['slot'])
                    assert a['id']==6 and a['flag']and not(a['state']&32)
                    assert after['state']&32 or not after['flag'],'Actual earned post-Flower projectile defeat'
                    if len(attack)<8:attack.append(dict(before=a,after=after,player=state(),Main=counts['Main_returns']))
        def step(self):
            self.settle();name=points.get((tag(self.pc),self.pc))
            if name:
                counts[name+'_entered']+=1
                if name=='PlayerHeadCollision':
                    if len(head)<8:head.append(dict(tile=self.a,player=state()))
                elif name=='SetupFloateyNumber':
                    if len(popups)<16:popups.append(self.a)
                else:
                    p=dict(name=name,return_=ret(self));p['return']=p.pop('return_')
                    if name=='HandlePowerUpCollision':p.update(actor=actor(self.x),before=state())
                    if name=='JayCaptureAmmoDefeat':p['victim']=actor(self.x)
                    self.pending.append(p)
            ctx.update(inside=True,PC=self.pc,tag=tag(self.pc),opcode=m[self.pc])
            try:return super().step()
            finally:ctx['inside']=False
    def write(bus,at,value):
        if bus is m and ctx['inside']:
            if at==fields['Square2SoundQueue']and value in(32,64):sound[value]+=1
            if at==fields['NumberofLives']and value==3:
                assert ctx['opcode']==0xee,'Real native INC life opcode'
                if len(life)<4:life.append(dict(PC=ctx['PC'],tag=ctx['tag'],opcode=ctx['opcode'],Main=counts['Main_returns'],motor=counts['motor_returns']))
        return old_write(bus,at,value)
    try:
        with patch.object(N,'NesMPU',CPU),patch.object(type(m),'__setitem__',write):
            for epoch in range(limit):
                Frames.frame(m,whole_pass=True)
                for c in objects:c.settle();assert not c.pending
                objects.clear()
                if done:break
    except Exception as error:
        fault=dict(error=repr(error),context=dict(ctx),state=state(),actors=actors(),
            pending=[dict(PC=c.pc,SP=c.sp,tag=tag(c.pc),scopes=[p['name']for p in c.pending])for c in objects])
    for name in('GameLoop','JayIntegrate','HandlePowerUpCollision','JnCollectPickup','JayCaptureAmmoDefeat'):
        if fault is None:assert counts[name+'_entered']==counts[name+'_returned'],(name,counts)
    result=dict(passed=done and fault is None,fault=fault,kind=kind,owning_SHA256=J.PIN,metadata91dc_only=J.Frozen.PIN,facade_SHA256=J.H(Path(J.__file__).read_bytes()),policy_SHA256=J.H(POLICY.read_bytes()),
        Main=counts['Main_returns'],motor=counts['motor_returns'],counts=dict(counts),target=target,credit=credit,
        collected=collected,births=births,head=head,attack=attack,life=life,sound=sound,popups=popups,
        private_collect_returns=private_returns[-8:],terminal=state(),phase_changes=list(changes),tail=list(tail),
        original_motor_return_PC=q['motion_callsite_PC']+11,attack_capture_PC=attack_pc,
        controller_only=True,generated_files=0,native=False,no_gameplay_or_actor_or_health_seeds=True)
    result['receipt_SHA256']=J.H(json.dumps(result,sort_keys=True,separators=(',',':')).encode());return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=('flower','star','life'),required=True);p.add_argument('--limit',type=int,default=1800);a=p.parse_args()
    assert 100<=a.limit<=2600
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Natural Jay route attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,a.kind,a.limit)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
