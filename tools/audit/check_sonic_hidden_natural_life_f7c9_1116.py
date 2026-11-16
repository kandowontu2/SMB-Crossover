"""Actual leasedf7 cold, ceiling, natural1UP and returned-worker witnesses."""
from pathlib import Path
from unittest.mock import patch
from collections import Counter,deque
import argparse,json,struct
import current_sonic_hidden_heads_f7c9_1116 as F
import sonic_natural_life_braked_policy_1327_1116 as Policy
from check_ff_stdout_controller_source_1110 import LuaRuntime

F_SHA='7bc61c4e600ef6b9264b8c8b8ff308b7d806b3b0e558567b4cc6ebd7f4f93796'
POLICY_SHA='3226b589d1b7c0baa090bf4b60a49e8db1d76687938211c773eb75dfd6b9c845'


def run(raw,form='sonic',limit=1200):
    assert F.H(Path(F.__file__).read_bytes())==F_SHA and F.H(Path(Policy.__file__).read_bytes())==POLICY_SHA
    q=F.bindings(raw);N,W=F.N,F.W;counts=Counter();objects=[];pending=[]
    ctx={'phase':'cold','PC':-1,'tag':-1,'SP':-1};m=None;policy=None;lua=None
    heads=[];births=[];mature=[];collect=[];credit=[];sounds=Counter();jumps=[];reset=[];tail=deque(maxlen=8);changes=[]
    finished=False;fault=None;lastphase=None;ring=[];oldring=0;life_pending=None
    fields=q['fields'];b=q['bundle'];points={}
    for name in('GameLoop','SonicHostMain','HandlePowerUpCollision','PlayerHeadCollision'):
        h=q['hooks'][name];points[(h['tag'],h['PC'])]=name
    points[(3,0xbbb0)]='OriginalFrame'
    at=W.location(b,'FloateyNumbersCore');data=raw[at:at+256]
    needle=b'\xee'+fields['NumberofLives'].to_bytes(2,'little');assert data.count(needle)==1
    at+=data.index(needle);lifePC=(W.address(b,'FloateyNumbersCore')&0xe000)+((at-16)&8191);lifeTag=((at-16)//8192)|128
    def tag(pc):return m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
    def signed(at):
        v=int.from_bytes(bytes(m.ram[2][at:at+3]),'little');return v-(1<<24)if v&(1<<23)else v
    def state():
        r=lambda n:N.get(m,n)
        return dict(x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),state=r('Player_State'),
            source_flags=m.ram[2][0x30],vx=signed(0x20),vy=signed(0x60),frame_status=m.ram[2][0x116],
            source_tick=m.ram[2][0x92],ready=m.ram[2][0x119],have_epoch=m.ram[2][0x11a],
            source_x=int.from_bytes(bytes(m.ram[2][0x71:0x73]),'little'),status=r('PlayerStatus'),rings=m.ram[2][0x340],
            ringLives=m.ram[2][0x341],hurt=m.ram[2][0x34f],sourceStar=m.ram[2][0x350],lives=r('NumberofLives'),
            engine=r('GameEngineSubroutine'),Main=counts['GameLoop_returns'],motor=counts['accepted_original'],saved=r('SavedJoypadBits'),
            source_input=m.ram[2][0xa8],native_yhigh=r('Player_Y_HighPos'),camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'))
    def actors():
        rows=[]
        for i in range(6):
            r=lambda n:N.get(m,n,i)
            if r('Enemy_Flag'):rows.append(dict(slot=i,flag=r('Enemy_Flag'),id=r('Enemy_ID'),kind=r('PowerUpType'),state=r('Enemy_State'),
                x=r('Enemy_X_Position')+256*r('Enemy_PageLoc'),y=r('Enemy_Y_Position')))
        return rows
    def after_main():
        nonlocal finished,lastphase,oldring
        s=state();aa=actors()
        assert N.get(m,'SelectedCharacter')==43 and m[0x5ffe]==F.FORMS[form][0]
        assert s['lives']in(2,3)and s['engine']!=11 and N.get(m,'WorldNumber')==N.get(m,'LevelNumber')==0,('Living real1-1',s)
        assert N.get(m,'CheatStartLevel')==N.get(m,'CheatInvincible')==0
        assert tuple(bytes(m.ram[k][0x1fe0:0x1ff0])for k in(2,3))==(F.COOKIE,)*2
        if oldring!=s['rings']:
            assert len(ring)<12;ring.append(dict(before=oldring,after=s['rings'],state=s));oldring=s['rings']
        for a in aa:
            if a['id']==46 and a['kind']==3:
                if not births:
                    assert heads and a['x']==1024;births.append(dict(actor=a,state=s))
                if a['state']&128 and not mature:mature.append(dict(actor=a,state=s))
        if credit and s['motor']>=credit[0]['state']['motor']+25:
            assert s['lives']==3 and s['rings']==collect[0]['before']['rings']==5 and s['status']==0
            assert mature and collect and sounds[64]and not reset,'Mature physical1UP, realcredit/cue and no reset'
            assert all(counts[n+'_entries']==counts[n+'_returns']for n in('GameLoop','SonicHostMain','OriginalFrame'))
            finished=True;return
        pad=policy.decide(policy,lua.table_from(s),lua.table_from([lua.table_from(a)for a in aa]));assert isinstance(pad,int)and 0<=pad<=255
        phase=policy.phase
        if phase!=lastphase:
            assert len(changes)<16;changes.append(dict(phase=phase,state=s,pad=pad));lastphase=phase
        tail.append(dict(state=s,phase=phase,pad=pad));m.controller_pad=pad
    baseCPU=N.NesMPU;baseBus=W.ControllerBus
    class Bus(baseBus):
        def __setitem__(self,at,value):
            if isinstance(at,int)and ctx['phase']=='route':
                if at==fields['Square2SoundQueue']and value in(32,64):sounds[value]+=1
                if at>=0x8000 and self.rawtags[(at-0x8000)//8192]==2 and at&8191 in(0x71,0x72)and heads:
                    before=int.from_bytes(bytes(self.ram[2][0x71:0x73]),'little');low=at&8191
                    after=(before&0xff00|value&255)if low==0x71 else(before&255|(value&255)<<8)
                    if before>=900 and after<500 and len(reset)<4:reset.append(dict(PC=ctx['PC'],tag=ctx['tag'],SP=ctx['SP'],address=at,before=before,after=after,state=state()))
            return super().__setitem__(at,value)
    class CPU(baseCPU):
        def __init__(self,*a,**kw):super().__init__(*a,**kw);self.pending=[];objects.append(self)
        def settle(self):
            nonlocal life_pending
            if ctx['phase']!='route':return
            if life_pending and(self.pc,self.sp,tag(self.pc))==life_pending['return']:
                assert N.get(m,'NumberofLives')==3
                credit.append(dict(PC=lifePC,tag=lifeTag,before=life_pending['before'],state=state()));life_pending=None
            while self.pending and(self.pc,self.sp,tag(self.pc))==self.pending[-1]['return']:
                p=self.pending.pop();name=p['name'];counts[name+'_returns']+=1
                if name=='OriginalFrame':counts['accepted_original'if self.p&1 else'rejected_original']+=1
                elif name=='GameLoop':after_main()
                elif name=='HandlePowerUpCollision'and p['actor']is not None and N.get(m,'Enemy_Flag',p['actor']['slot'])==0:
                    a=p['actor'];s=state();assert a['id']==46 and a['kind']==3 and births and heads
                    assert N.get(m,'FloateyNum_Control',a['slot'])==11 and s['lives']==2 and sounds[32]>p['cue32']
                    assert not collect;collect.append(dict(actor=a,before=p['before'],state=s,popup=11,cue32=sounds[32]-p['cue32']))
        def step(self):
            nonlocal life_pending
            if ctx['phase']=='route':
                self.settle();t=tag(self.pc);name=points.get((t,self.pc))
                if(t,self.pc)==(3,0xbb26):counts['selector']+=1
                if(t,self.pc)==(2,0xd344):counts['helper']+=1
                if(t,self.pc)==(lifeTag,lifePC)and collect and not credit:
                    assert N.get(m,'NumberofLives')==2;life_pending=dict(before=state(),return_ignored=False,**{'return':((lifePC+3)&65535,self.sp,t)})
                if name=='PlayerHeadCollision':
                    if self.a==0x60:
                        assert len(heads)<2;heads.append(dict(PC=self.pc,tag=t,SP=self.sp,tile=self.a,state=state(),query=dict(axis=m.ram[2][0xb7],negative=m.ram[2][0xb8],kind=m.ram[2][0xb6])))
                        assert state()['vy']>=0 and m.ram[2][0xb6]==4,'Actual original ceiling clip before native head'
                elif name:
                    counts[name+'_entries']+=1;sp=self.sp;pc=(m[0x100+((sp+1)&255)]+256*m[0x100+((sp+2)&255)]+1)&65535
                    p=dict(name=name,**{'return':(pc,(sp+2)&255,tag(pc))})
                    if name=='HandlePowerUpCollision':
                        a=next((a for a in actors()if a['slot']==self.x and a['id']==46 and a['kind']==3),None)
                        p.update(actor=a,before=state(),cue32=sounds[32])
                    self.pending.append(p)
            else:
                if self.pc>=0x8000 and self.memory.rawtags[(self.pc-0x8000)//8192]==2:assert self.pc!=0xd344,'No helper before fullcold readback'
            ctx.update(PC=self.pc,tag=self.memory.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1,SP=self.sp)
            return super().step()
    cold=None
    try:
        with patch.object(W,'ControllerBus',Bus),patch.object(N,'NesMPU',CPU),patch.object(W.UI.F,'NesMPU',CPU):
            m,cold=F.cold(raw,form);objects.clear();ctx['phase']='route'
            lua=LuaRuntime();lua.globals().SONIC_READ=lambda n,i=0:N.get(m,n,i);lua.globals().SONIC_MEMORY=lambda at:m[at]
            policy=lua.execute(Policy.text()).new('life')
            for _ in range(limit):
                F.Frames.frame(m,whole_pass=True)
                for c in objects:c.settle();assert not c.pending
                objects.clear()
                if finished:break
    except Exception as e:fault=dict(error=repr(e),context=dict(ctx),state=state()if m is not None else None)
    out=dict(passed=finished and fault is None,ROM_SHA256=F.PIN,form=form,cold=cold,fault=fault,counts=dict(counts),
        heads=heads,births=births,mature=mature,collected=collect,credit=credit,sounds=dict(sounds),source_position_resets=reset,
        ring_changes=ring,phase_changes=changes,tail=list(tail),terminal=state()if m is not None else None,
        source_SHA256=F.H(Path(__file__).read_bytes()),facade_SHA256=F_SHA,policy_SHA256=F.H(Policy.text().encode()),
        native=False,outputs=0,gameplay_or_actor_or_resource_or_helper_seeds=False)
    out['receipt_SHA256']=F.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--form',choices=tuple(F.FORMS),default='sonic');a.add_argument('--limit',type=int,default=1200);a=a.parse_args();assert 500<=a.limit<=1500
    def deny(*a,**kw):raise AssertionError('Source natural1UP attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(F.load_current_image(),a.form,a.limit)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
