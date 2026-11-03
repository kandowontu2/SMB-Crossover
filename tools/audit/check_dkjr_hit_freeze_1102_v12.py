"""Private six-slot DK Jr hit pause using real native secondary-flag paths.

No shared AI/birth hook and no ROM is written.  These are explicitly isolated
native service fixtures, not a raw40 public/Main or hardware qualification.
"""
import collections,itertools,json,sys
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import check_hogan_current_bounded_v1 as N
R=A.R;O=A.O;W=A.W


def main():
    raw=A.BASE.read_bytes();assert A.sha(raw)==A.PIN
    q=json.loads((O/'native-body-v10-layout.json').read_text());L=q['labels'];core=(O/'native-body-v10.bin').read_bytes();assert A.sha(core)==q['code_SHA256']
    b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes');b['raw']=raw
    names=['Enemy_Flag','Enemy_ID','ObjectMetasprite']
    source='.setcpu "6502"\n.segment "DK_FREEZE"\n'
    source+='\n'.join(n+'=$%04x'%W.address(b,n)for n in names)+'\n'
    source+='DkjrNativePhase=$%04x\n'%L['DkjrNativePhase']
    source+='''
.export DkHitFreeze,DkHitThaw,DkPrivateMain,DkFreezeEnd
Ready=$c440
SavedFlag=$c446
SavedId=$c44c
SavedMeta=$c452
; Private wrapper for the already qualified source phase. Retirement calls
; DkHitThaw unconditionally before invalidating this owner's headers.
DkPrivateMain:
 lda $c068
 bne :+
 jsr DkHitThaw
:
 jsr DkjrNativePhase
 php
 jsr DkHitFreeze
 plp
 rts
DkHitFreeze:
 php
 pha
 txa
 pha
 tya
 pha
 lda $c068
 beq FreezeDone
 ldx #5
FreezeSlot:
 lda Ready,x
 beq SaveNew
 txa
 ora #$80
 cmp Enemy_Flag,x
 bne SaveNew
 jsr ShadowId
 cmp Enemy_ID,x
 beq NextFreeze
SaveNew:
 lda Enemy_Flag,x
 sta SavedFlag,x
 lda Enemy_ID,x
 sta SavedId,x
 lda ObjectMetasprite+1,x
 sta SavedMeta,x
 lda #1
 sta Ready,x
 jsr ShadowId
 sta Enemy_ID,x
 lda SavedFlag,x
 bne :+
 lda #0
 sta ObjectMetasprite+1,x
:
 txa
 ora #$80
 sta Enemy_Flag,x
NextFreeze:
 dex
 bpl FreezeSlot
FreezeDone:
 pla
 tay
 pla
 tax
 pla
 plp
 rts
; Empty slots and cannon-bill ID09 use harmless ID00 while suspended. This
; is needed because ProcessCannons independently runs ID09 even if its flag
; is secondary. Ordinary/live firebar IDs remain intact for genuine drawing.
ShadowId:
 lda SavedFlag,x
 beq ShadowZero
 lda SavedId,x
 cmp #9
 bne ShadowReturn
ShadowZero:
 lda #0
ShadowReturn:
 rts
DkHitThaw:
 php
 pha
 txa
 pha
 tya
 pha
 ldx #5
ThawSlot:
 lda Ready,x
 beq NextThaw
 lda #0
 sta Ready,x
 txa
 ora #$80
 cmp Enemy_Flag,x
 bne NextThaw
 jsr ShadowId
 cmp Enemy_ID,x
 bne NextThaw
 lda SavedId,x
 sta Enemy_ID,x
 lda SavedFlag,x
 sta Enemy_Flag,x
 bne NextThaw
 lda SavedMeta,x
 sta ObjectMetasprite+1,x
NextThaw:
 dex
 bpl ThawSlot
 jmp FreezeDone
DkFreezeEnd:
'''
    helper,H=A.assemble('hit-freeze-v12',source,'MEMORY{P:start=$d540,size=$2c0,file=%O;}SEGMENTS{DK_FREEZE:load=P,type=ro;}')
    assert H['DkFreezeEnd']<=0xd800
    points={}
    for name in ['EnemiesAndLoopsCore','RunEnemyObjectsCore','ProcLoopCommand','ProcessCannons','BulletBillHandler','EnemyGraphicsEngine','DrawAllMetasprites','DrawMetasprite','ShellOrBlockDefeat']:
        points[(W.address(b,name),((W.location(b,name)-16)//8192)|128)]=name
    counts=collections.Counter();native=N.NesMPU
    class Trace(native):
        def step(self):
            if self.pc>=0x8000:
                name=points.get((self.pc,self.memory.rawtags[(self.pc-0x8000)//8192]))
                if name:counts[name]+=1
            return super().step()
    N.NesMPU=Trace
    def call(m,name):
        # The public owner frame is not implemented here. Explicitly supply
        # its documented authenticated C2 mapping for this private leaf.
        m.raw_page(2,2);N.put(m,CurrentBankC=2)
        c=Trace(memory=m,pc=H[name]);c.a,c.x,c.y,c.p,c.sp=0x55,7,91,0xb1,224;c.stPushWord(0x5ffe)
        for _ in range(150000):
            if c.pc==0x5fff:break
            assert m[c.pc]!=0,('freeze BRK',name,hex(c.pc));c.step()
        else:raise AssertionError(('freeze call bound',name))
        assert (c.a,c.x,c.y,c.p,c.sp)==(0x55,7,91,0xb1,224),(name,c.a,c.x,c.y,c.p,c.sp)
        return c.processorCycles
    def fresh():
        m=N.Bus(b);m.ram[3][:len(core)]=core;m.ram[2][0x1540:0x1540+len(helper)]=helper;m.raw_page(1,3);m.raw_page(2,2)
        N.put(m,CurrentBank=3,CurrentBankC=2,SelectedCharacter=0,OperMode=1,GameEngineSubroutine=8,TimerControl=0,AreaType=1,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,Player_X_Position=32,Player_Y_Position=176,Player_Y_HighPos=1,ObjectOffset=0)
        return m
    def direct_source(m,name):
        c=Trace(memory=m,pc=L[name]);c.sp=224;c.stPushWord(0x5ffe)
        for _ in range(100000):
            if c.pc==0x5fff:return
            assert m[c.pc]!=0,(name,hex(c.pc));c.step()
        raise AssertionError(name)
    def put(m,n,v,i=0):m[W.address(b,n)+i]=v
    def field(m,n):return bytes(m[W.address(b,n):W.address(b,n)+6])
    tests=collections.Counter();cycles=[];art=[]
    try:
        # One genuine native Goomba establishes its own metasprite/position.
        # All six slots then pass through the actual native enemy loop and
        # cannon ingress60times, while empty slots have deliberately stale IDs.
        for live_slot in range(6):
            m=fresh()
            for i in range(6):
                for n,v in [('Enemy_Flag',0),('Enemy_ID',9 if i%2 else 0x1b),('Enemy_Y_HighPos',1),('Enemy_X_Position',80+i*16),('Enemy_Y_Position',184)]:put(m,n,v,i)
            for n,v in [('Enemy_Flag',1),('Enemy_ID',6)]:put(m,n,v,live_slot)
            N.put(m,ObjectOffset=live_slot);N.invoke(m,'InitGoomba',x=live_slot);N.invoke(m,'EnemiesAndLoopsCore',x=live_slot)
            pose=m[W.address(b,'ObjectMetasprite')+1+live_slot];assert pose>0
            before={n:field(m,n)for n in ['Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos','Enemy_X_Speed','Enemy_Y_Speed']}
            original_meta=bytes(m[W.address(b,'ObjectMetasprite')+1:W.address(b,'ObjectMetasprite')+7])
            m.ram[2][0x68]=1;cycles.append(call(m,'DkHitFreeze'))
            assert field(m,'Enemy_Flag')==bytes(0x80|i for i in range(6))
            start=dict(counts)
            for epoch in range(60):
                for i in range(6):N.put(m,ObjectOffset=i);N.invoke(m,'EnemiesAndLoopsCore',x=i)
                N.invoke(m,'ProcessCannons')
                assert field(m,'Enemy_X_Position')==before['Enemy_X_Position']and field(m,'Enemy_Y_Position')==before['Enemy_Y_Position']
                assert N.get(m,'TimerControl')==0
                tests['actual_enemy_loop_slot_suspensions']+=6;tests['actual_cannon_no_spawn_no_move_updates']+=1
            for name in ['RunEnemyObjectsCore','ProcLoopCommand','BulletBillHandler']:
                assert counts[name]==start.get(name,0),(name,dict(counts),start)
            N.put(m,CurrentOAMOffset=24,GuestOamRotationActive=0,RgOamUsed=24,VRAM_Buffer1_Offset=0);m[512:768]=[248,0,0,0]*64
            old=counts['DrawMetasprite'];N.invoke(m,'DrawAllMetasprites');assert counts['DrawMetasprite']>old
            assert m[W.address(b,'ObjectMetasprite')+1+live_slot]==pose
            records=[list(m[512+i:516+i])for i in range(0,256,4)if m[512+i]<240];assert records
            art.append(dict(slot=live_slot,genuine_metasprite=pose,native_visible_records=len(records),native_DrawMetasprite_calls=counts['DrawMetasprite']-old))
            start=len(m.writes);call(m,'DkHitThaw')
            assert {n:field(m,n)for n in before}==before and bytes(m[W.address(b,'ObjectMetasprite')+1:W.address(b,'ObjectMetasprite')+7])==original_meta
            for i in range(6):assert sum(at==W.address(b,'Enemy_Flag')+i for at,_ in m.writes[start:])==1
            start=len(m.writes);call(m,'DkHitThaw');assert not any(W.address(b,'Enemy_Flag')<=at<W.address(b,'Enemy_Flag')+6 for at,_ in m.writes[start:])
            tests['all_six_exact_flags_ids_metas_restore_once_and_repeat_noop']+=1
        # Actual cannon-bill ID09's independent path must also be suspended.
        for slot in range(3):
            m=fresh();put(m,'Enemy_Flag',1,slot);put(m,'Enemy_ID',9,slot);put(m,'Enemy_State',1,slot);put(m,'Enemy_X_Position',160,slot);put(m,'Enemy_Y_Position',160,slot);put(m,'Enemy_Y_HighPos',1,slot);put(m,'Enemy_X_Speed',24,slot)
            m.ram[2][0x68]=1;call(m,'DkHitFreeze');assert m[W.address(b,'Enemy_ID')+slot]==0
            old=counts['BulletBillHandler'];x=field(m,'Enemy_X_Position');N.invoke(m,'ProcessCannons');assert counts['BulletBillHandler']==old and field(m,'Enemy_X_Position')==x
            call(m,'DkHitThaw');assert m[W.address(b,'Enemy_ID')+slot]==9
            tests['positive_cannon_ID09_shadow_draw_contract']+=1
        # A genuine positive native birth of the sameID invalidates the old
        # receipt. A direct retirement cannot overwrite any newborn fields.
        for slot in range(6):
            m=fresh();put(m,'Enemy_Flag',1,slot);put(m,'Enemy_ID',6,slot);m.ram[2][0x68]=1;call(m,'DkHitFreeze')
            N.put(m,EnemyFrenzyQueue=6,ObjectOffset=slot,Enemy_Y_Position=176,WorldNumber=0,LevelNumber=0)
            N.invoke(m,'ChkEnemyFrenzy',x=slot,p=0x30);assert m[W.address(b,'Enemy_Flag')+slot]==1 and m[W.address(b,'Enemy_ID')+slot]==6
            newborn_names=['Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos','Enemy_X_Speed','Enemy_Y_Speed','Enemy_MovingDir','EnemyIntervalTimer']
            before={n:m[W.address(b,n)+slot]for n in newborn_names};call(m,'DkHitThaw');assert {n:m[W.address(b,n)+slot]for n in newborn_names}==before
            tests['actual_same_ID_positive_birth_retirement_preserves_newborn']+=1
        # Original hit routine alone determines duration/clock. The adapter
        # neither increments nor substitutes this source timer.
        m=fresh();donor,_=W.P.D.active();m.ram[2][:2048]=bytes(donor.memory[:2048]);m.ram[2][0x68]=1;m.ram[2][0x69]=0;m.ram[2][0x66]=0;m.ram[2][0x6b]=1;m.ram[2][0x38]=0x23
        call(m,'DkHitFreeze');clock=m.ram[2][0x38]
        for epoch in range(1,61):
            direct_source(m,'DkjrFruitHit')
            if epoch<60:assert m.ram[2][0x68]and m.ram[2][0x38]==clock
        assert not m.ram[2][0x68]and m.ram[2][0x38]==0x40
        call(m,'DkHitThaw');assert not any(m.ram[2][0x440:0x446]);tests['original_hit_60_updates_and_original_clock_terminal']+=1
    finally:N.NesMPU=native
    out=dict(passed=True,proposal_only=True,ROM_written=False,shared_hooks_added=False,native_owner_admitted=False,base_SHA256=A.PIN,component_bytes=len(helper),helper_span=[0xd540,H['DkFreezeEnd']],private_state_span=[0xc440,0xc458],checks=dict(tests),native_calls=dict(counts),genuine_art=art,first_freeze_CPU=dict(minimum=min(cycles),maximum=max(cycles)),
        source_semantics='Original D1AE owns60updates and Clock freeze/reset. Native six enemy slots (including empty spawn slots) are self-secondary while paused. Empty slots have no metasprite; cannon09 is temporarilyID00 because its independent native ProcessCannons bypasses secondary admission. All exact flags/IDs/empty metasprites restore once; positive same-ID native birth is never overwritten.',
        remaining=['Wire authenticated public Main/foreign retirement before any actor overlay invalidation. The v11 manager still needs a source-funded DK retire callback, not just header invalidation.','Native miscellaneous hammer/coin/firebar render policy is outside this focused1-1 ordinary enemy/cannon fixture; no all-stage global-object freeze claim.','Public source contact immunity during hit, all foreign/IRQ/metadata lifetimes and actual hardware remain unqualified.'],scope='Actual current native enemy loop/cannon/renderer/birth primitives in isolated legal Mario0 service fixtures. Source actor pause retains exact original timing. No raw40/menu/shared grant or Mesen execution.',bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),A.BASE,O/'native-body-v10.bin',O/'native-body-v10-layout.json',O/'hit-freeze-v12.s',O/'hit-freeze-v12.bin']})
    (O/'hit-freeze-v12-CPU.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','component_bytes','helper_span','private_state_span','checks','first_freeze_CPU']}))


if __name__=='__main__':main()
