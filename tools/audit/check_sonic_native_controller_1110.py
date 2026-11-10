"""Actual native menu/1-1 controller consumer for the composed Sonic image.

Caller supplies its exact in-memory composition and aligned source packet.
After genuine Select/Start only controller peripheral and normal NMI change.
No ROM, game/terrain/actor writes, emulator or output files are produced.
"""
from collections import Counter,deque
from hashlib import sha256
import json

import check_ff_white_mushroom_current_1110 as W

N,UI=W.N,W.UI


def frontend_overlay(image,current):
    """Apply only the root-owned, exact-current menu delta after a disjoint check."""
    import check_sonic_gimmick_frontend_1110 as Frontend
    assert sha256(current).hexdigest()==Frontend.PIN
    menu,record=Frontend.proposal(current)
    indices=[i for i,(old,new)in enumerate(zip(current,menu))if old!=new]
    assert len(image)==len(current)==len(menu)
    overlap=[i for i in indices if image[i]!=current[i]]
    assert not overlap,('Frontend/Sonic source-preimage overlap',overlap)
    combined=bytearray(image)
    for i in indices:combined[i]=menu[i]
    return bytes(combined),dict(frontend=record,changed_bytes=len(indices),
        exact_Sonic_preimages=True,overlap_bytes=0,
        composed_SHA256=sha256(combined).hexdigest())


def run(image,p,*,goal_x=200,max_epochs=1200):
    b=W.Symbols.bundle();b['raw']=image
    old=N.Bus;N.Bus=W.ControllerBus
    try:m=UI.seed(b,25)
    finally:N.Bus=old
    for _ in range(3):UI.key(m,32)
    title=UI.menu_name(m)[0];assert title=='SONIC',title
    assert N.get(m,'SelectedCharacter')==43
    start=UI.key(m,16);assert N.get(m,'CrossoverMenuState')==0
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    idle=W.address(b,'IdleLoop');loop=W.address(b,'GameLoop')
    assert bytes(m[idle+9:idle+12])==b'\x20'+loop.to_bytes(2,'little')
    points={}
    for name in('KillPlayer','PlayerBGCollision','EnemyStomped','PlayerHeadCollision','FlagpoleCollision'):
        points[((W.location(b,name)-16)//8192|128,W.address(b,name))]=name
    for name in('SonicHostMain','SonicHostConstruct','SonicHostPowerup'):
        points[3,p['service']['symbols'][name]]=name
    for name in('MetaHead','MetaFeet','MetaBounds','MetaDraw','MetaDeath'):
        pc=p['metadata']['symbols'][name];points[2 if pc>=0xc000 else 3,pc]=name
    points[3,p['packet']['frame']['symbols']['SonicNativeOrdinaryFrame']]='OriginalSonicFrame'
    hits=Counter();tail=deque(maxlen=16);cold=None;active=0;last_jump=-100;minimum=255
    max_camera=0;old_camera=None
    def state(epoch):
        return dict(epoch=epoch,x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
            y=N.get(m,'Player_Y_Position'),y_high=N.get(m,'Player_Y_HighPos'),state=N.get(m,'Player_State'),
            engine=N.get(m,'GameEngineSubroutine'),mode=N.get(m,'OperMode'),task=N.get(m,'OperMode_Task'),
            lives=N.get(m,'NumberofLives'),status=N.get(m,'PlayerStatus'),timer=N.get(m,'TimerControl'),
            world=N.get(m,'WorldNumber'),level=N.get(m,'LevelNumber'),area=N.get(m,'AreaAddrsLOffset'),
            camera=N.get(m,'ScreenLeft_PageLoc')*256+N.get(m,'ScreenLeft_X_Pos'),
            source=list(m.ram[2][0x70:0x76]),velocity=list(m.ram[2][0x20:0x23])+list(m.ram[2][0x60:0x63]),
            flags=m.ram[2][0x30],height=m.ram[2][0x42],ready=m.ram[2][p['service']['fields']['Ready']-0xc000],
            frame_status=m.ram[2][0x116],point=list(m.ram[2][0x100:0x10b]),
            header2=bytes(m.ram[2][0x1fe0:0x1ff0]).hex(),header3=bytes(m.ram[3][0x1fe0:0x1ff0]).hex())
    def actors():
        return[dict(flag=N.get(m,'Enemy_Flag',i),kind=N.get(m,'Enemy_ID',i),state=N.get(m,'Enemy_State',i),
            x=N.get(m,'Enemy_X_Position',i)+256*N.get(m,'Enemy_PageLoc',i),y=N.get(m,'Enemy_Y_Position',i))for i in range(6)]
    try:
        for epoch in range(max_epochs):
            s=state(epoch);pad=0
            if(s['mode'],s['task'],s['engine'])==(1,3,8):
                assert N.get(m,'SelectedCharacter')==43
                assert N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
                assert s['lives']==2 and(s['world'],s['level'],s['area'])==(0,0,5)
                if cold is None:
                    cold=s;assert s['x']==40
                    print(json.dumps(dict(event='Sonic_active_native_1_1',state=s)),flush=True)
                if active>3:pad=1
                if s['state']==0 and active-last_jump>24:
                    near=any(a['flag']and a['kind']<21 and a['state']<2 and 0<=a['x']-s['x']<=56 for a in actors())
                    if near:last_jump=active
                if active-last_jump<20:pad|=128
                if old_camera is not None:max_camera=max(max_camera,s['camera']-old_camera)
                old_camera=s['camera'];active+=1
                if s['x']>=goal_x:
                    assert hits['OriginalSonicFrame']>=20 and hits['MetaFeet']and hits['MetaDraw']
                    assert s['ready']==1 and s['frame_status']==0
                    assert s['header2']==s['header3']==p['packet']['cookie'].hex()
                    return dict(passed=True,source_CPU_controller_only=True,Mesen_run=False,ROM_written=False,
                        ROM_SHA256=sha256(image).hexdigest(),menu=title,cold=cold,terminal=s,active_updates=active,
                        calls=dict(hits),minimum_SP=minimum,maximum_logical_camera_step=max_camera,
                        OAM_visible=sum(m[0x200+4*i]<240 for i in range(64)),
                        scope='Cold native menuarena, realSelect3/Start, actual nativeGameLoops/parsing/actor/renderer/camera. Afterconfirmationcontroller/NMIonly. Opening threshold only, no fullstage/powerup/physicalcadence claim.'),m
            m.controller_pad=pad;W.clear_logs(m);N.consume(m)
            c=N.NesMPU(memory=m,pc=idle);c.sp,c.p=255,0x31;c.stPushWord(0xe33b)
            for _ in range(500000):
                if(c.pc,c.sp)==(idle+12,252):break
                minimum=min(minimum,c.sp)
                if c.pc>=0x8000:
                    label=points.get((m.rawtags[(c.pc-0x8000)//8192],c.pc))
                    if label:
                        hits[label]+=1
                        assert label!='KillPlayer',('Sonic native opening injury/death',s,actors())
                assert m[c.pc],('Native Sonic controller BRK',epoch,hex(c.pc),m.rawtags)
                c.step()
            else:raise AssertionError(('Native Sonic GameLoop bound',epoch,hex(c.pc)))
            tail.append(dict(pad=pad,**state(epoch)))
            assert not m.blocked
        raise AssertionError(('Sonic native controller bound',state(max_epochs),dict(hits),list(tail)))
    except Exception:
        print(json.dumps(dict(passed=False,ROM_SHA256=sha256(image).hexdigest(),calls=dict(hits),tail=list(tail),terminal=state(epoch))),flush=True)
        raise
