"""Private DK Jr source-hit/native-pause lease; no shared hook or ROM write.

The original capture branch remains unpaused.  Only the following sixty
D1AE branches lease native TimerControl. Empty native slots are self-secondary
so native enemy/cannon births cannot bypass that pause. Live flags stay genuine.
"""
import collections,itertools,json,re
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import check_hogan_current_bounded_v1 as N
R=A.R;O=A.O;W=A.W


def main():
    raw=A.BASE.read_bytes();assert A.sha(raw)==A.PIN
    q=json.loads((O/'native-body-v10-layout.json').read_text());L=q['labels'];core=(O/'native-body-v10.bin').read_bytes();assert A.sha(core)==q['code_SHA256']
    b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes');b['raw']=raw
    names=['Enemy_Flag','Enemy_ID','ObjectMetasprite','TimerControl','GameEngineSubroutine','OperMode','OperMode_Task','AreaPointer','WorldNumber','LevelNumber']
    source='.setcpu "6502"\n.macpack longbranch\n.segment "DK_PAUSE"\n'+''.join(n+'=$%04x\n'%W.address(b,n)for n in names)
    source+='DkjrNativePhase=$%04x\nDkjrFruitHit=$%04x\n'%(L['DkjrNativePhase'],L['DkjrFruitHit'])
    source+='''
.export DkPauseMain,DkPauseBegin,DkPauseThaw,DkPauseEnd
Active=$c440
SavedTimer=$c441
SavedArea=$c442
SavedWorld=$c443
SavedLevel=$c444
Empty=$c445
SavedId=$c44b
SavedMeta=$c451
; Public owner authentication/mapping precedes this private Main. A newly
; earned hit is deliberately not paused in its normal/capture branch.
DkPauseMain:
 lda Active
 bne PauseWasActive
 lda $c068
 beq PauseNormal
 jsr DkPauseBegin
 bcc PauseReject
PauseWasActive:
 jsr PauseContext
 bcc PauseAbort
 lda TimerControl
 cmp #$fe
 bcc PauseAbort
 lda $c068
 beq PauseNormalThaw
 lda #$ff
 sta TimerControl
 jsr DkjrFruitHit
 sec
 rts
PauseNormalThaw:
 jsr DkPauseThaw
PauseNormal:
 jmp DkjrNativePhase
PauseAbort:
 jsr DkPauseThaw
PauseReject:
 clc
 rts
PauseContext:
 lda OperMode
 cmp #1
 bne PauseContextNo
 lda OperMode_Task
 cmp #3
 bne PauseContextNo
 lda GameEngineSubroutine
 cmp #8
 bne PauseContextNo
 lda AreaPointer
 cmp SavedArea
 bne PauseContextNo
 lda WorldNumber
 cmp SavedWorld
 bne PauseContextNo
 lda LevelNumber
 cmp SavedLevel
 bne PauseContextNo
 sec
 rts
PauseContextNo:
 clc
 rts
DkPauseBegin:
 lda TimerControl
 bne PauseContextNo
 lda OperMode
 cmp #1
 bne PauseContextNo
 lda OperMode_Task
 cmp #3
 bne PauseContextNo
 lda GameEngineSubroutine
 cmp #8
 bne PauseContextNo
 lda AreaPointer
 sta SavedArea
 lda WorldNumber
 sta SavedWorld
 lda LevelNumber
 sta SavedLevel
 lda TimerControl
 sta SavedTimer
 lda #1
 sta Active
 ldx #5
PauseSaveEmpty:
 lda #0
 sta Empty,x
 lda Enemy_Flag,x
 bne PauseNextEmpty
 lda Enemy_ID,x
 sta SavedId,x
 lda ObjectMetasprite+1,x
 sta SavedMeta,x
 lda #1
 sta Empty,x
 lda #0
 sta Enemy_ID,x
 sta ObjectMetasprite+1,x
 txa
 ora #$80
 sta Enemy_Flag,x
PauseNextEmpty:
 dex
 bpl PauseSaveEmpty
 lda #$ff
 sta TimerControl
 sec
 rts
; Exact native-field restoration once. A positive birth/changed ID invalidates
; an empty-slot token. Context changes or native Engine9 keep their own timer.
DkPauseThaw:
 php
 pha
 txa
 pha
 tya
 pha
 lda Active
 beq PauseThawDone
 lda #0
 sta Active
 jsr PauseContext
 bcc PauseLeaveTimer
 lda TimerControl
 cmp #$fe
 bcc PauseLeaveTimer
 lda SavedTimer
 sta TimerControl
PauseLeaveTimer:
 ldx #5
PauseRestoreEmpty:
 lda Empty,x
 beq PauseNextRestore
 lda #0
 sta Empty,x
 txa
 ora #$80
 cmp Enemy_Flag,x
 bne PauseNextRestore
 lda Enemy_ID,x
 bne PauseNextRestore
 lda #0
 sta Enemy_Flag,x
 lda SavedId,x
 sta Enemy_ID,x
 lda SavedMeta,x
 sta ObjectMetasprite+1,x
PauseNextRestore:
 dex
 bpl PauseRestoreEmpty
PauseThawDone:
 pla
 tay
 pla
 tax
 pla
 plp
 rts
DkPauseEnd:
'''
    helper,H=A.assemble('native-pause-v16',source,'MEMORY{P:start=$d540,size=$2c0,file=%O;}SEGMENTS{DK_PAUSE:load=P,type=ro;}')
    assert H['DkPauseEnd']<=0xd800
    donor,_=W.P.D.active();seed=bytes(donor.memory[:2048]);tests=collections.Counter();rows=[]
    def fresh():
        m=N.Bus(b);m.ram[3][:len(core)]=core;m.ram[2][:2048]=seed;m.ram[2][0x1540:0x1540+len(helper)]=helper;m.raw_page(1,3);m.raw_page(2,2)
        N.put(m,CurrentBank=3,CurrentBankC=2,SelectedCharacter=0,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,TimerControl=0,AreaType=1,AreaPointer=0x25,WorldNumber=0,LevelNumber=0,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,Player_X_Position=32,Player_Y_Position=176,Player_Y_HighPos=1,ObjectOffset=0)
        return m
    def call(m,name):
        c=N.NesMPU(memory=m,pc=H[name]);c.a,c.x,c.y,c.p,c.sp=0x55,7,91,0xb1,224;c.stPushWord(0x5ffe)
        for _ in range(150000):
            if c.pc==0x5fff:break
            assert m[c.pc]!=0,('pause BRK',name,hex(c.pc));c.step()
        else:raise AssertionError(('pause bound',name,hex(c.pc)))
        assert c.sp==224
        if name=='DkPauseThaw':assert(c.a,c.x,c.y,c.p)==(0x55,7,91,0xb1)
        return c
    def put(m,n,v,i=0):m[W.address(b,n)+i]=v
    def field(m,n):return bytes(m[W.address(b,n):W.address(b,n)+6])
    # Bind the actual current GameLoop timer block, including its FrameCounter
    # increment. The fixture executes those bytes, not a Python timer model.
    at=W.location(b,'GameLoop');window=W.address(b,'GameLoop');data=raw[at:at+1024]
    signature=bytes.fromhex('ad4a07f0');off=data.index(signature);assert data.count(signature)==1
    frame=W.address(b,'FrameCounter');increment=bytes([0xe6,frame])if frame<256 else bytes([0xee,frame&255,frame>>8])
    end=data.index(increment,off)+len(increment)
    timer_pc=window+off;timer_end=window+end;timer_bank=((at-16)//8192)|128
    def timers(m):
        maps=list(m.rawtags);win=(timer_pc-0x8000)//8192;m.raw_page(win,timer_bank)
        c=N.NesMPU(memory=m,pc=timer_pc)
        for _ in range(1000):
            if c.pc==timer_end:break
            c.step()
        else:raise AssertionError('actual timer bound')
        for i,tag in enumerate(maps):m.raw_page(i,tag)
    def enemies(m):
        for i in range(6):N.put(m,ObjectOffset=i);N.invoke(m,'EnemiesAndLoopsCore',x=i)
        N.invoke(m,'ProcessCannons')
    def setup_enemy(m,slot,ident=6):
        for n,v in [('Enemy_Flag',1),('Enemy_ID',ident),('Enemy_State',0),('Enemy_Y_HighPos',1),('Enemy_X_Position',96),('Enemy_PageLoc',0),('Enemy_Y_Position',184)]:put(m,n,v,slot)
        N.put(m,ObjectOffset=slot);N.invoke(m,'InitGoomba',x=slot)
        put(m,'Enemy_ID',ident,slot)
    motion=['Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos','Enemy_X_Speed','Enemy_Y_Speed']
    for slot in range(6):
        m=fresh();setup_enemy(m,slot)
        # Deliberately stale cannon IDs/metas in empty slots. Real loader births
        # would otherwise execute even while TimerControl is set.
        for i in range(6):
            if i!=slot:put(m,'Enemy_ID',9,i);put(m,'ObjectMetasprite',30+i,i+1)
        before_flags=field(m,'Enemy_Flag');before_ids=field(m,'Enemy_ID');before_meta=bytes(m[W.address(b,'ObjectMetasprite')+1:W.address(b,'ObjectMetasprite')+7])
        for i in range(6):put(m,'Cannon_PageLoc',1,i);put(m,'Cannon_Timer',3+i,i)
        cannon=field(m,'Cannon_Timer');N.put(m,EnemyFrenzyQueue=6,AreaParserTaskNum=0)
        m.ram[2][0x68]=1;m.ram[2][0x69]=0;m.ram[2][0x66]=0;m.ram[2][0x38]=0x23
        start={n:field(m,n)for n in motion};clock=m.ram[2][0x38]
        # First actual source hit branch acquires the lease. Following top-of-
        # GameLoop timer blocks must preserve all ordinary native timers.
        for epoch in range(1,61):
            call(m,'DkPauseMain');assert N.get(m,'TimerControl')==255
            if epoch<60:assert m.ram[2][0x68]and m.ram[2][0x38]==clock
            else:assert not m.ram[2][0x68]and m.ram[2][0x38]==0x40
            enemies(m);assert {n:field(m,n)for n in motion}==start,(slot,epoch,'motion')
            assert field(m,'Cannon_Timer')==cannon and N.get(m,'EnemyFrenzyQueue')==6
            assert m[W.address(b,'Enemy_Flag')+slot]==1
            tick_start=bytes(m[W.address(b,'Timers'):W.address(b,'DemoTimer')+1]);timers(m)
            assert bytes(m[W.address(b,'Timers'):W.address(b,'DemoTimer')+1])==tick_start
            tests['actual_sixty_D1AE_enemy_cannon_spawn_timer_paused_epochs']+=1
        assert m.ram[2][0x440]==1
        call(m,'DkPauseThaw');assert N.get(m,'TimerControl')==0
        assert field(m,'Enemy_Flag')==before_flags and field(m,'Enemy_ID')==before_ids
        assert all(m[W.address(b,'ObjectMetasprite')+1+i]==before_meta[i]for i in range(6)if i!=slot)
        old=len(m.writes);call(m,'DkPauseThaw');assert not any(at==W.address(b,'TimerControl')or W.address(b,'Enemy_Flag')<=at<W.address(b,'Enemy_Flag')+6 for at,_ in m.writes[old:])
        rows.append(dict(slot=slot,source_hit_branches=60,source_clock_terminal=64,native_cannon_timers=list(cannon),all_native_live_flags_retained=True,exact_empty_fields_restore_once=True))
        tests['real_native_empty_births_and_cannon_countdowns_suppressed_without_page_writes']+=1
    # Native nonzero pause is never claimed; its timer and all native fields
    # remain intact. Engine9/scene changes cancel our lease without resetting
    # the native transition's timer, including the same-valued FF impulse.
    for timer in [1,2,127,254,255]:
        m=fresh();N.put(m,TimerControl=timer);m.ram[2][0x68]=1;before=bytes(m[:256])+bytes(m[0x200:0x800]);z=call(m,'DkPauseMain')
        assert not z.p&1 and before==bytes(m[:256])+bytes(m[0x200:0x800])and not m.ram[2][0x440];tests['preexisting_native_pause_not_claimed']+=1
    for change in [{'GameEngineSubroutine':9,'TimerControl':255},{'GameEngineSubroutine':11,'TimerControl':255},{'AreaPointer':0x26,'TimerControl':255},{'OperMode':0,'TimerControl':0},{'LevelNumber':1,'TimerControl':5}]:
        m=fresh();m.ram[2][0x68]=1;call(m,'DkPauseMain');N.put(m,**change);before=N.get(m,'TimerControl');call(m,'DkPauseMain')
        assert not m.ram[2][0x440]and N.get(m,'TimerControl')==before;tests['nested_engine_scene_lease_cancel_preserves_native_timer']+=1
    # A genuine same-ID positive native birth invalidates its empty receipt.
    for slot in range(6):
        m=fresh();m.ram[2][0x68]=1;call(m,'DkPauseMain');N.put(m,EnemyFrenzyQueue=6,ObjectOffset=slot,WorldNumber=0,LevelNumber=0)
        N.invoke(m,'ChkEnemyFrenzy',x=slot);assert m[W.address(b,'Enemy_Flag')+slot]==1
        snapshot={n:m[W.address(b,n)+slot]for n in ['Enemy_Flag','Enemy_ID']+motion};call(m,'DkPauseThaw')
        assert snapshot=={n:m[W.address(b,n)+slot]for n in snapshot};tests['actual_same_ID_positive_birth_not_overwritten']+=1
    out=dict(passed=True,proposal_only=True,ROM_written=False,native_owner_admitted=False,shared_hooks_added=False,base_SHA256=A.PIN,component_bytes=len(helper),helper_span=[0xd540,H['DkPauseEnd']],private_state_span=[0xc440,0xc457],checks=dict(tests),source_hit_native_pause_cases=rows,
        actual_timer_block=dict(physical_PRG=timer_bank&127,PC_half_open=[timer_pc,timer_end],SHA256=A.sha(data[off:end])),
        source_order='Normal capture returns through original fruit advance/clock path with TimerControl0. The next Main with sourceHit!=0 starts native pause and executes D1AE. Exactly60hit branches hold the lease, including the terminal branch; thaw precedes the next normal source branch. Earned capture plus full GameCore-order fixture is a remaining proof below.',
        host_effect_adaptation='Native FrameCounter and jump-coin/firebar visual frame animations retain authentic native powerup-pause behavior. This is not a donor ability or timer change.',
        remaining=['Earned first-hit/capture-to-next-D1AE actual native world ordering and platform/firebar/hammer rendered art controls.','Wire authenticated full Main and public lifecycle/pickup/contact/retirement ingresses; nested Engine9 proof here is direct actual state ingress, not full powerup pipeline.','All public/IRQ/source reader closure and final resource/menu grant remain pending.'],
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),A.BASE,O/'native-body-v10.bin',O/'native-body-v10-layout.json',O/'native-pause-v16.s',O/'native-pause-v16.bin']})
    (O/'native-pause-v16-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['passed','component_bytes','helper_span','private_state_span','checks']}))


if __name__=='__main__':main()
