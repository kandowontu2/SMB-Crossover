"""Exact1124 ordinary lift/reach controls: post-lift ground gate observer.

In-memory source model only. No game-state writes, ROM files or emulator.
"""
import json
import argparse
from collections import deque
from pathlib import Path
from unittest.mock import patch

import probe_prince_lift_swept_plane_1123 as Sweep
import run_prince_oneup_lift_native_1123 as Native

C,R,F,H,W,N = Sweep.C,Sweep.R,Sweep.F,Sweep.H,Sweep.W,Sweep.N
CONTROL='29949711ed25a1a045fa29ebc6f9d9461b1e03794d0026660780016c9978931e'
IMAGE='1124ad4219fdee26306a369092f921b9eee35728e8ab19fd66d95cc34e6d3e9c'
OLD=bytes.fromhex('ad11c6c9c4')
NEW=bytes.fromhex('ad85c0c901')


def ground_fixture(seed, origin=-3, sy=193):
    m=F.scene(F.authored(seed),x=1018,top=75)
    F.slot(m,'Enemy_Y_Position',75)
    F.slot(m,'Enemy_BoundBoxCtrl',6)
    N.put(m,Player_Y_Position=(sy+origin+5)-32,Player_Y_HighPos=1,
          Player_State=2,Player_Y_Speed=0,PlayerFacingDir=2,
          PlayerStatus=1,PlayerSize=0,
          ScreenLeft_X_Pos=156,ScreenLeft_PageLoc=3,
          SavedJoypadBits=0,SavedJoypad1Bits=0,A_B_Buttons=0,
          Left_Right_Buttons=0,Up_Down_Buttons=0)
    s=m.ram[2]
    for at,value in ((0x611,sy),(0x8b,sy),(0x88,5),(0x616,7),(0x617,106),
                     (0x618,4),(0xa6,3),(0x4e1,0),(0x4e2,12),
                     (0x6db,0),(0x4d4,0),(0x6da,2),(0x6dd,0),(0x6cf,4)):
        s[at]=value
    s[0x89:0x8b]=origin.to_bytes(2,'little',signed=True)
    foot=sy+origin+5;s[0x84:0x88]=foot.to_bytes(2,'little')*2
    return m


def isolated(image,overlay):
    seed=R.cold(image,overlay)
    for _ in range(12):seed.controller_pad=0;R.Engine.Frames.frame(seed,cold=True)
    assert bytes(seed.ram[3][0x62c:0x631])==OLD
    before=ground_fixture(seed);after=N.fork(before)
    after.ram[3][0x62c:0x631]=NEW
    rows=[];base=N.NesMPU
    def state(m):
        s=m.ram[2]
        return dict(sourceY=s[0x611],origin=int.from_bytes(s[0x89:0x8b],'little',signed=True),
                    foot=int.from_bytes(s[0x84:0x86],'little'),prior=int.from_bytes(s[0x86:0x88],'little'),
                    action_pose_mode=list(s[0x616:0x619]),surface=list(s[0x7f:0x83]),
                    HP=s[0x6cf],lives=N.get(m,'NumberofLives'),x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
                    y=N.get(m,'Player_Y_Position'))
    class Spy(base):
        def step(self):
            m=self.memory;pc=self.pc
            tag=m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else None
            old=bytes(m.ram[2][0x616:0x619]);q=super().step()
            if bytes(m.ram[2][0x616:0x619])!=old:
                rows.append(dict(PC=hex(pc),bank=tag,before=list(old),after=list(m.ram[2][0x616:0x619])))
            return q
    old_call=F.private(before,0xb36e)
    with patch.object(N,'NesMPU',Spy):new_call=F.private(after,0xb36e)
    first=dict(baseline=state(before),patched=state(after),writers=rows,
               baseline_call=old_call,patched_call=new_call)
    print('PRINCE_GROUND_ISOLATED_FIRST '+json.dumps(first,separators=(',',':')),flush=True)
    assert first['baseline']['action_pose_mode'][0]==7
    assert first['patched']['action_pose_mode'][0]==17
    assert any(r['PC']=='0xa352'and r['bank']==3 for r in rows)
    samples=[]
    for i in range(96):
        after.controller_pad=0;R.Engine.Frames.frame(after,cold=True)
        if i%12==0:samples.append(dict(update=i,**state(after)))
        assert N.get(after,'NumberofLives')==2 and after.ram[2][0x6cf]==4,samples
    assert list(after.ram[2][0x616:0x619])==[0,15,0],samples
    assert 206<=int.from_bytes(after.ram[2][0x84:0x86],'little')<=211,samples
    pairs=0
    for origin,sy in ((77,115),(61,131),(29,163),(0,190)):
        a=ground_fixture(seed,origin,sy);b=N.fork(a);b.ram[3][0x62c:0x631]=NEW
        qa=F.private(a,0xb36e);qb=F.private(b,0xb36e)
        if sy+14<196:
            assert qa==qb and bytes(a.ram[2])==bytes(b.ram[2]),(origin,sy,state(a),state(b))
            pairs+=1
    lifts=[]
    for name,make in (('fresh-swept',Sweep.fixture),('held-pose106',Sweep.held_fixture)):
        a=make(seed);F.slot(a,'Enemy_BoundBoxCtrl',6)
        b=N.fork(a);b.ram[3][0x62c:0x631]=NEW
        qa=Sweep.observe(a);qb=Sweep.observe(b)
        assert qa==qb and bytes(a.ram[2])==bytes(b.ram[2]),name
        assert qb['native']['flag']==5 and qb['final_source']['action_pose_mode'][0]==17,name
        lifts.append(name)
    result=dict(ROM=H(image),preimage=OLD.hex(),replacement=NEW.hex(),first=first,
        subsequent_actual_Main_updates=96,final=state(after),samples=samples,
        ordinary_in_range_Worker_pairs=pairs,lift_Worker_and_native_collision_pairs=lifts,translated_fixture=True,
        full_linked_fix_or_native_not_claimed=True,outputs=0)
    digest=H(json.dumps(result,sort_keys=True,separators=(',',':')).encode())
    print('PRINCE_GROUND_ISOLATED '+json.dumps(dict(result,SHA256=digest),separators=(',',':')),flush=True)
    return result


