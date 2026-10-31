"""Project the recovered original Thomas source into isolated selected C2 state.

No current-roster object, menu, allocation or ROM is edited by this tool.
"""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).resolve().parent))
import thomas_original_cpu_1031_v1 as T
from prepare_thomas_component_1031_v3 import code
from private_build_outputs_v1 import validate
P=R/'build/thomas-original-component-v5';M=R/'build/thomas-melee-component-v2'
O=R/'build/thomas-c2-component-v1'
HOST=R/'build/contra-force-lives-position-1031-v3/joint/candidate.nes'
HOST_HAND=R/'docs/qa/checkpoints/2026-10-31/contra-force-lives-layout-source-v1/handoff.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dump=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

def main():
    global O
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=O);args=ap.parse_args();O=args.output.resolve()
    assert not O.exists();O.mkdir(parents=True);(O/'source').mkdir()
    assert sha(M/'source-stage.json')=='be3560da3039c474fcbd2db9f86a8e06286d9eeeb4108fbdcb8e76d33d95ac3e'
    assert sha(HOST)=='7b7f37eec12caf75fdccce29281d0cafb517c2c9e7d8d81e48aa5dbbd2927143'
    assert sha(HOST_HAND)=='ecee01d51d7b6a4ce39b20be1a8c6f63c75f603667afd4a1fac8b4441341b294'
    c=T.machine();cold1,i1,_=code(c,0x84f0,0x8522,'ThCold');cold2,i2,_=code(c,0x8563,0x860e,'ThCold');cold3,i3,_=code(c,0x8610,0x861c,'ThCold')
    reset,ri,_=code(c,0x830d,0x8319,'ThFrameReset');timers,ti,_=code(c,0x8321,0x8338,'ThTimers');controller,ci,_=code(c,0x9002,0x9032,'ThController')
    assert not ri and not ti and not ci
    # Native world/scene pointer table remains an explicit original dependency.
    assert not i1 and set(i2|i3)=={'ThomasOriginal_8610','ThomasOriginal_810E','ThomasOriginal_8114','ThomasOriginal_8117','ThomasOriginal_8119','ThomasOriginal_811D','ThomasOriginal_8112','ThomasOriginal_811B','ThomasOriginal_8102','ThomasOriginal_8106','ThomasOriginal_810A','ThomasOriginal_80F8'}
    cold2=cold2.replace('ThomasOriginal_8610','ThCold_8610')
    # Only the native clear-loop pointer's high-byte domain changes. Other
    # immediate data (physics, counters, palettes, audio) is never rebased.
    cold1=cold1.replace('ThCold_84FA: LDX #$03','ThCold_84FA: LDX #$C3').replace('ThCold_8509: CPX #$05','ThCold_8509: CPX #$C5').replace('ThCold_850F: CPX #$08','ThCold_850F: CPX #$C8')
    assert 'ThCold_84FA: LDX #$C3' in cold1 and 'ThCold_850F: CPX #$C8' in cold1
    refs=[]
    def project(text):
        lines=[]
        for line in text.splitlines():
            if line.lstrip().startswith('.segment'):continue
            body,sep,comment=line.partition(';')
            # Never rewrite immediates, labels, original ROM imports or data bytes.
            m=re.search(r'\b(lda|ldx|ldy|sta|stx|sty|adc|sbc|and|ora|eor|cmp|cpx|cpy|inc|dec|asl|lsr|rol|ror|bit)\s+(?:a:)?\$([0-9a-fA-F]{2,4})(?![0-9a-fA-F])',body,re.I)
            if m:
                address=int(m[2],16)
                if 16<=address<2048 or body.startswith('ThCold_84F4:'):
                    end=m.end(2);start=m.start(2)-1
                    if body[start-2:start]=='a:':start-=2
                    body=body[:start]+f'ThomasState+${address:04X}'+body[end:]
                    refs.append(dict(source=body.strip(),native=address,projected=0xc000+address))
            body=re.sub(r'\b(BEQ|BNE|BCC|BCS|BPL|BMI|BVC|BVS)\b',lambda m:'j'+m[1][1:].lower(),body,flags=re.I)
            lines.append(body+(sep+comment if sep else ''))
        return '\n'.join(lines)+'\n'
    core=project((P/'source/thomas_core.inc').read_text(encoding='utf-8'))
    health=project((P/'source/thomas_health.inc').read_text(encoding='utf-8'))
    geom=(M/'source/melee.s').read_text(encoding='utf-8')
    geom=geom[geom.index('ThGeom_C0B6:'):]
    geom=project(geom)
    cold=project(cold1+cold2+cold3)
    frame_helpers=project(reset)+' rts\n'+project(timers)+' rts\n'+project(controller)
    # A compiled native-reference wrapper uses these same original instructions
    # and source call order; the C2 worker adds epoch/ownership transaction guards.
    wrapper='''
.export ThomasC2ColdInit,ThomasC2AcceptedFrame,ThomasC2Borrow,ThomasC2Return
.export ThomasState,ThReady,ThBusy,ThOwnerPlayer,ThLastEpoch,ThHaveEpoch,ThPoseCommand
.export ThSavedZP,ThAcceptedCount
.export ThomasInput,ThomasMove,ThomasAnimate,ThomasSelectPose,ThomasNativeDamage
.export ThomasBodyBox,ThomasAttackBox,ThomasOverlap,ThomasAttackActive
ThomasInput=Th_A482
ThomasMove=Th_A696
ThomasAnimate=Th_A826
ThomasSelectPose=Th_A8EB
ThomasNativeDamage=ThHealth_C462
ThomasBodyBox=ThGeom_C0B6
ThomasAttackBox=ThGeom_C65B
ThomasOverlap=ThGeom_C0F3
ThomasState=$C000
ThReady=$C800
ThBusy=$C801
ThOwnerPlayer=$C802
ThLastEpoch=$C803
ThHaveEpoch=$C804
ThPoseCommand=$C805
ThFloor=$C806
ThAcceptedCount=$C807
ThSavedZP=$C810

; Preserve native caller AXYP. These wrappers communicate only through owned C2.
.macro SaveCaller
 php
 pha
 txa
 pha
 tya
 pha
.endmacro
.macro RestoreCaller
 pla
 tay
 pla
 tax
 pla
 plp
 rts
.endmacro

; Caller must establish Busy before borrowing. No nested owner entry is allowed.
ThomasC2Borrow:
 ldx #15
@Save:
 lda $00,x
 sta ThSavedZP,x
 lda ThomasState,x
 sta $00,x
 dex
 bpl @Save
 rts
ThomasC2Return:
 ldx #15
@Restore:
 lda $00,x
 sta ThomasState,x
 lda ThSavedZP,x
 sta $00,x
 dex
 bpl @Restore
 rts

; A=floor0..4, X=player0/1, Y=initial epoch. Cold does not consume an epoch.
; Complete private clear precedes genuine native life/floor initialization.
ThomasC2ColdInit:
 SaveCaller
 cpx #2
 jcs ThColdReject
 tsx
 lda $0103,x
 cmp #5
 jcs ThColdReject
 lda ThBusy
 jne ThColdReject
 lda #0
 sta ThReady
 lda #1
 sta ThBusy
 lda $0102,x
 sta ThOwnerPlayer
 sty ThLastEpoch
 tsx
 lda $0103,x
 sta ThFloor
 ldx #0
 lda #0
@Clear:
 sta ThomasState+$000,x
 sta ThomasState+$100,x
 sta ThomasState+$200,x
 sta ThomasState+$300,x
 sta ThomasState+$400,x
 sta ThomasState+$500,x
 sta ThomasState+$600,x
 sta ThomasState+$700,x
 inx
 bne @Clear
 jsr ThomasC2Borrow
 lda ThOwnerPlayer
 sta ThomasState+$55
 lda ThFloor
 sta ThomasState+$5f
 jsr ThCold_84F0
 jsr ThCold_8563
 ; Scene upload7..9 belongs to donor intro. Publish genuine idle body command.
 lda #0
 sta ThomasState+$52
 jsr ThomasSelectPose
 lda ThomasState+$52
 sta ThPoseCommand
 lda #0
 sta ThHaveEpoch
 sta ThAcceptedCount
 jsr ThomasC2Return
 lda #0
 sta ThBusy
 lda #$a7
 sta ThReady
ThColdReject:
 RestoreCaller

; A=unmodified donor held buttons; X=1 accepted actor update (0=lag/pause/etc),
; Y=foreground epoch modulo256. Duplicate epoch and busy/unready calls are inert.
; This is NOT a physical-NMI clock or an installed owner predicate.
ThomasC2AcceptedFrame:
 SaveCaller
 cpx #1
 jne ThFrameReject
 lda ThReady
 cmp #$a7
 jne ThFrameReject
 lda ThBusy
 jne ThFrameReject
 lda ThHaveEpoch
 jeq @New
 cpy ThLastEpoch
 jeq ThFrameReject
@New:
 lda #1
 sta ThBusy
 sty ThLastEpoch
 sta ThHaveEpoch
 jsr ThomasC2Borrow
 ; Actual donor frame reset/timer instruction slices, including slowtick20.
 jsr ThFrameReset_830D
 jsr ThTimers_8321
 ; Original controller bookkeeping9002..9031 from the raw held-byte ABI.
 tsx
 ; JSR Borrow has returned, so original callerA is at currentSP+3.
 lda $0103,x
 ldx ThomasState+$55
 jsr ThController_9002
 lda ThomasState+$14,x
 sta ThomasState+$6a
 ; Genuine87B5 dirty-pose detection before the previous-direction integrator.
 ldx ThomasState+$036f
 ldy ThomasState+$036e
 lda ThomasState+$69
 sta ThomasState+$036f
 lda ThomasState+$68
 sta ThomasState+$036e
 cpx ThomasState+$69
 bne @Dirty
 cpy ThomasState+$68
 beq @Move
@Dirty:
 lda #1
 sta ThomasState+$038f
@Move:
 jsr ThomasMove
 ; Native actors/contacts/world are explicit later host boundaries, not duplicated.
 lda ThomasState+$038f
 bne @Animate
 jsr ThomasInput
@Animate:
 jsr ThomasAnimate
 lda ThomasState+$038f
 beq @Finish
 jsr ThomasSelectPose
@Finish:
 lda ThomasState+$52
 beq @KeepPose
 sta ThPoseCommand
@KeepPose:
 inc ThAcceptedCount
 jsr ThomasC2Return
 lda #0
 sta ThBusy
ThFrameReject:
 RestoreCaller
'''
    depnames=set(re.findall(r'\.export (\w+)',(P/'source/lab_native_import.s').read_text(encoding='utf-8')))|((set(i2)|set(i3))-{'ThomasOriginal_8610'})
    header=' .setcpu "6502"\n .macpack longbranch\n'+''.join(f' .import {n}\n'for n in sorted(depnames))+' .segment "CODE"\n'
    (O/'source/component.s').write_text(header+core+health+geom+(P/'source/thomas_tables.inc').read_text(encoding='utf-8')+cold+frame_helpers+wrapper,encoding='utf-8')
    original=(P/'source/lab_native_import.s').read_text(encoding='utf-8')
    imports=(i2|i3);imports.pop('ThomasOriginal_8610')
    original+='\n'+''.join(f'.export {n}\n{n}=${v:04X}\n'for n,v in sorted(imports.items()))
    (O/'source/original_dependencies.s').write_text(original,encoding='utf-8')
    (O/'source/component.cfg').write_text('MEMORY { LAB: start=$6000,size=$2000,file=%O,fill=yes,fillval=$ff; }\nSEGMENTS { CODE: load=LAB,type=ro; }\n',encoding='utf-8')
    commands=[];cc=R/'tools/Windows/cc65/bin'
    def run(cmd):
        g=validate(cmd,O,cwd=O);p=subprocess.run([str(v)for v in cmd],cwd=O,capture_output=True,text=True);commands.append(dict(command=[str(v)for v in cmd],guard=g,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert not p.returncode,p.stderr
    for name in ['component','original_dependencies']:
        run([cc/'ca65.exe',O/f'source/{name}.s','-g','-o',O/f'{name}.o','-l',O/f'{name}.lst','--create-full-dep',O/f'{name}.dep'])
    run([cc/'ld65.exe','-C',O/'source/component.cfg',O/'component.o',O/'original_dependencies.o','-o',O/'component.bin','--dbgfile',O/'component.dbg','-Ln',O/'component.lbl','-m',O/'component.map'])
    dump(O/'build-commands.json',commands);dump(O/'state-reference-projection.json',refs)
    dump(O/'source-stage.json',dict(status='SOURCE_LINKED_ISOLATED_C2_NOT_HOST_ALLOCATED',parent_source_stage=sha(M/'source-stage.json'),
        state_model='Selected physicalRAM2 C view C000..C7FF native2KBprojection, C800..C81F localtransaction metadata. Lab-only; no sharedallocation.',
        borrowed_scratch='00..0F savedto selectedC2C810..C81F and restored around each acceptedtransaction; stack/registers restored, Busy forbids reentry',
        cold='Completeprivatezero then source84F0 +8563 +8610 and genuine idlepose before ReadyA7 LAST',
        frame='Native heldbutton latch/timers/dirtypose/move/input/animation/pose order; acceptedX1 and epochY dedup; no world/actor/contact/nativeNMI execution',
        source_projection='All direct native RAM16..07FF lifted to absoluteC2; indirect pointer00 staysscopedZP; native clearpointer03/05/08 high constants rebasedC3/C5/C8 only',
        preserved_dependencies='Original named damage metadata, foreignactorrelease B243 and original coldworldtables remain explicit dependencies; no audio/APU execution yet',
        future_terrain_base=dict(path=str(HOST),sha256=sha(HOST),handoff=str(HOST_HAND),handoff_sha256=sha(HOST_HAND)),
        bindings={str(p):sha(p)for p in [Path(__file__),Path(T.__file__),R/'tools/audit/prepare_thomas_component_1031_v3.py',R/'tools/audit/private_build_outputs_v1.py',M/'source-stage.json',P/'source/thomas_core.inc',P/'source/thomas_health.inc',P/'source/thomas_tables.inc',M/'source/melee.s',P/'source/lab_native_import.s',HOST,HOST_HAND]+[p for p in O.rglob('*')if p.is_file()]}))
    print(json.dumps(dict(result='SOURCE_LINKED',source_stage_sha256=sha(O/'source-stage.json'),component_sha256=sha(O/'component.bin'))))

if __name__=='__main__':main()
