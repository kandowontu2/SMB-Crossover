"""Whole native Main earns DK fruit defeat, original60hit updates and thaw."""
import collections,json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import check_hogan_current_bounded_v1 as N
R=A.R;O=A.O;W=A.W


def main():
    path=R/'tools/audit/check_dkjr_native_lifecycle_1102_v31.py'
    source=path.read_text().replace('native-lifecycle-v30','native-effects-v39').replace('native-lifecycle-','native-effects-').replace('-v30.bin','-v39.bin')
    env={'__name__':'dk_earned_main_fixture','__file__':str(path)};exec(compile(source,str(path),'exec'),env)
    b,m,L,q=env['fixture']();N.put(m,Player_X_Position=48);env['direct'](m,L['DkConstruct'])
    N.put(m,CurrentPlayer=0,AreaParserTaskNum=7,GameTimerCtrlTimer=24,GameTimerExpiredFlag=0,DisableIntermediate=1,PlayerSize=1,Player_BoundBoxCtrl=1,PlayerFacingDir=1)
    for name in ['Block_Buffer_1','Block_Buffer_2']:
        for row in [11,12]:m[W.address(b,name)+row*16:W.address(b,name)+row*16+16]=[0x54]*16
    for i,v in enumerate([4,0,0]):m[W.address(b,'GameTimerDisplay')+i]=v
    for i,value in enumerate([60,0,191,0]):m[W.address(b,'R0')+i]=value
    c=N.NesMPU(memory=m,pc=L['DkjrNativeFruitSet']);c.sp=224;c.x=0;c.stPushWord(0x5ffe)
    for _ in range(10000):
        if c.pc==0x5fff:break
        c.step()
    else:raise AssertionError('native worldfruit set bound')
    for slot,x in [(0,60),(5,180)]:
        for name,value in [('Enemy_Flag',1),('Enemy_ID',6),('Enemy_State',0),('Enemy_X_Position',x),('Enemy_PageLoc',0),('Enemy_Y_Position',184),('Enemy_Y_HighPos',1)]:m[W.address(b,name)+slot]=value
        N.put(m,ObjectOffset=slot);N.invoke(m,'InitGoomba',x=slot)
    timer=json.loads((O/'native-pause-v16-CPU.json').read_text())['actual_timer_block'];lo,hi=timer['PC_half_open'];tag=timer['physical_PRG']|128
    counts=collections.Counter();old=N.NesMPU;points={};epochs=[];recent=collections.deque(maxlen=18);minimum=255;overlap=None
    for name in ['GameCoreRoutine','MoveNormalEnemy','ShellOrBlockDefeat','ProcessCannons','DrawAllMetasprites']:
        points[W.address(b,name),((W.location(b,name)-16)//8192)|128]=name
    for name in ['DkNativeMain','DkjrFruitHit','DkNativeDraw','DkNativeEffects']:
        points[L[name],2 if L[name]>=0xc000 else 3]=name
    class Trace(old):
        def step(self):
            nonlocal minimum,overlap
            minimum=min(minimum,self.sp);recent.append([self.pc,self.sp,self.a,list(self.memory.rawtags)])
            if overlap is None and self.sp<=0x7b:overlap=[self.pc,self.sp,self.a,list(self.memory.rawtags)]
            if self.pc>=0x8000:
                name=points.get((self.pc,self.memory.rawtags[(self.pc-0x8000)//8192]))
                if name:counts[name]+=1
            return super().step()
    N.NesMPU=Trace
    def timers():
        maps=list(m.rawtags);m.raw_page((lo-0x8000)//8192,tag);c=Trace(memory=m,pc=lo)
        for _ in range(1000):
            if c.pc==hi:break
            c.step()
        else:raise AssertionError('native real timer bound')
        for i,t in enumerate(maps):m.raw_page(i,t)
    try:
        capture=terminal=thaw=None;motion=None;start_clock=None
        for epoch in range(1,63):
            N.put(m,FrameCounter=epoch,SavedJoypadBits=0,SavedJoypad1Bits=0,VRAM_Buffer1_Offset=0)
            timers();before=counts['MoveNormalEnemy']
            try:N.invoke(m,'GameCoreRoutine',a=85,x=0,y=0,p=0x31)
            except AssertionError as error:
                negative=dict(passed=False,ROM_written=False,native_owner_admitted=False,epoch=epoch,error=str(error),minimum_CPU_SP=minimum,first_SMC_stack_overlap_PC_SP_A_maps=overlap,recent_PC_SP_A_maps=list(recent),actual_calls=dict(counts),private_body_SHA256=A.sha((O/'native-effects-v39.bin').read_bytes()))
                (O/'native-earned-Main-v41-negative.json').write_text(json.dumps(negative,indent=2)+'\n')
                raise
            r=m.ram[2];now={name:bytes(m[W.address(b,name):W.address(b,name)+6])for name in ['Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos','Enemy_X_Speed','Enemy_Y_Speed']}
            if capture is None and r[0x68]:
                capture=epoch;assert epoch==1 and not r[0x440]and N.get(m,'TimerControl')==0 and counts['ShellOrBlockDefeat']==1 and counts['MoveNormalEnemy']>before
                motion=now;start_clock=r[0x38]
            elif 2<=epoch<=61:
                assert r[0x440]and N.get(m,'TimerControl')==255 and now==motion,(epoch,'full actual Main mechanical motion')
                assert (N.get(m,'Player_X_Position'),N.get(m,'Player_Y_Position'))==(48,176)
                if epoch<61:assert r[0x68]and r[0x38]==start_clock
                else:assert not r[0x68]and r[0x38]==64;terminal=epoch
            else:
                assert epoch==62 and not r[0x440]and N.get(m,'TimerControl')==0 and counts['MoveNormalEnemy']>before;thaw=epoch
            assert N.get(m,'NumberofLives')==2 and N.get(m,'GameEngineSubroutine')==8
            assert N.get(m,'CurrentOAMOffset')%4==0
            assert N.get(m,'ObjectMetasprite')==0 and N.get(m,'SmPosePtr')+256*N.get(m,'SmPosePtr',1)==W.address(b,'ObjectMetasprite')
            if epoch in [1,2,60,61,62]:epochs.append(dict(epoch=epoch,hit=r[0x68],lease=r[0x440],TimerControl=N.get(m,'TimerControl'),clock=r[0x38],source_hit_entries=counts['DkjrFruitHit'],actual_native_AI_entries=counts['MoveNormalEnemy']-before))
        assert(capture,terminal,thaw)==(1,61,62)and counts['DkjrFruitHit']==60 and counts['ShellOrBlockDefeat']==1
        at=W.address(b,'Player1ScoreDisplay');score=sum(m[at+i]*10**(6-i)for i in range(6));assert score==1200 and m.ram[2][0x430]==0
    finally:N.NesMPU=old
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,historical_v65_matching_header_fixture=True,
        earned_capture_epoch=capture,original_hit_terminal_epoch=terminal,next_normal_thaw_epoch=thaw,original_hit_updates=60,physical_native_defeats=1,source_native_score_400plus800=score,lives_before=2,lives_after=2,epoch_boundaries=epochs,actual_calls=dict(counts),
        scope='Complete actual GameCore62epochs plus real native timer ingress and DrawAll. Fruit/nativeGoomba initial positions are explicit legal fixtures; hit/defeat/pause/score are earned. Source hit/timers/powerups are never seeded. No real-level fruit placement/parser/emulator or latest-current cold authentication claim.',
        remaining=['All17 unfinished typed rows and raw40 fullbox/contact/pickup/bounce native gates; exact final latest-owner rebind and headers/cookie/cold lifecycle.','Actual Mesen basics and native helper-assisted1-1 remain root-owned.'],
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),path,O/'native-effects-v39-layout.json',O/'native-effects-v39.bin',O/'native-effects-v40-CPU.json',O/'native-pause-v16-CPU.json']})
    (O/'native-earned-Main-v41-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['passed','earned_capture_epoch','original_hit_terminal_epoch','next_normal_thaw_epoch','source_native_score_400plus800','actual_calls']}))


if __name__=='__main__':main()