def run(image,overlay,text):
    b=dict(W.Symbols.bundle(),raw=image)
    at={n:W.address(b,n)for n in (
        'Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos',
        'GameEngineSubroutine','Player_State','Player_Y_Speed','NumberofLives',
        'Enemy_Flag','Enemy_ID','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position',
        'PlatformCollisionFlag','FrameCounter')}
    game=W.address(b,'GameLoop');game_tag=128+(W.location(b,'GameLoop')-16)//8192
    base=N.NesMPU;clock=[0];rows=deque(maxlen=80);last_key=[None];flag=[False];progress=[0]
    sites={0xa5d9:'Terrain',0xa62c:'LoadRawY',0xa62f:'RawY-limit',0xa631:'RawY-branch',
           0xa640:'Terrain-early-return',0xa6f6:'Material-call',0xa70b:'Material-gateway',
           0xa80d:'Landing-gate',0xa836:'Original-align',0xa352:'Original-state-write',
           0xb3bd:'After-terrain',0xb3c0:'OldFoot-write'}

    def row(cpu,name):
        m=cpu.memory;s=m.ram[2]
        read=lambda name,index=0:m[at[name]+index]
        x=read('Player_X_Position')+256*read('Player_PageLoc')
        actors=[]
        for i in range(6):
            if read('Enemy_Flag',i)==1 and read('Enemy_ID',i)==37:
                actors.append([i,read('Enemy_X_Position',i)+256*read('Enemy_PageLoc',i),
                               read('Enemy_Y_Position',i),read('PlatformCollisionFlag',i)])
        return dict(site=name,Main=clock[0],frame=read('FrameCounter'),PC=hex(cpu.pc),
            A=cpu.a,P=cpu.p,x=x,y=read('Player_Y_Position'),high=read('Player_Y_HighPos'),
            ground=read('Player_State'),speed=read('Player_Y_Speed'),lives=read('NumberofLives'),
            sourceY=s[0x611],lastY=s[0x8b],origin=int.from_bytes(s[0x89:0x8b],'little',signed=True),
            delta=int.from_bytes(s[0x88:0x89],'little',signed=True),
            foot=int.from_bytes(s[0x84:0x86],'little'),prior=int.from_bytes(s[0x86:0x88],'little'),
            action_pose_mode=list(s[0x616:0x619]),phase=s[0xa6],
            surface=list(s[0x7f:0x83]),floor=list(s[0x9b:0xa0]),actors=actors)

    class Spy(base):
        def step(self):
            m=self.memory;pc=self.pc
            tag=m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else None
            if pc==game and tag==game_tag and m[at['GameEngineSubroutine']]==8:clock[0]+=1
            if tag==3 and pc in sites and m[at['GameEngineSubroutine']]==8:
                x=m[at['Player_X_Position']]+256*m[at['Player_PageLoc']]
                s=m.ram[2]
                if 975<=x<=1048 and (s[0x84]<120 or s[0x616]in(28,14)):flag[0]=True
                if flag[0] and 975<=x<=1048:
                    entry=row(self,sites[pc])
                    key=(clock[0],pc)
                    if key!=last_key[0]:
                        rows.append(entry);last_key[0]=key
                        if pc==0xa631 and entry['sourceY']>=196 and progress[0]<8:
                            progress[0]+=1
                            print('PRINCE_GROUND_PROGRESS '+json.dumps(entry,separators=(',',':')),flush=True)
            return super().step()

    with patch.object(N,'NesMPU',Spy),patch.object(R.Engine.J,'cold',lambda raw:R.cold(raw,overlay)),patch.object(R.Engine.J,'PIN',H(image)):
        result=R.Engine.run(image,3800,text=text)
    return dict(execution=result,trace=list(rows),high_reach_seen=flag[0])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--isolated',action='store_true')
    args=parser.parse_args()
    parent=R.P.G.ROM.read_bytes();assert H(parent)==C.PARENT
    image,overlay=C.compose(parent,Sweep.hold_plane_plan)
    text=Native.controller(parent,image,overlay,'pickup',False,True,True,True)
    assert H(image)==IMAGE and H(text.encode())==CONTROL
    print('PRINCE_GROUND_BIND '+json.dumps(dict(ROM=H(image),controller=CONTROL,outputs=0),separators=(',',':')),flush=True)
    def deny(*a,**k):raise AssertionError('Ground observer attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        if args.isolated:return isolated(image,overlay)
        result=run(image,overlay,text)
    receipt=result['execution'].get('receipt',{})
    stock=receipt.get('natural_stock',{})
    summary=dict(ROM=H(image),controller=CONTROL,trace=result['trace'],
        high_reach_seen=result['high_reach_seen'],
        execution={k:v for k,v in result['execution'].items()if k!='receipt'},
        receipt={k:receipt[k]for k in ('passed','reason','terminal','phase','Main_returns')if k in receipt},
        lift={k:v for k,v in stock.get('lift',{}).items()if k in
            ('boarded','request','admission','reached_apex','contacts','moving_contacts','attempts')},outputs=0)
    digest=H(json.dumps(summary,sort_keys=True,separators=(',',':')).encode())
    print('PRINCE_GROUND_RESULT '+json.dumps(dict(summary,SHA256=digest),separators=(',',':')),flush=True)


if __name__=='__main__':main()
