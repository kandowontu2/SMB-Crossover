"""Build a private explicit Parodius HUD publication protocol; no native run."""
from pathlib import Path
import argparse,difflib,hashlib,json,shutil,subprocess,sys
from parodius_visibility_candidate import replace
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
SHA='50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
GATE='''; Parodius-only queue cache. All old instructions/data retain their addresses.
.pushseg
.segment "PN_HUD_GATE"
.proc PnHudGate
 lda DisableScreenFlag
 bne Done
 lda VvVariant
 asl
 ora #1
 cmp InvHudActive
 bne Slow
 lda VvHudDirty
 bne Slow
 ; Clean valid labels: renew exactly the original physical font lease.
 lda VvVariant
 clc
 adc #.lobyte(395)
 sta InvHudPhysical
 lda X5HudChrUpper
 bmi CleanZero
 lda #.hibyte(396)
 sta X5HudChrUpper
CleanZero:
 lda #0
Done:rts
Slow:
 ; The normal farcall macro owns A. Keep A77 tables mapped and own C
 ; explicitly, using the same shadow-before-hardware NMI-safe convention.
 lda CurrentBankC
 pha
 lda #.bank(PnHudQueue) | MMC5_PRG_ROM
 sta CurrentBankC
 sta MMC5_PRG_BANK_C
 jsr PnHudQueue
 pla
 sta CurrentBankC
 sta MMC5_PRG_BANK_C
 rts
.endproc
.proc PnHudCancelLife
 ; Original callers have A=0. Keep A/XY/C/V and original store's NZ.
 sta InvHudActive
 lda X5HudChrUpper
 and #3
 sta X5HudChrUpper
 lda #0
 rts
.endproc
.proc PnHudNewLife
 lda #0
 jsr PnHudCancelLife
 tax
 rts
.endproc
.assert *-PnHudGate <=106,error,"Use only verified A77 tail"
.popseg
.pushseg
.segment "PN_HUD_INIT"
.proc PnHudInventoryInit
 pha
 lda X5HudChrUpper
 and #3
 sta X5HudChrUpper
 pla
 inc InvDirty
 rts
.endproc
.popseg
.pushseg
.segment "PN_HUD_TEXT"
.proc PnHudTextCancel
 ; WriteGameText overwrites Buffer1, including live warp-zone delivery.
 ; Keep its original saved-A stack item and exact ASL/TAY continuation.
 pha
 pha
 lda X5HudChrUpper
 bpl Restore
 and #3
 sta X5HudChrUpper
 lda #1
 sta VvHudDirty
Restore:
 pla
 asl
 tay
 jmp WriteGameText+3
.endproc
.assert *-PnHudTextCancel=23,error,"Exact verified bank3 tail"
.popseg
'''
QUEUE='''; A77 caller remains mapped while C116 owns the rare foreground helper.
; Pending: Upper=$80|(variant<<2)|1, Active=0, Physical=admission offset.
; Both hardware readers require Active!=0 and mask Upper with AND#3.
.pushseg
.segment "PN_HUD_QUEUE"
.proc PnHudQueue
 lda VvVariant
 cmp #1
 bcc Done
 cmp #4
 bcs Done
 asl
 ora #1
 cmp InvHudActive
 beq Valid
 lda InvHudActive
 bne Invalid
 lda X5HudChrUpper
 bpl Invalid
 and #$0c
 lsr
 lsr
 cmp VvVariant
 beq Done ; append already pending: preserve any new meter dirty state
Invalid:
 lda InvHudActive
 beq :+
 inc ReloadCHRBank
:
 lda #0
 sta InvHudActive
 lda X5HudChrUpper
 and #3
 sta X5HudChrUpper
 lda #1
 sta VvHudDirty
 lda PnInitialized
 cmp #$50
 bne Done
 lda PnBombPaletteReady
 cmp #1
 bne Done
 ldx VRAM_Buffer1_Offset
 cpx #0
 bne Done
 stx InvHudPhysical
 lda #$20
 sta VRAM_Buffer1,x
 lda #$22
 sta VRAM_Buffer1+1,x
 lda #28
 sta VRAM_Buffer1+2,x
 lda VvVariant
 sec
 sbc #1
 tay
 lda PnHud::GraphicalOffsets,y
 tay
 lda #28
 sta VvTemp2
Cells:
 lda PnHud::PnHudCells,y
 sta VRAM_Buffer1+3,x
 iny
 inx
 dec VvTemp2
 bne Cells
 inx
 inx
 inx
 jsr Attributes
 lda VvVariant
 asl
 asl
 ora #$81
 sta X5HudChrUpper
 rts
Valid:
 lda X5HudChrUpper
 bmi Done
 lda VvVariant
 clc
 adc #.lobyte(395)
 sta InvHudPhysical
 lda #1
 sta X5HudChrUpper
 lda VvHudDirty
 beq Done
 ldx VRAM_Buffer1_Offset
 cpx #32
 bcs Done
 txa
 pha
 jsr Attributes
 pla
 asl
 asl
 ora #$81
 sta X5HudChrUpper
 rts
Attributes:
 lda #$23
 sta VRAM_Buffer1,x
 lda #$c0
 sta VRAM_Buffer1+1,x
 lda #8
 sta VRAM_Buffer1+2,x
 txa
 clc
 adc #3
 tax
 lda #1
 sta VvTemp
 ldy #8
Loop:
 lda #$aa
 sta VvTemp2
 lda VvTemp
 and VvMeter
 beq RightNormal
 lda #$a6
 sta VvTemp2
RightNormal:
 lda VvTemp
 lsr
 and VvMeter
 beq LeftNormal
 lda VvTemp2
 and #$fc
 ora #1
 sta VvTemp2
LeftNormal:
 lda VvTemp2
 sta VRAM_Buffer1,x
 inx
 asl VvTemp
 dey
 bne Loop
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
 sta VvHudDirty
Done:rts
.endproc

; NMI owns C116, no foreground scratch/SMC or mapping changes. The normal
; gateway's ctrl0 selection starts at Buffer1. At this hook UpdateScreen has
; consumed every byte through the live terminator, before CHR/OAM publication.
.proc PnHudCommitAfterVram
 lda X5HudChrUpper
 bmi Pending
 lda OperMode
 jmp PnPaletteScreenUpdate+13
Pending:
 lda InvHudActive
 bne Return ; ctrl6 may retain an attribute command; pre-guard owns it.
 php
 txa
 pha
 tya
 pha
 lda SelectedCharacter
 cmp #18
 jne Cancel
 lda OperMode
 cmp #1
 jne Cancel
 lda GameEngineSubroutine
 cmp #8
 jne Cancel
 lda DisableScreenFlag
 jne Cancel
 lda PnInitialized
 cmp #$50
 jne Cancel
 lda PnBombPaletteReady
 cmp #1
 jne Cancel
 lda VvVariant
 cmp #1
 jcc Cancel
 cmp #4
 jcs Cancel
 asl
 asl
 ora #$81
 cmp X5HudChrUpper
 jne Cancel
 lda VRAM_Buffer_AddrCtrl
 cmp #6
 jeq Deferred
 cmp #0
 jne Cancel
 lda InvHudActive
 jne Cancel
 ldx InvHudPhysical
 cpx #1
 jcs Cancel
 lda VRAM_Buffer1_Offset
 cmp #84
 jcs Cancel
 sec
 sbc InvHudPhysical
 jcc Cancel
 cmp #42
 jne Cancel
 ; Check consumed pointer, including Buffer1's actual AF-page crossing.
 lda VRAM_Buffer1_Offset
 clc
 adc #<VRAM_Buffer1
 tax
 lda #>VRAM_Buffer1
 adc #0
 cmp NmiR1
 jne Cancel
 txa
 cmp NmiR0
 jne Cancel
 ldx InvHudPhysical
 lda VRAM_Buffer1,x
 cmp #$20
 bne Cancel
 lda VRAM_Buffer1+1,x
 cmp #$22
 bne Cancel
 lda VRAM_Buffer1+2,x
 cmp #28
 bne Cancel
 lda VRAM_Buffer1+31,x
 cmp #$23
 bne Cancel
 lda VRAM_Buffer1+32,x
 cmp #$c0
 bne Cancel
 lda VRAM_Buffer1+33,x
 cmp #8
 bne Cancel
 lda VvVariant
 clc
 adc #.lobyte(395)
 sta InvHudPhysical
 lda VvVariant
 asl
 ora #1
 sta InvHudActive
 lda #1
 sta X5HudChrUpper
 inc ReloadCHRBank
 jmp Deferred
Cancel:
 lda X5HudChrUpper
 and #3
 sta X5HudChrUpper
 lda #0
 sta InvHudActive
 lda #1
 sta VvHudDirty
Deferred:
 pla
 tay
 pla
 tax
 plp
Return:
 lda OperMode
 jmp PnPaletteScreenUpdate+13
.endproc
.popseg
'''
QUEUE=QUEUE.replace(' bcc Done',' jcc Done').replace(' bcs Done',' jcs Done').replace(' beq Done',' jeq Done').replace(' bne Done',' jne Done').replace(' beq Valid',' jeq Valid').replace(' bpl Return',' jpl Return')
QUEUE=QUEUE.replace(' bne Return ; ctrl6',' jne Return ; ctrl6')
QUEUE=QUEUE.replace(' bmi Done',' jmi Done')
PRE='''; Guard the final assembled packet, after every native foreground producer.
; Full labels are only queued first at offset0. Attribute admissions carry
; offset0..31 in Upper bits2..6 with Active!=0 and the physical font retained.
; All nonpending identities pay only this LDA/branch/JMP before native code.
.pushseg
.segment "PN_HUD_QUEUE"
.proc PnHudPreUpdateScreen
 lda X5HudChrUpper
 bmi Pending
Native:
 jmp PnPaletteScreenUpdate
Pending:
 lda InvHudActive
 jne AttrControl
 ; Common first-full case: ctrl0's initial pointer is owned by the
 ; resident VRAM_AddrTable selection. The post-flush commit still checks
 ; its consumed end pointer and six headers before leasing the font.
 lda VRAM_Buffer_AddrCtrl
 bne FullControl
 lda VRAM_Buffer1_Offset
 cmp #42
 bne FullGeneral
 lda GameEngineSubroutine
 cmp #8
 bne FullGeneral
 lda DisableScreenFlag
 bne FullGeneral
 jmp Native
FullControl:
 cmp #6
 jeq Native
 jmp Cancel
FullGeneral:
 lda NmiR0
 cmp #<VRAM_Buffer1
 jne Cancel
 lda NmiR1
 cmp #>VRAM_Buffer1
 jne Cancel
 lda InvHudPhysical
 jne Cancel
 lda VRAM_Buffer1_Offset
 cmp #42
 jcc Cancel
 jmp DeferFull
AttrControl:
 lda VRAM_Buffer_AddrCtrl
 cmp #6
 beq Native ; Buffer2 flush cannot consume or discard the pending Buffer1.
 cmp #0
 jne Cancel
 lda NmiR0
 cmp #<VRAM_Buffer1
 jne Cancel
 lda NmiR1
 cmp #>VRAM_Buffer1
 jne Cancel
 jmp Attr
 ; A full first-HUD append has no prefix. Never combine it with any later
 ; timer/score/palette/bomb command; those original commands still flush.
DeferFull:
 lda VRAM_Buffer1
 cmp #$20
 jne Cancel
 lda VRAM_Buffer1+1
 cmp #$22
 jne Cancel
 lda VRAM_Buffer1+2
 cmp #28
 jne Cancel
 lda VRAM_Buffer1+31
 cmp #$23
 jne Cancel
 lda VRAM_Buffer1+32
 cmp #$c0
 jne Cancel
 lda VRAM_Buffer1+33
 cmp #8
 jne Cancel
 lda #<(VRAM_Buffer1+42)
 sta NmiR0
 lda #>(VRAM_Buffer1+42)
 sta NmiR1
 clv ; native nonempty Buffer1's final pointer high-ADC always clears V.
 jmp Cancel
Attr:
 lda X5HudChrUpper
 and #$7c
 lsr
 lsr
 tax
 lda VRAM_Buffer1_Offset
 cmp #84
 jcs Cancel
 txa
 clc
 adc #11
 cmp VRAM_Buffer1_Offset
 bcc ExtentChecked
 beq ExtentChecked
 jmp Cancel
ExtentChecked:
 lda VRAM_Buffer1,x
 cmp #$23
 jne Cancel
 lda VRAM_Buffer1+1,x
 cmp #$c0
 jne Cancel
 lda VRAM_Buffer1+2,x
 cmp #8
 jne Cancel
 lda VRAM_Buffer1_Offset
 cmp #32
 bcs DeferAttr
 ; Success does not erase Dirty raised by a later meter/pickup owner.
 lda X5HudChrUpper
 and #3
 sta X5HudChrUpper
 jmp Native
DeferAttr:
 cpx #0
 beq AfterPrefix
 ; Flush the unmodified prefix through native UpdateScreen, ending only
 ; at the temporary attribute header. No foreground can observe this.
 lda #0
 sta VRAM_Buffer1,x
 jsr UpdateScreen
 lda X5HudChrUpper
 and #$7c
 lsr
 lsr
 tax
 lda #$23
 sta VRAM_Buffer1,x
AfterPrefix:
 txa
 clc
 adc #<(VRAM_Buffer1+11)
 sta NmiR0
 lda #>(VRAM_Buffer1+11)
 adc #0
 sta NmiR1
Cancel:
 lda X5HudChrUpper
 and #3
 sta X5HudChrUpper
 lda #1
 sta VvHudDirty
 jmp Native
.endproc
.popseg
'''
def edit(p,old,new):
 raw=p.read_bytes();nl=b'\r\n'if b'\r\n'in raw else b'\n'
 replace(p,old.replace('\n','\n').encode().replace(b'\n',nl),new.encode().replace(b'\n',nl))
