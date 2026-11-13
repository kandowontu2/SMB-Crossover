"""Directed native/source contact differential; no ROM/gameplay qualification."""
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import compose_dkjr_helper_retire_1113 as P
import check_dkjr_head_bridge_1113 as H

B,N,W,L=P.B,H.N,H.W,H.L
SLOT=3


def field(m,name,value):
    m[W.address(m.bundle,name)+SLOT]=value


def view(m):
    return dict(nativeY=N.get(m,'Player_Y_Position'),sourceY=m.ram[2][0x210],
        source=m.ram[2][0x6b],prior=m.ram[2][0x6c],fallStart=m.ram[2][0x76],
        fallLimit=m.ram[2][0x7b],top=N.get(m,'Enemy_Y_Position',SLOT),
        passenger=N.get(m,'PlatformCollisionFlag',SLOT),
        playerBox=list(m[0x658:0x65c]),helperBox=list(m[0x65c+4*SLOT:0x660+4*SLOT]),
        query=list(m.ram[2][0x8ea:0x8ec]),count=m.ram[2][0x8dd])


def setup(seed):
    m=L.clone(seed)
    for i in range(6):N.invoke(m,'EraseEnemyObject',x=i)
    # Declared component fixture: one pipe-top solid and one native vertical
    # actor at the observed coordinates. No natural-route result is claimed.
    m[0x300:0x4a0]=bytes(416)
    for x in(912,928):m[0x3d0+112+((x>>4)&15)]=0x61
    N.put(m,SelectedCharacter=40,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,
        TimerControl=0,Player_X_Position=939&255,Player_PageLoc=939>>8,
        Player_Y_Position=112,Player_Y_HighPos=1,Player_Y_Speed=0,Player_State=0,
        ScreenLeft_X_Pos=848&255,ScreenLeft_PageLoc=848>>8,
        ScreenRight_X_Pos=(848+255)&255,ScreenRight_PageLoc=(848+255)>>8,
        SavedJoypadBits=0,SavedJoypad1Bits=0,NmiDisable=255,FamilyMainCommit=1)
    for name,value in dict(Enemy_ID=37,Enemy_Flag=1,Enemy_X_Position=944&255,
        Enemy_PageLoc=944>>8,Enemy_Y_Position=137,Enemy_Y_HighPos=1).items():field(m,name,value)
    N.invoke(m,'InitEnemyObject',x=SLOT)
    for name,value in dict(Enemy_ID=37,Enemy_Flag=1,Enemy_State=0,Enemy_X_Position=944&255,
        Enemy_PageLoc=944>>8,Enemy_Y_Position=137,Enemy_Y_HighPos=1,
        Enemy_BoundBoxCtrl=5,PlatformCollisionFlag=255).items():field(m,name,value)
    N.invoke(m,'HuFresh')
    N.invoke(m,'HuMovement')
    N.invoke(m,'RelativePlayerPosition',x=0)
    N.invoke(m,'HuFullBox',x=0)
    return m


def native_contact(m,delta,foot_sample):
    box=bytes(m[0x658:0x65c]);before=box[3]
    if foot_sample:
        assert before<=253,'This directed fixture must not wrap the sampled footer.'
        m[0x65b]=before+2
    N.put(m,ObjectOffset=SLOT)
    count=0;Base=N.NesMPU
    class Probe(Base):
        def step(self):
            nonlocal count
            if self.pc==0xac29 and self.memory.rawtags[1]==199:count+=1
            return Base.step(self)
    with patch.object(N,'NesMPU',Probe):
        N.invoke(m,'LargePlatformCollision',a=0,x=SLOT,y=0)
        flag=N.get(m,'PlatformCollisionFlag',SLOT)
        field(m,'Enemy_Y_Position',N.get(m,'Enemy_Y_Position',SLOT)+delta)
        if flag<128 and not count:N.invoke(m,'PositionPlayerOnVPlat',a=0,x=SLOT,y=0)
    if foot_sample:
        assert m[0x65b]==before+2,'The native collision/positioning must not rewrite the sampled box.'
        m[0x65b]=before
        assert bytes(m[0x658:0x65c])==box,'Sampling must not leak into the native body rectangle.'
    return dict(passenger=flag,native_position_calls=count)


def source_step(m,pad=0):
    N.put(m,SavedJoypadBits=pad,SavedJoypad1Bits=pad)
    N.invoke(m,'HuMovement')
    N.invoke(m,'RelativePlayerPosition',x=0)
    N.invoke(m,'HuFullBox',x=0)


def trajectory(seed,sample,deltas):
    m=setup(seed)
    initial=view(m)
    first=native_contact(m,1,False)
    contact=view(m);steps=[]
    for i,delta in enumerate(deltas):
        source_step(m)
        after_source=view(m)
        if after_source['source']==5:break
        event=native_contact(m,delta,sample)
        steps.append(dict(step=i,after_source=after_source,contact=event,after_native=view(m)))
    return m,dict(platform_only_plus2_sample=sample,initial=initial,initial_contact=first,
        initial_after_native=contact,steps=steps,final=view(m))


