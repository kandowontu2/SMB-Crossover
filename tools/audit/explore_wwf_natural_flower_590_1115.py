"""Actual590 compiled WWF M/Flower ordinary-control source exploration."""
from collections import Counter,deque
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import argparse,json

import replay_named_world_images_590_1115 as Images
import check_shared_world_sprite_images_1114 as Cold
import check_wwf_role_palette_1110 as Packet

W,N,Frames=Images.DK.W,Images.DK.N,Cold.Frames
PIN=Images.PIN
IDENTITIES={k:v for k,v in Images.IDENTITIES.items()if k!='donkey_kong'}


def config(raw,key):
    assert key in IDENTITIES and sha256(raw).hexdigest()==PIN
    _,parent=Images.owning(raw)
    q=Images.WWF.bindings(parent,key)
    assert(q['owner'],q['role'])==(29,IDENTITIES[key][-1])
    return q


def explore(raw,key,limit=3200):
    cfg=config(raw,key);b=dict(W.Symbols.bundle(),raw=raw)
    expected=Packet.cookies(raw,b);at=W.location(b,'WfCookieC')
    assert len(expected)==96 and raw[at:at+96]==expected
    factory=SimpleNamespace(bindings=lambda image,k:config(image,k))
    with patch.object(Cold,'Factory',factory):m=Cold.cold(raw,key)
    current=dict(Main=0,phase='first-M',moves=0)
    events=[];recent=deque(maxlen=16);items={};pending=None;calls=Counter()
    jump=None;pipe=0;travel_jump=None;cooldown=0;cross_start=None;retreat_settle=0
    original=N.NesMPU
    hooks={name:((W.location(b,name)-16)//8192|128,W.address(b,name))for name in
        ('WfMovement','HandlePowerUpCollision','GuestPowerupUpdate')}
    def score():
        digits=[N.get(m,'Player1ScoreDisplay',i)for i in range(6)]
        assert all(0<=x<10 for x in digits)
        return int(''.join(map(str,digits)))
    def state():
        return dict(Main=current['Main'],phase=current['phase'],moves=current['moves'],
            x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
            y=N.get(m,'Player_Y_Position'),high=N.get(m,'Player_Y_HighPos'),
            native=N.get(m,'Player_State'),vy=N.get(m,'Player_Y_Speed'),
            engine=N.get(m,'GameEngineSubroutine'),power=N.get(m,'PlayerStatus'),
            active=N.get(m,'GuestPowerupActive'),age=N.get(m,'GuestPowerupAge'),
            lives=N.get(m,'NumberofLives'),score=score())
    def actor(i):
        return dict(slot=i,flag=N.get(m,'Enemy_Flag',i),id=N.get(m,'Enemy_ID',i),
            state=N.get(m,'Enemy_State',i),kind=N.get(m,'PowerUpType',i),
            x=N.get(m,'Enemy_X_Position',i)+256*N.get(m,'Enemy_PageLoc',i),
            y=N.get(m,'Enemy_Y_Position',i))
    def actors():return[a for i in range(6)if(a:=actor(i))['flag']]
    def note(kind,**extra):
        assert len(events)<48
        events.append(dict(event=kind,state=state(),**extra))
    def phase(name):current['phase']=name;note('phase')
    def active(s):return N.get(m,'OperMode')==1 and N.get(m,'OperMode_Task')==3 and s['engine']==8
    def punch():return(68 if cfg['role']==3 else 64)if current['Main']%18<3 else 0
    def nearby(s,aa):
        return any(a['flag']<128 and a['id']<21 and a['state']&32==0
            and 0<a['x']-s['x']<=44 and abs(a['y']-s['y'])<40 for a in aa)
    class CPU(original):
        def step(self):
            nonlocal pending
            tag=self.memory.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            if pending and(self.pc,self.sp)==pending['return_to']:
                p=pending;pending=None;a=actor(p['slot']);item=items[p['kind']]
                assert self.p&1 and a['flag']==0 and N.get(m,'FloateyNum_Control',p['slot'])==6
                assert N.get(m,'GuestPowerupActive')==1 and N.get(m,'GuestPowerupAge')==0
                assert N.get(m,'GameEngineSubroutine')==9 and N.get(m,'TimerControl')==255
                item['collected']=dict(before=p['before'],after=state(),return_PC=self.pc,return_SP=self.sp,
                    cue=N.get(m,'Square2SoundQueue'),carry=self.p&1)
                assert item['collected']['cue']&32
                phase('freeze-M'if p['kind']==0 else'freeze-F')
                note('actual-collection-return',pickup_kind=p['kind'])
            if(tag,self.pc)==hooks['WfMovement']:
                current['moves']+=1;calls['WfMovement']+=1
            elif(tag,self.pc)==hooks['GuestPowerupUpdate']and N.get(m,'GuestPowerupActive'):
                kind=0 if current['phase']=='freeze-M'else 1
                item=items[kind];assert item.get('collected')
                assert N.get(m,'GuestPowerupAge')==item['ticks']
                item['ticks']+=1;assert item['ticks']<=60
            elif(tag,self.pc)==hooks['HandlePowerUpCollision']:
                a=actor(self.x)
                if a['id']==46 and a['flag']==1:
                    kind=a['kind'];assert kind in(0,1)and kind in items
                    item=items[kind]
                    assert item.get('mature')and a['state']>=128 and not item.get('collected')and not pending
                    assert(kind==0 and a['x']<600)or(kind==1 and a['x']==1248)
                    ret=m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1
                    pending=dict(kind=kind,slot=self.x,before=state(),return_to=(ret,(self.sp+2)&255))
                    note('actual-native-collector',actor=a)
            return super().step()
    failure=None;passed=False;steps=0
    try:
        with patch.object(N,'NesMPU',CPU):
            for tick in range(limit):
                current['Main']=tick;s=state();aa=actors()
                assert N.get(m,'SelectedCharacter')==29 and N.get(m,'FmGroups')&7==cfg['role']
                assert N.get(m,'WorldNumber')==N.get(m,'LevelNumber')==0 and s['lives']==2
                for a in aa:
                    if a['flag']==1 and a['id']==46 and(a['x']<600 or a['x']==1248):
                        kind=0 if a['x']<600 else 1
                        assert a['kind']==kind,('Final actual native kind',a,s)
                        if kind not in items:
                            items[kind]=dict(born=dict(player=s,actor=a),ticks=0)
                            note('authored-birth',actor=a)
                        if a['state']>=128 and not items[kind].get('mature'):
                            items[kind]['mature']=dict(player=s,actor=a);note('mature',actor=a)
                bits=0;p=current['phase']
                if s['active']:
                    assert p in('freeze-M','freeze-F')
                elif p in('freeze-M','freeze-F'):
                    kind=0 if p=='freeze-M'else 1;item=items[kind]
                    assert item['ticks']==60 and s['power']==kind+1 and active(s)
                    item['recovered']=s;item['resume_moves']=current['moves'];phase('post-M'if kind==0 else'post-F')
                elif p in('post-M','post-F'):
                    kind=0 if p=='post-M'else 1;item=items[kind]
                    item['resumed']=current['moves']-item['resume_moves']
                    if item['resumed']>=25:
                        assert item['resumed']==25 and s['score']>=item['collected']['before']['score']+1000
                        item['ready']=s
                        if kind==1:passed=True;break
                        phase('travel')
                elif active(s):
                    if p=='first-M':
                        if jump is not None and tick-jump<18:bits=128
                        elif nearby(s,aa):bits=punch()
                        elif jump is None and s['x']>=328:jump=tick;bits=128
                        else:bits=1 if s['x']<401 else 0
                    elif p=='travel':
                        starts=(404,564,692,868);ends=(484,644,772,948)
                        if pipe<4 and s['x']>=ends[pipe]and s['native']==0:pipe+=1
                        if s['x']>=1184 and s['native']==0:
                            assert s['power']==1,('Earned Mushroom armor before Flower',s)
                            phase('flower-align')
                        else:
                            bits=1
                            if travel_jump is not None:
                                age=tick-travel_jump
                                if age<4 or s['vy']>=128:bits|=128
                                if age>12 and s['native']==0:travel_jump=None;cooldown=8
                            elif cooldown:cooldown-=1
                            elif s['native']==0:
                                if pipe<4 and s['x']>=starts[pipe]:travel_jump=tick;bits|=128
                                elif nearby(s,aa):bits=punch()
                    elif p=='flower-align':
                        if s['x']<1239:bits=1
                        elif s['x']>1241:bits=2
                        elif s['native']==0:
                            jump=tick;bits=128;phase('flower-spawn')
                    elif p=='flower-spawn':
                        if 1 in items:phase('flower-mature')
                        else:
                            assert tick-jump<120,('Flower head bump was not admitted',s)
                            if tick-jump<24:bits=128
                    elif p=='flower-mature':
                        if items[1].get('mature')and s['native']==0:phase('flower-retreat')
                    elif p=='flower-retreat':
                        if s['x']>1200:bits=2
                        elif s['native']==0:
                            retreat_settle+=1
                            if retreat_settle>=4:
                                cross_start=tick;bits=129;phase('flower-cross')
                    elif p=='flower-cross':
                        assert tick-cross_start<160,('Flower roof approach',s)
                        bits=1 if s['x']<1245 else 2 if s['x']>1253 else 0
                        if tick-cross_start<4 or s['vy']>=128:bits|=128
                if tick%100==0:recent.append(dict(**s,pad=bits,actors=aa))
                if tick%500==499:print('PROGRESS '+json.dumps(s,separators=(',',':')),flush=True)
                m.controller_pad=bits;Frames.frame(m,whole_pass=True);steps=tick+1
    except AssertionError as e:failure=str(e)
    result=dict(passed=passed,identity=key,ROM_SHA256=PIN,role=cfg['role'],source_Main=steps,
        final=state(),items=items,events=events,recent=list(recent),calls=dict(calls),failure=failure,
        all6_cookie_SHA256=sha256(expected).hexdigest(),outputs=0,gameplay_seeds=0,Mesen_run=False,
        scope='Ordinary source exploration of real M then Flower/60-tick transactions/+25 moves; no native or full-stage claim')
    result['receipt_SHA256']=sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=IDENTITIES,default='hogan');a=p.parse_args()
    raw=Images.ROM.read_bytes()
    def deny(*args,**kwargs):raise AssertionError('Source exploration attempted output/Mesen')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):q=explore(raw,a.identity)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Natural WWF Flower remains source-unqualified'
