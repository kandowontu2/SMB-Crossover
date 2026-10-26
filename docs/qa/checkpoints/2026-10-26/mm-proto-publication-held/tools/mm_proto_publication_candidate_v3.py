"""Build one private731 publication-aware body/shot priority experiment."""
from pathlib import Path
import argparse,difflib,hashlib,json,shutil,subprocess,sys,traceback
from check_tmnt_audio_fallback_oc import qualified
from link_pit_rygar_sophia_audit_cpu import scoped_load

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT=D/'mm-proto-clean-menu-candidates-v1/clean-menu-irq'
DONOR=D/'mm-proto-body-priority-v3'
EXPECTED='731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p,z):Path(p).write_text(json.dumps(z,indent=2)+'\n')


def edit(p,old,new):
    raw=p.read_bytes();nl=b'\r\n' if b'\r\n' in raw else b'\n'
    x,y=[s.replace('\n',nl.decode()).encode() for s in [old,new]]
    assert raw.count(x)==1,(p,old)
    p.write_bytes(raw.replace(x,y))


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();assert not a.output.resolve().is_relative_to(R)
    a.output.mkdir(parents=True,exist_ok=False)
    try:
        assert sha(PARENT/'candidate.nes')==EXPECTED
        assert sha(DONOR/'candidate.nes')=='00fb4a72ec9788f7b2878d6201f70a96ae6e47b4935ba186648c7edc04806a62'
        manifest=json.loads((PARENT/'source-manifest.json').read_text())
        source=a.output/'source'
        for rel,h in manifest.items():
            src,dst=PARENT/'source'/rel,source/rel;assert sha(src)==h
            dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
        for rel in ['src/megaman_weapons.s','src/metasprite_engine.s','smb1base-mmc5-expanded.cfg']:
            shutil.copyfile(DONOR/'source'/rel,source/rel)
        weapons=source/'src/megaman_weapons.s';engine=source/'src/metasprite_engine.s'
        edit(weapons,'''  lda #$80                    ; Existing boolean owner, explicit body-first mode.
  sta GuestOamRotationActive''','''  bit MmPublicationState      ; Same desired bit6 until a real regular DMA ack.
  bvs PublicationShotTurn
  lda #$80                    ; Body prefix0; mode bit6 clear.
  sta GuestOamRotationActive''')
        edit(weapons,'''PriorityLegacy:
  ldx #0
  jmp MmBodyPriorityClearRing''','''PublicationShotTurn:
  lda #$c0                    ; Shot prefix0; positive body cursor after shots.
  sta GuestOamRotationActive
  ldx #0
  jmp MmPublicationZeroRotation
PriorityLegacy:
  ; Ineligible/hidden/death draw replaces the old tagged page. Retain only
  ; desired bit6; no invalid image may be acknowledged as a priority turn.
  asl MmPublicationState
  lsr MmPublicationState
  ldx #0
  jmp MmBodyPriorityClearRing''')
        edit(weapons, '  tax                         ; Reserve40/44 before every nonbody admission.\n  lda #0', '  tax                         ; Reserve40/44 before every nonbody admission.\n::MmPublicationZeroRotation:\n  lda #0')
        edit(weapons,'''  .res 23,$ea
  .assert *-MegaManDrawShots=139,error,"Shot wrapper original span"''','''  .res 2,$ea
  .assert *-MegaManDrawShots=139,error,"Shot wrapper original span"''')
        edit(weapons,'''  lda ObjectVerticalFlip
  bmi No
  sec
  rts''','''  lda ObjectVerticalFlip
  eor #$80
  asl                         ; C=1 precisely when the original sign was clear.
  rts''')
        edit(weapons,'''  lda CurrentOAMOffset
  clc
  adc RgOamPlayerStart
  sta CurrentOAMOffset
  sec
  sbc RgOamFirst''','''  sta MmPublicationState      ; A is the genuine owned80/C0 mode from tail.
  lda CurrentOAMOffset
  bit GuestOamRotationActive
  bvs PublicationLogicalReady
  clc
  adc RgOamPlayerStart         ; Body0 logical count excludes the real shots.
  sta CurrentOAMOffset
PublicationLogicalReady:
  sec
  sbc RgOamFirst''')
        edit(weapons,'''  lda RgOamFirst
  eor #$ff
  clc
  adc #1
  sta RgOamRotation''','''  lda #0
  sec
  sbc RgOamFirst
  sta RgOamRotation''')
        edit(engine,'''    lda #0
.if ::ENABLE_CROSSOVER
    ldx GuestOamRotationActive
    beq :+
.if ::ENABLE_MMC5_EXPANDED
    bmi :+
.endif
      lda RgOamPlayerStart
    :
.endif
    sta CurrentOAMOffset''','''.if ::ENABLE_MMC5_EXPANDED
    ; Existing modes0/1 and owned80/C0: ASL is zero only for legacy0/body80.
    ; X is dead here; the genuine next player LDX replaces it on every path.
    lda GuestOamRotationActive
    asl
    beq :+
      lda RgOamPlayerStart
    :
.else
    lda #0
.if ::ENABLE_CROSSOVER
    ldx GuestOamRotationActive
    beq :+
      lda RgOamPlayerStart
    :
.endif
.endif
    sta CurrentOAMOffset''')
        edit(engine,''' .res 10,$ea
::WorldFirebarAdmissionDone:
 rts
 .assert *-WorldFirebarDrawAdmission=35,lderror,"Private body-priority admission span"''','''::MmPublicationClearOamCursor:
 lda #0
 sta CurrentOAMOffset
 sta MmPublicationState
 rts
 .res 4,$ea
::WorldFirebarAdmissionDone:
 rts
 .assert *-WorldFirebarDrawAdmission=38,lderror,"Publication priority admission span"''')
        edit(engine,'''MoveAllSpritesOffscreen:
  ldy #0
  sty CurrentOAMOffset
  lda #$f8''','''MoveAllSpritesOffscreen:
.if ::ENABLE_MMC5_EXPANDED
  jsr MmPublicationClearOamCursor
  ldy #0
.else
  ldy #0
  sty CurrentOAMOffset
.endif
  lda #$f8''')
        # Both turns retain the same logicalR reservation/capacity. Only the
        # shot emitter's physical rotation differs; restore0 before allworld.
        edit(weapons, '''  bit MmPublicationState      ; Same desired bit6 until a real regular DMA ack.
  bvs PublicationShotTurn
  lda #$80                    ; Body prefix0; mode bit6 clear.
  sta GuestOamRotationActive
  jsr ProtoOamReservation
  tax                         ; Reserve40/44 before every nonbody admission.
::MmPublicationZeroRotation:
  lda #0
  sta RgOamRotation
  jmp MmBodyPriorityClearRing
PublicationShotTurn:
  lda #$c0                    ; Shot prefix0; positive body cursor after shots.
  sta GuestOamRotationActive
  ldx #0
  jmp MmPublicationZeroRotation''', '''  lda MmPublicationState
  and #$40
  ora #$80                    ; owned80body / C0shots, always an actual reserveR.
  sta GuestOamRotationActive
  jsr ProtoOamReservation
  tax                         ; Both priority turns begin logicalR40/44.
  lda #0
  bit GuestOamRotationActive
  bvc PublicationStoreRotation
  txa
  eor #$ff
  clc
  adc #1                      ; shot physical0 = logicalR + (-R).
PublicationStoreRotation:
  sta RgOamRotation
  jmp MmBodyPriorityClearRing''')
        edit(weapons, '  .res 2,$ea\n  .assert *-MegaManDrawShots=139,error,"Shot wrapper original span"', '  .res 1,$ea\n  .assert *-MegaManDrawShots=139,error,"Shot wrapper original span"')
        edit(engine, '''  jsr MmBodyPriorityFinish
  jmp InitObjectLoop
  .res 13,$ea                 ; Retain the following object-loop addresses.''', '''  jsr MmBodyPriorityFinish
  bit GuestOamRotationActive
  bpl PublicationWorldReady
  lda #0
  sta RgOamRotation           ; world has the same mapping on both turns.
PublicationWorldReady:
  jmp InitObjectLoop
  .res 3,$ea                  ; Retain the actual original object-loop PCs.''')
        core=source/'src/protoman_cold.s'
        old=core.read_text().split('.proc ProtoNmiAudioCore\n',1)[1].split('.endproc',1)[0]
        b=scoped_load(PARENT/'candidate.nes');size=int(b['syms']['ProtoNmiAudioCore']['size'],0)
        edit(core,'.proc ProtoNmiAudioCore\n'+old+'.endproc',f'''.proc ProtoNmiAudioCore
  jmp MmPublicationAudioCore
  .res {size-3},$ea
  .assert *-ProtoNmiAudioCore={size},error,"Original public NMI core wrapper span"
.endproc''')
        gate='''; One new explicitly declared lifecycle owner; never borrow audio/OAM scratch.
MmPublicationState=$5ff8
.export MmPublicationState
.pushseg
.segment "MM_PUBLICATION_COLD"
.proc MmPublicationAudioCore
  ; This real core is reached only by Mega/Proto AudioUpdate. The outer
  ; regularNMI return word lies atSP+5; savedP/X move it toSP+7/+8.
  ; Main cannot mutate page2 while NMI owns this acknowledged transfer.
  php
  bit MmPublicationState
  bpl NoPending
  phx
  tsx
  lda $0107,x
  cmp #<(MmPublicationRegularAudioCall+2)
  bne RestoreX
  lda $0108,x
  cmp #>(MmPublicationRegularAudioCall+2)
  bne RestoreX
  lda OperMode
  cmp #1
  bne Invalidate
  lda OperMode_Task
  cmp #3
  bne Invalidate
  lda GameEngineSubroutine
  cmp #8
  bne Invalidate
  lda MmDeathFlag
  bne Invalidate
  lda MmPublicationState
  eor #$c0                    ; pending80->desired40; pendingC0->desired0.
  sta MmPublicationState
  jmp RestoreX
Invalidate:
  lda #0                      ; scene/death replacement cannot consume a turn.
  sta MmPublicationState
RestoreX:
  plx
NoPending:
  plp
'''+old+'''.endproc
.assert *<=$bb50,error,"Publication cold code overlaps pinned menuBB50"
.popseg
'''
        (source/'src/mm_proto_publication.s').write_text(gate)
        entry=source/'src/entrypoint.s';entry.write_bytes(entry.read_bytes()+b'\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n.include "mm_proto_publication.s"\n.endif\n')
        reset=source/'src/reset.s'
        edit(reset,'''  jsr AudioUpdate
  
.if ::DEBUG_WORLD_SELECT''','''.if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5
::MmPublicationRegularAudioCall:
.endif
  jsr AudioUpdate
  
.if ::DEBUG_WORLD_SELECT''')
        cfg=source/'smb1base-mmc5-expanded.cfg'
        edit(cfg,'    MENU_VRAM_BUDGET: load=X5_NEW_42,type=ro,start=$bb50,optional=yes;\n','    MM_PUBLICATION_COLD: load=X5_NEW_42,type=ro,start=$b9a8;\n    MENU_VRAM_BUDGET: load=X5_NEW_42,type=ro,start=$bb50,optional=yes;\n')
        previous=PARENT/'candidate.nes';raw=previous.read_bytes()
        assert raw[16+66*8192+0x19a8:16+66*8192+0x1b50]==bytes([255])*424
        assert raw[16+4*8192+0x1f33:16+4*8192+0x1f8b]==bytes([255])*88
        new={rel:sha(source/rel) for rel in manifest};new['src/mm_proto_publication.s']=sha(source/'src/mm_proto_publication.s')
        changed=[rel for rel,h in manifest.items() if new[rel]!=h]+['src/mm_proto_publication.s']
        put(a.output/'source-manifest.json',new)
        patch=[]
        for rel in changed:
            left=(PARENT/'source'/rel).read_text().splitlines(True) if rel in manifest else []
            patch+=difflib.unified_diff(left,(source/rel).read_text().splitlines(True),fromfile='clean731/'+rel,tofile='private/'+rel)
        (a.output/'source.patch').write_text(''.join(patch))
        cmd=[sys.executable,'-B',str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),'--compiler',str(R/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')]
        z=subprocess.run(cmd,cwd=source,capture_output=True,text=True)
        put(a.output/'build-launch.json',dict(command=cmd,exit=z.returncode,stdout=z.stdout,stderr=z.stderr))
        assert z.returncode==0,z.stdout+z.stderr
        candidate=a.output/'candidate.nes';after=candidate.read_bytes()
        assert raw[:16]==after[:16] and raw[16+128*8192:]==after[16+128*8192:]
        delta={i:sum(x!=y for x,y in zip(raw[16+i*8192:16+(i+1)*8192],after[16+i*8192:16+(i+1)*8192])) for i in range(128)}
        delta={i:n for i,n in delta.items() if n};assert set(delta)=={4,66},delta
        qb,qa=qualified(previous),qualified(candidate)
        moves=[dict(name=list(n),old=v,new=qa.get(n)) for n,v in qb.items() if qa.get(n)!=v]
        for n in ['NonMaskableInterrupt','OAMandReadJoypad','AudioUpdate','ProtoNmiAudioCore','ProtoMenuPrepare','MoveAllSpritesOffscreen','OAMClear','DrawMetasprite','MetaspriteRenderLoop']:
            assert qb[(n,)]==qa[(n,)],(n,qb[(n,)],qa.get((n,)))
        assert qa[('MmPublicationState',)]==0x5ff8
        put(a.output/'genuine-symbol-movement.json',moves)
        proof=dict(passed=True,source_only=True,native_run=False,installed=False,parent_ROM_sha256=EXPECTED,ROM_sha256=sha(candidate),changed_source=changed,changed_PRG_bytes=delta,
                   new_lifecycle_byte=0x5ff8,no_existing_RAM_or_CHR_moved=True,genuine_symbol_moves=moves,public_original_NMI_DMA_Audio_core_and_render_entries_retained=True,
                   private_original_core_Original_Restore_labels_removed_with_actual_body_relocation=True,prototype00fb_held=True,
                   limits='Build/layout only; no CPU/source/audio/caller/lifecycle/capacity/cost/IRQ/native acceptance yet. Actual construction acknowledges only a regularNMI call route; body/shot/world visibility tradeoff remains.',tool_sha256=sha(__file__))
        put(a.output/'proof.json',proof);print(json.dumps(proof,indent=2))
    except BaseException as e:
        put(a.output/'failure.json',dict(passed=False,native_run=False,error=repr(e),traceback=traceback.format_exc(),tool_sha256=sha(__file__)))
        shutil.copyfile(__file__,a.output/'failed-tool.py');raise


if __name__=='__main__':main()
