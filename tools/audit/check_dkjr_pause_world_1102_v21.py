"""Earned DK Jr fruit-hit ordering with actual native world-pause primitives.

Distinct proof consumes frozen v10/v16 read-only. Legal Mario0 service fixture;
there is no raw40/public owner/emulator claim or shared mutation.
"""
import collections,json,re
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import check_hogan_current_bounded_v1 as N
R=A.R;O=A.O;W=A.W;D=W.P.D


def main():
    b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes');b['raw']=A.BASE.read_bytes();assert A.sha(b['raw'])==A.PIN
    body=json.loads((O/'native-body-v10-layout.json').read_text());L=body['labels'];core=(O/'native-body-v10.bin').read_bytes();assert A.sha(core)==body['code_SHA256']
    helper=(O/'native-pause-v16.bin').read_bytes();H={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'native-pause-v16.lbl').read_text(),re.M)}
    q16=json.loads((O/'native-pause-v16-CPU.json').read_text());assert q16['passed'];block=q16['actual_timer_block'];timer_pc,timer_end=block['PC_half_open'];timer_bank=block['physical_PRG']|128
    donor,_=D.active();seed=bytes(donor.memory[:2048]);counts=collections.Counter();events=[]
    points={}
    for name in ['RunNormalEnemies','MoveNormalEnemy','ProcessCannons','BulletBillHandler','RunLargePlatform','ProcFirebar','ShellOrBlockDefeat','GuestPowerupUpdate']:
        points[W.address(b,name),((W.location(b,name)-16)//8192)|128]=name
    base=N.NesMPU;recent=collections.deque(maxlen=18)
    class Trace(base):
        def step(self):
            recent.append((self.pc,list(self.memory.rawtags),self.sp))
            if self.pc>=0x8000:
                name=points.get((self.pc,self.memory.rawtags[(self.pc-0x8000)//8192]))
                if name:counts[name]+=1
            return super().step()
    N.NesMPU=Trace
    def call(m,name):
        target=H.get(name,L.get(name));assert target
        c=Trace(memory=m,pc=target);c.a,c.x,c.y,c.p,c.sp=0x55,7,91,0xb1,224;c.stPushWord(0x5ffe)
        for _ in range(150000):
            if c.pc==0x5fff:break
            assert m[c.pc]!=0,('world pause BRK',name,hex(c.pc));c.step()
        else:raise AssertionError(('world pause bound',name))
        assert c.sp==224
        return c
    def put(m,name,value,i=0):m[W.address(b,name)+i]=value
    def get(m,name,i=0):return m[W.address(b,name)+i]
    def timers(m):
        maps=list(m.rawtags);m.raw_page((timer_pc-0x8000)//8192,timer_bank);c=Trace(memory=m,pc=timer_pc)
        for _ in range(1000):
            if c.pc==timer_end:break
            c.step()
        else:raise AssertionError('world actual timer bound')
        for i,tag in enumerate(maps):m.raw_page(i,tag)
    def fresh():
        m=N.Bus(b);m.ram[3][:len(core)]=core;m.ram[2][:2048]=seed;m.ram[2][0x1540:0x1540+len(helper)]=helper;m.raw_page(1,3);m.raw_page(2,2)
        N.put(m,CurrentBank=3,CurrentBankC=2,SelectedCharacter=0,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,TimerControl=0,AreaType=1,AreaPointer=0x25,WorldNumber=0,LevelNumber=0,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,Player_X_Position=48,Player_Y_Position=176,Player_Y_HighPos=1,ObjectOffset=0,VRAM_Buffer1_Offset=0)
        oracle=D.Bus();oracle[:2048]=seed;oracle[0:3]=bytes([40,191,0x18]);c=D.T.NesMPU(memory=oracle,pc=0);D.T.run(c,0xe9ee,0,0,0,0x20)
        r=bytearray(oracle[:2048])
        for at,v in [(0x6b,1),(0x6c,1),(0x6d,1),(0x54,4),(0x55,4),(0x4a,1),(0x4e,0),(0x68,0)]:r[at]=v
        m.ram[2][:2048]=r;call(m,'DkjrNativeWorldEnable');call(m,'DkjrNativeFruitReset')
        for name in ['Block_Buffer_1','Block_Buffer_2']:
            for row in [11,12]:m[W.address(b,name)+row*16:W.address(b,name)+row*16+16]=[0x54]*16
        for i,value in enumerate([60,0,191,0]):m[W.address(b,'R0')+i]=value
        c=Trace(memory=m,pc=L['DkjrNativeFruitSet']);c.x=0;c.sp=224;c.stPushWord(0x5ffe)
        for _ in range(10000):
            if c.pc==0x5fff:break
            c.step()
        else:raise AssertionError('actual fruit set bound')
        return m
    def enemy(m,i,ident,x,y,init):
        for name,v in [('Enemy_Flag',1),('Enemy_ID',ident),('Enemy_State',0),('Enemy_X_Position',x),('Enemy_PageLoc',0),('Enemy_Y_Position',y),('Enemy_Y_HighPos',1)]:put(m,name,v,i)
        N.put(m,ObjectOffset=i)
        if init:N.invoke(m,init,x=i)
        put(m,'Enemy_ID',ident,i)
    def world(m):
        N.put(m,CurrentOAMOffset=24,RgOamUsed=24,GuestOamRotationActive=0)
        for i in range(6):N.put(m,ObjectOffset=i);N.invoke(m,'EnemiesAndLoopsCore',x=i)
        N.invoke(m,'MiscObjectsCore');N.invoke(m,'ProcessCannons')
    try:
        m=fresh();enemy(m,0,6,60,184,'InitGoomba');enemy(m,5,6,180,184,'InitGoomba')
        # Earn capture through genuine Main, with no seeded sourceHit/clock.
        before=get(m,'Enemy_X_Position',5);before_ai=counts['MoveNormalEnemy'];timers(m);call(m,'DkPauseMain')
        assert m.ram[2][0x68]and not m.ram[2][0x440]and get(m,'TimerControl')==0
        assert counts['ShellOrBlockDefeat']==1
        world(m);assert counts['MoveNormalEnemy']>before_ai
        events.append(dict(epoch=1,kind='earned-capture-normal-native-world-pass',source_hit=m.ram[2][0x68],lease=m.ram[2][0x440],TimerControl=get(m,'TimerControl'),real_native_AI_calls=counts['MoveNormalEnemy']-before_ai))
        native_motion={name:bytes(m[W.address(b,name):W.address(b,name)+6])for name in ['Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos','Enemy_X_Speed','Enemy_Y_Speed']}
        player=(get(m,'Player_X_Position'),get(m,'Player_Y_Position'));clock=m.ram[2][0x38];hit_calls=0
        for epoch in range(2,62):
            timers(m);call(m,'DkPauseMain');hit_calls+=1
            assert get(m,'TimerControl')==255 and m.ram[2][0x440]
            world(m)
            assert native_motion=={name:bytes(m[W.address(b,name):W.address(b,name)+6])for name in native_motion},(epoch,'native enemy motion')
            assert player==(get(m,'Player_X_Position'),get(m,'Player_Y_Position'))
            if epoch<61:assert m.ram[2][0x68]and m.ram[2][0x38]==clock
        assert hit_calls==60 and not m.ram[2][0x68]and m.ram[2][0x38]==64
        events.append(dict(epoch=61,kind='sixtieth-D1AE-terminal-still-native-paused',lease=m.ram[2][0x440],TimerControl=get(m,'TimerControl'),source_clock=m.ram[2][0x38]))
        timers(m);call(m,'DkPauseMain');assert not m.ram[2][0x440]and get(m,'TimerControl')==0
        before_ai=counts['MoveNormalEnemy'];world(m);assert counts['MoveNormalEnemy']>before_ai
        events.append(dict(epoch=62,kind='normal-source-branch-thaws-before-native-world',lease=m.ram[2][0x440],TimerControl=get(m,'TimerControl'),source_clock=m.ram[2][0x38],real_native_AI_calls=counts['MoveNormalEnemy']-before_ai))
        # Actual native platform/firebar/hammer primitives keep their motion
        # held while rebuilding the genuine native draw data under this lease.
        controls=[];invalid_controls=[]
        cannon_id=W.address(b,'BulletBill_CannonVar');assert cannon_id==0x33
        for kind,ident,init in [('cannon',cannon_id,None),('platform',0x27,'InitHoriPlatform'),('firebar',0x1b,'InitShortFirebar')]:
            mm=fresh();enemy(mm,2,ident,160,128,init)
            if kind=='cannon':
                # ProcessCannons' actual birth contract, then its first live
                # handler builds genuine art before the owned hit pause.
                put(mm,'Enemy_BoundBoxCtrl',9,2);put(mm,'ObjectOffset',2)
                N.invoke(mm,'BulletBillHandler',x=2)
            mm.ram[2][0x68]=1;call(mm,'DkPauseMain')
            fields=['Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos','Enemy_X_Speed','Enemy_Y_Speed']
            if kind=='firebar':fields+=['FirebarSpinState_Low','FirebarSpinState_High']
            start={name:get(mm,name,2)for name in fields}
            if kind=='cannon':
                # Keep the original failed fixture visibly classified. Actual
                # native CannonVar is33; normal slot09 is not a legal cannon.
                for timer in [0,255]:
                    ref=N.fork(mm);put(ref,'Enemy_ID',9,2);N.put(ref,TimerControl=timer,ObjectOffset=2)
                    try:N.invoke(ref,'EnemiesAndLoopsCore',x=2)
                    except AssertionError as error:invalid_controls.append(dict(kind='INVALID_ID09_not_actual_CannonVar33',TimerControl=timer,error=str(error)))
            for _ in range(12):
                N.put(mm,CurrentOAMOffset=24,RgOamUsed=24,GuestOamRotationActive=0,ObjectOffset=2)
                try:N.invoke(mm,'EnemiesAndLoopsCore',x=2)
                except AssertionError as error:raise AssertionError((kind,str(error),list(recent)))from error
                if kind=='cannon':N.invoke(mm,'ProcessCannons')
                timers(mm);assert {name:get(mm,name,2)for name in fields}==start,(kind,start,{name:get(mm,name,2)for name in fields})
            assert get(mm,'Enemy_Flag',2)==1
            mm[512:768]=[248,0,0,0]*64;N.put(mm,CurrentOAMOffset=24,RgOamUsed=24,GuestOamRotationActive=0)
            N.invoke(mm,'DrawAllMetasprites')
            visible=sum(mm[512+i]<240 for i in range(0,256,4));assert visible>0,(kind,'genuine native DrawAll visible art')
            controls.append(dict(kind=kind,native_ID=ident,actual_native_updates=12,ingress='EnemiesAndLoopsCore+ProcessCannons'if kind=='cannon'else'EnemiesAndLoopsCore',mechanical_fields_exact=True,genuine_live_flag_retained=True,actual_DrawAll_visible_records=visible))
    finally:N.NesMPU=base
    out=dict(passed=True,proposal_only=True,ROM_written=False,native_owner_admitted=False,shared_hooks_added=False,complete_world_pause_qualified=False,invalid_fixture_negatives=invalid_controls,cannon_fixture_correction='Actual native BulletBill_CannonVar is33. Earlier v12/v16 explanatory ID09 cannon wording was incorrect. v16 hybrid helper has no live cannon-ID literal and is unchanged. This distinct v21 proves real33 through both native ingresses; no frozen packet was rewritten.',base_SHA256=A.PIN,source_capture_epoch=1,source_hit_terminal_epoch=61,next_normal_epoch=62,original_hit_updates=60,earned_capture=True,events=events,mechanical_controls=controls,actual_native_calls=dict(counts),
        order='Actual private Main earns fruit collision/native defeat with TimerControl0, then genuine native AI runs in capture epoch. Exactly60 following D1AE branches hold source/player/fruit/native enemy motion; terminal branch stays paused. Following normal source branch thaws before actual native AI resumes. Native GameLoop timers run before source phase, exactly as current host order.',
        remaining=['Actual nested Engine9 full powerup completion/reacquisition and scene/death public lifecycle; v16 direct cancellation alone is not that proof.','Native whole GameCore/public owner and IRQ/lagNMI integration, actual Mesen and1-1.','Source-owned complete fruit/hit/points OAM publication and helper/art cookie layout.'],
        scope='Actual current native timer/enemy/misc/cannon/platform/firebar primitives in explicitly legal Mario0 fixtures. Original actor/fruit hit is earned; no source hit/timer/upgrade was seeded in the ordered fixture. Isolated mechanical controls seed sourceHit only to test the native lease. No raw40 native entry, hardware or global all-stage claim.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in [Path(__file__),A.BASE,O/'native-body-v10.bin',O/'native-body-v10-layout.json',O/'native-pause-v16.bin',O/'native-pause-v16.lbl',O/'native-pause-v16-CPU.json']})
    (O/'native-pause-world-v21-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['passed','earned_capture','source_capture_epoch','source_hit_terminal_epoch','next_normal_epoch','mechanical_controls']}))


if __name__=='__main__':main()