def conditional(original,replacement):
 return '.if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5\n'+replacement+'\n.else\n'+original+'\n.endif'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--compiler',required=True,type=Path);p.add_argument('--copy-helper',type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);shutil.copy2(Path(__file__),a.output/Path(__file__).name)
 baseline=a.base/'baseline-rebuild-v2/candidate.nes';assert sha(baseline)==SHA
 source=a.output/'source';shutil.copytree(a.base/'nmi-fast-candidate-v1/source',source)
 edit(source/'src/parodius_render.s',' lda DisableScreenFlag\n jne GraphicalDone',conditional(' lda DisableScreenFlag',' jmp PnHudGate')+'\n jne GraphicalDone')
 for old in [' sta InvHudActive\n sta DisableCollisionDet']:
  # Two distinct lifecycle stores, each kept at its original three-byte PC.
  q=source/'src/vic_adapter.s';raw=q.read_text();assert raw.count(old)==2
  q.write_text(raw.replace(old,conditional(' sta InvHudActive',' jsr PnHudCancelLife')+'\n sta DisableCollisionDet'),encoding='utf-8',newline='')
 edit(source/'src/vic_adapter.s','NewLife:\n lda #0\n tax','NewLife:\n'+conditional(' lda #0\n tax',' jsr PnHudNewLife'))
 edit(source/'src/samus_freeze_render.s','.proc SamusFreezeInit\n  inc InvDirty','.proc SamusFreezeInit\n'+conditional('  inc InvDirty','  jsr PnHudInventoryInit'))
 edit(source/'src/samus_freeze_render.s','  jmp PnPaletteScreenUpdate','  jmp PnHudPreUpdateScreen')
 edit(source/'src/screen_render.s','cproc WriteGameText\n  pha                      ;save text number to stack\n    asl\n    tay', 'cproc WriteGameText\n'+conditional('  pha                      ;save text number to stack\n    asl\n    tay','  jmp PnHudTextCancel'))
 edit(source/'src/parodius_bells.s','.proc PnPaletteScreenUpdate\n jsr UpdateScreen\n lda SelectedCharacter\n cmp #18\n bne Samus\n lda OperMode','.proc PnPaletteScreenUpdate\n jsr UpdateScreen\n lda SelectedCharacter\n cmp #18\n bne Samus\n'+conditional(' lda OperMode',' jmp PnHudCommitAfterVram'))
 edit(source/'smb1base-mmc5-expanded.cfg','    VIC_WORLD:load=X5_NEW_4D,type=ro;','    VIC_WORLD:load=X5_NEW_4D,type=ro;\n    PN_HUD_GATE:load=X5_NEW_4D,type=ro;')
 edit(source/'smb1base-mmc5-expanded.cfg','    NMI_VRAM_FAST:load=X5_NEW_74,type=ro;','    NMI_VRAM_FAST:load=X5_NEW_74,type=ro;\n    PN_HUD_QUEUE:load=X5_NEW_74,type=ro;')
 edit(source/'smb1base-mmc5-expanded.cfg','    INVENTORY: load=XG_MUSIC_3B_MEM, type=ro, optional=yes;','    INVENTORY: load=XG_MUSIC_3B_MEM, type=ro, optional=yes;\n    PN_HUD_INIT:load=XG_MUSIC_3B_MEM,type=ro;')
 edit(source/'smb1base-mmc5-expanded.cfg','    WORLD_SPRITE_PALETTE: load=PRGA_03, type=ro, optional=yes, start=$bfc9;','    WORLD_SPRITE_PALETTE: load=PRGA_03, type=ro, optional=yes, start=$bfc9;\n    PN_HUD_TEXT:load=PRGA_03,type=ro;')
 f=source/'src/entrypoint.s';f.write_bytes(f.read_bytes()+b'\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n.include "parodius_hud_queue.s"\n.endif\n')
 (source/'src/parodius_hud_queue.s').write_text(GATE+QUEUE+PRE,encoding='utf-8')
 # The unadopted copy helper can move; all installed50b5 PCs remain fixed.
 edit(source/'src/nmi_vram_fast.s',' ; X=0 has the native meaning256, not an empty packet.\n cpx #0\n beq Chunk\n cpx #8\n bcc Tail',' ; X=0 naturally follows the native256-byte literal tail.\n cpx #8\n bcc LiteralTail')
 edit(source/'src/nmi_vram_fast.s','Tail:\n cpx #0\n beq LiteralDone\nLiteralTail:',' cpx #0\n bne LiteralTail\n clc\n jmp OutputToVRAM+11\nLiteralTail:')
 if a.copy_helper:
  assert sha(a.copy_helper)=='99d07b22d5851658b054a3f5445581545974a71df40f9b84330c23d2ecbb1df8','Only the reviewed full-continuation-proved arithmetic helper is accepted'
  shutil.copy2(a.copy_helper,source/'src/nmi_vram_fast.s')
 cmd=[sys.executable,'-B',str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),'--source-overlay',str(source),'--compiler',str(a.compiler),'--output',str(a.output/'candidate.nes')];r=subprocess.run(cmd,capture_output=True,text=True);(a.output/'host-build.log').write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stdout+r.stderr
 old=scoped_load(baseline);new=scoped_load(a.output/'candidate.nes');changed=[];patch=[]
 for f in sorted(source.rglob('*')):
  if not f.is_file()or'build'in f.relative_to(source).parts:continue
  rel=f.relative_to(source);prior=a.base/'baseline-source-v2'/rel
  if prior.exists()and f.read_bytes()==prior.read_bytes():continue
  if rel.suffix not in ['.s','.cfg']:continue
  changed.append(rel.as_posix());before=prior.read_text(encoding='utf-8').splitlines(keepends=True)if prior.exists()else[];patch.extend(difflib.unified_diff(before,f.read_text(encoding='utf-8').splitlines(keepends=True),fromfile='a/'+rel.as_posix(),tofile='b/'+rel.as_posix()))
 (a.output/'sourcepatch.patch').write_text(''.join(patch),encoding='utf-8')
 for n in old['syms']:assert n in new['syms']and address(old,n)==address(new,n),('old symbol shifted',n)
 hooks=[('OutputToVRAM',0),('PnPaletteScreenUpdate::Copy',0),('PnHud',0),('VvReset::Cleanup',2),('VvDeathStart',8),('VvEnsure::NewLife',0),('SamusFreezeInit',0),('SamusFreezeUpdateScreen',5),('PnPaletteScreenUpdate',10),('WriteGameText',0)]
 allowed=[];hookrows=[]
 for n,delta in hooks:
  at=location(old,n)+delta;allowed.append((at,3));hookrows.append(dict(symbol=n,delta=delta,offset=at,before=old['raw'][at:at+3].hex(),after=new['raw'][at:at+3].hex()))
  if (at-16)//8192==127:
   mirror=at-2*8192;assert old['raw'][mirror:mirror+3]==old['raw'][at:at+3]and new['raw'][mirror:mirror+3]==new['raw'][at:at+3]
   allowed.append((mirror,3));hookrows.append(dict(symbol=n+' DMC mirror125',delta=delta,offset=mirror,before=old['raw'][mirror:mirror+3].hex(),after=new['raw'][mirror:mirror+3].hex()))
 tails=[]
 for n in ['NMI_VRAM_FAST','PN_HUD_GATE','PN_HUD_QUEUE','PN_HUD_INIT','PN_HUD_TEXT']:
  g=next(g for g in new['segs'].values()if g['name']=='"'+n+'"');at=int(g['ooffs'],0);size=int(g['size'],0);assert old['raw'][at:at+size]==bytes([255])*size
  allowed.append((at,size));tails.append(dict(segment=n,offset=at,size=size,bank=(at-16)//8192))
 diff=[i for i,(x,y)in enumerate(zip(old['raw'],new['raw']))if x!=y];assert all(any(at<=i<at+n for at,n in allowed)for i in diff),[i for i in diff if not any(at<=i<at+n for at,n in allowed)][:20]
 q=dict(prepared=True,CPU_passed=False,native_run=False,goal_complete=False,before_sha256=SHA,after_sha256=sha(a.output/'candidate.nes'),script_sha256=sha(Path(__file__)),patch_sha256=sha(a.output/'sourcepatch.patch'),all_old_symbols_exact=True,old_symbols=len(old['syms']),CHR_bytes_exact=old['raw'][1048592:]==new['raw'][1048592:],changed_source={n:sha(source/n)for n in changed},hooks=hookrows,tails=tails,differing_bytes=len(diff),build_command=cmd)
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(q,indent=2))
if __name__=='__main__':main()
