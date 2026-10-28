"""Bounded actual linked RCR leaf contracts; CPU arenas, not native gameplay."""
from pathlib import Path
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from prepare_river_city_reference import NATIVE,native_motion

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def fresh(bundle,variant=0,mode=1):
    q=Arena(bundle,21)
    q.put(RcVariant=variant,CrossoverBehaviorVersion=mode,NumberofLives=3,
          AreaPointer=0,WorldNumber=0,Player_State=0,Player_Y_Position=176,
          Player_Y_HighPos=1,Player_X_Position=96,Player_PageLoc=1,
          GamePauseStatus=0,TimerControl=0,NmiDisable=255,Sprite0HitDetectFlag=1)
    q.invoke('RcGlobalInit');return q

def pad(q,bits):
    q.put(SavedJoypadBits=bits,A_B_Buttons=bits&192,Left_Right_Buttons=bits&3)
    return q.invoke('RcMovement')[0]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    bundle=scoped_load(a.rom);rows=[];interrupts=[]
    for variant in [0,1]:
        for mode in [0,1]:
            q=fresh(bundle,variant,mode)
            assert [q.get('RcHealth',i)for i in[0,1]]==[48,48]
            for facing,bits,sign in [(1,1,1),(2,2,-1)]:
                q=fresh(bundle,variant,mode);start=q.get('Player_X_Position')+256*q.get('Player_PageLoc')
                for _ in range(8):pad(q,bits)
                end=q.get('Player_X_Position')+256*q.get('Player_PageLoc');assert end-start==12*sign,(facing,end-start)
                pad(q,0);pad(q,bits);assert q.get('RcRun')==1
                begin=q.get('Player_X_Position')+256*q.get('Player_PageLoc')
                for _ in range(8):pad(q,bits)
                end=q.get('Player_X_Position')+256*q.get('Player_PageLoc');assert end-begin==28*sign
                rows.append(dict(check='source-walk-run',variant=variant,mode=mode,facing=facing,walk_displacement=12*sign,run_displacement=28*sign))
            q=fresh(bundle,variant,mode);pad(q,128);ys=[q.get('Player_Y_Position')]
            assert q.get('Player_State')==1 and q.get('MmVY',2)>=128
            for _ in range(55):pad(q,128);ys.append(q.get('Player_Y_Position'))
            assert min(ys)<=100 and min(ys)>=16
            rows.append(dict(check='SMB-adapted-jump',variant=variant,mode=mode,minimum_Y=min(ys),starting_Y=176,updates=56))
            q=fresh(bundle,variant,mode);pad(q,128);q.put(Player_Y_Speed=0);pad(q,128)
            assert q.get('MmVY',2)==0,'real ceiling response is honored'
            q=fresh(bundle,variant,mode);pad(q,4);assert q.get('RgCrouch')==1
            q.invoke('RcCollisionBox');assert q.get('PlayerSize')==0
            # Native type/state remains intact during private melee stun.
            q=fresh(bundle,variant,mode)
            q.set('Enemy_Flag',1);q.set('Enemy_ID',address(bundle,'Goomba'));q.set('Enemy_State',0)
            q.set('Enemy_Y_HighPos',1);q.set('Enemy_Y_Position',184);q.set('Enemy_PageLoc',1);q.set('Enemy_X_Position',112)
            q.set('Enemy_X_Speed',240)
            pad(q,64);q.invoke('RcWeapons')
            for _ in range(5):pad(q,0);q.invoke('RcWeapons')
            assert q.get('RcEnemyHP')==2 and q.get('RcEnemyStun')>0
            assert q.get('Enemy_State')==0 and q.get('Enemy_Flag')==1
            # A real Up+B edge acquires only the already-stunned typed actor.
            for _ in range(10):pad(q,0);q.invoke('RcWeapons')
            pad(q,72);q.invoke('RcWeapons');assert q.get('RcCarrySlot')==0
            c,_=q.invoke('RcEnemyControl',x=0);assert c.p&1 and q.get('Enemy_Y_Position')==160
            q.invoke('RcReleaseCarry');assert q.get('Enemy_X_Speed')==240 and q.get('RcCarrySlot')==255
            rows.append(dict(check='punch-stun-grab-release',variant=variant,mode=mode,private_stun=True,native_state_unchanged=True))
            q=fresh(bundle,variant,mode);q.set('RcHealth',8,variant);q.set('RcTier',0,variant)
            q.invoke('RcHeal',a=0);assert q.get('RcHealth',variant)==32
            for _ in range(5):q.invoke('RcHeal',a=1)
            assert q.get('RcHealth',variant)==64 and q.get('RcTier',variant)==2
            before=list(q.m[0x5fa0:0x5fb0]);c,_=q.invoke('RcHeal',a=2);assert not c.p&1 and before==list(q.m[0x5fa0:0x5fb0])
            q.put(NumberofLives=4);q.invoke('RcEnsure');assert q.get('RcTier',variant)==2
            q.put(NumberofLives=3);q.invoke('RcEnsure');assert q.get('RcTier',variant)==0 and q.get('RcHealth',variant)==48
            rows.append(dict(check='earned-life-preserves-death-resets',variant=variant,mode=mode))
            # The genuine code addresses and bank mapping, no fake aliases.
            for facing in [1,2]:
                q=fresh(bundle,variant,mode);q.put(PlayerFacingDir=facing)
                for pose in range(18):
                    q.invoke('RcSetPose',x=pose);q.invoke('RcPublish')
                    ptr=q.get('SmPosePtr')+256*q.get('SmPosePtr',1)
                    assert q.m.banks[2]==70 and 0xcb80<=ptr<0xdb80
                    assert [q.get('CurrentCHRBank',i)for i in range(4)]==[(716+4*variant+i)&255 for i in range(4)]
                    length=q.m[ptr];assert 0<length<=48 and length%4==0
                    for offset in [0,128,224,244,252]:
                        q.put(CurrentOAMOffset=offset,R0=ptr&255,R1=ptr>>8,R3=0,R4=120,R5=0,R6=176,R7=1,GuestOamRotationActive=0)
                        c,trace=q.invoke('MetaspriteRenderLoop')
                        if offset+length>=256:assert not c.p&1
                        else:assert c.p&1 and q.get('CurrentOAMOffset')==offset+length
                    rows.append(dict(check='linked-body-record-render',variant=variant,mode=mode,facing=facing,pose=pose,bytes=length))
    # Foreign actor movement must return C0 without application writes.
    for character in range(21):
        q=fresh(bundle);q.put(SelectedCharacter=character)
        before=list(q.m[:0x100])+list(q.m[0x200:0x8000]);c,_=q.invoke('RcEnemyControl',x=0)
        after=list(q.m[:0x100])+list(q.m[0x200:0x8000]);assert before==after and not c.p&1
        rows.append(dict(check='foreign-actor-movement',character=character))
    # Actual RTI paths interrupt a new leaf while its private A bank is live.
    for variant in [0,1]:
        for which in ['NMI','IRQ']:
            for delta in [0,3,8]:
                q=fresh(bundle,variant);saved=NesMPU.step;fired=[False];target=address(bundle,'RcPublish')+delta
                def step(c):
                    if not fired[0] and c.pc==target and q.m.banks[1]==81:
                        fired[0]=True;before=(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,list(q.m.banks),q.get('CurrentBank'),q.get('CurrentBankC'))
                        if which=='NMI':c.nmi()
                        else:c.stPushWord(c.pc);c.stPush(c.p&~c.BREAK|c.UNUSED);c.p|=c.INTERRUPT;c.pc=address(bundle,'IrqScrollSplit')
                        for _ in range(20000):
                            saved(c)
                            if c.pc==before[5]and c.sp==before[4]:break
                        else:raise AssertionError('interrupt RTI timeout')
                        after=(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc,list(q.m.banks),q.get('CurrentBank'),q.get('CurrentBankC'));assert before==after,(which,before,after)
                    saved(c)
                NesMPU.step=step
                try:q.invoke('RcPublish')
                finally:NesMPU.step=saved
                assert fired[0];interrupts.append(dict(variant=variant,kind=which,PC=target))
    proof=dict(passed=True,native_run=False,scope=__doc__,ROM_sha256=sha(a.rom),rows=rows,interrupts=interrupts,
               original_native_motion=native_motion(NATIVE.read_bytes()),
               limitations=['Typed CPU arenas, not natural acquisition or full GameLoop integration.','No PPU/NMI deadline/cadence claim.','Current frozen asset has a diagnosed palette-class interpretation error; colors not qualified.'],
               bindings=[dict(path=str(p),sha256=sha(p))for p in [Path(__file__),a.rom,a.rom.with_suffix('.dbg'),ROOT/'src/river_city_core.s',ROOT/'src/river_city_combat.s',ROOT/'src/river_city_render.s',ROOT/'chr/characters/river-city.chr']])
    a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,rows=len(rows),interrupts=len(interrupts),output=str(a.output))))
if __name__=='__main__':main()