def negatives(seed):
    rows=[]
    for gap in(3,4,8,16):
        m=setup(seed);native_contact(m,1,False);source_step(m)
        footer=m[0x65b]
        field(m,'Enemy_Y_Position',footer+gap)
        H.call(m,0xb624)
        event=native_contact(m,0,True)
        assert event==dict(passenger=255,native_position_calls=0),(SLOT,gap,event,view(m))
        rows.append(dict(kind='gap',gap=gap,rejected=True))
    m=setup(seed);native_contact(m,1,False);source_step(m)
    source_step(m,128)
    jumped=view(m);event=native_contact(m,0,True)
    assert jumped['source']==3 and N.get(m,'Player_Y_Speed')>=128,(SLOT,jumped,event)
    assert event==dict(passenger=255,native_position_calls=0),(SLOT,jumped,event,view(m))
    rows.append(dict(kind='original_fresh_jump',source_state=jumped['source'],rejected=True))

    m=setup(seed);native_contact(m,1,False)
    N.invoke(m,'EraseEnemyObject',x=SLOT);m[0x300:0x4a0]=bytes(416)
    for age in range(80):
        source_step(m)
        r=m.ram[2]
        if r[0x6b]==r[0x6c]==4 and r[0x210]-r[0x76]>=r[0x7b]+2:break
    else:raise AssertionError(('Original fall setup bound',SLOT,view(m)))
    distance=r[0x210]-r[0x76];limit=r[0x7b];top=m[0x65b]
    for name,value in dict(Enemy_ID=37,Enemy_Flag=1,Enemy_State=0,Enemy_X_Position=944&255,
        Enemy_PageLoc=944>>8,Enemy_Y_Position=top,Enemy_Y_HighPos=1,
        Enemy_BoundBoxCtrl=5,PlatformCollisionFlag=255).items():field(m,name,value)
    H.call(m,0xb624)
    event=native_contact(m,0,True)
    assert event['passenger']==SLOT and event['native_position_calls']==1,(SLOT,event,view(m))
    assert r[0x6b]==5,(SLOT,distance,limit,event,view(m))
    rows.append(dict(kind='genuine_high_fall',source_updates=age+1,original_distance=distance,
        original_limit=limit,original_injury_preserved=True))
    return rows


def main():
    global SLOT
    raw=(B.R/'build/metal-flower-native-1112/candidate.nes').read_bytes()
    assert sha256(raw).hexdigest()==P.PRINCE_PROPOSAL
    assert H.T.girder_images()[0]['symbols']['DkRefreshPlatform']==0xb624
    donor=Path('C:/NES/Donkey Kong Jr. (World) (Rev 1).nes').read_bytes()
    assert sha256(donor).hexdigest()=='1bc7fdc98c29b2c51438c3ce92ca37fac61b939a7cf100c644fed37206cf2cf6'
    prg=donor[16:16+16384*donor[4]];point=0xe947%len(prg)
    assert prg[point:point+9]==bytes.fromhex('186901853f69018541')
    _,seed=H.cold(raw,raw[B.COOKIE_AT:B.COOKIE_AT+16])
    rows=[];negative=[];paired=0;positive_steps=0
    code=bytes(seed.ram[2][0x900:0xd00])
    for SLOT in range(6):
        for deltas in ((1,)*8,(0,)*8,(2,)*8,(-1,)*8,(-2,)*8,(1,2,0,-1,-2,0,2,1)):
            for sample in(False,True):
                m,row=trajectory(seed,sample,deltas)
                assert row['initial']['playerBox']==[90,127,107,142]
                assert row['initial_contact']==dict(passenger=SLOT,native_position_calls=1)
                assert (row['initial_after_native']['nativeY'],row['initial_after_native']['sourceY'])==(106,121)
                if sample:
                    assert len(row['steps'])==8
                    for step in row['steps']:
                        v=step['after_native']
                        assert step['contact']==dict(passenger=SLOT,native_position_calls=1),(SLOT,deltas,step)
                        assert (v['source'],v['prior'],v['fallStart'],v['fallLimit'])==(1,1,0,22),(SLOT,deltas,step)
                        assert (v['nativeY'],v['sourceY'])==(v['top']-32,v['top']-17),(SLOT,deltas,step)
                        positive_steps+=1
                elif deltas==(1,)*8:
                    assert row['steps'][0]['contact']['passenger']==255
                    assert row['steps'][1]['after_source']['source']==4
                assert bytes(m.ram[2][0x900:0xd00])==code
                paired+=1
                rows.append(dict(slot=SLOT,deltas=deltas,sample=sample,
                    passengers=[s['contact']['passenger'] for s in row['steps']],
                    states=[s['after_native']['source'] for s in row['steps']],final=row['final']))
        negative.append(dict(slot=SLOT,cases=negatives(seed)))
    print('DKJR_CONTACT_COMPONENT '+json.dumps(dict(passed=True,ROM_SHA256=sha256(raw).hexdigest(),
        checker_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),
        original_support_probe=dict(CPU_half_open=[0xe947,0xe950],
            bytes_hex='186901853f69018541',source_footer_offsets=[1,2]),
        trajectory_branches=paired,positive_contact_updates=positive_steps,
        trajectories_SHA256=sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        negative=negative,ROM_written=False,outputs_written=0,
        scope='Declared component coordinates/terrain and actor-delta input, genuine current native/source procedures. Experimental bbox sampling is fixture-only; no Mesen, candidate patch or natural-route claim.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
