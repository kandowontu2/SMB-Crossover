"""Build private5354 HUD death-hold/cancellation ownership repair; no native run."""
from pathlib import Path
import argparse,collections,difflib,hashlib,json,shutil,subprocess,sys
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
ROOT=Path(__file__).resolve().parents[2]
SHA='5354161f339548f2e12b955f5fc1481b9956fe83a63263a04f4b2816edbbdf30'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
TAIL='''
; Rare foreground lifecycle work. The A77 stub owns a real C-window bracket;
; no new RAM or farcall SMC is used. All three real callers supply A=0.
.pushseg
.segment "PN_HUD_LIFE_GATE"
.proc PnHudCancelGateway
 lda CurrentBankC
 pha
 lda #.bank(PnHudCancelWork) | MMC5_PRG_ROM
 sta CurrentBankC
 sta MMC5_PRG_BANK_C
 jmp PnHudCancelWork
.endproc
.assert *-PnHudCancelGateway=15,error,"Verified A77 tail only"
.popseg
.pushseg
.segment "PN_HUD_LIFE"
.proc PnHudCancelWork
 php
 txa
 pha
 tya
 pha
 ; Real return word below Y/X/P/oldC identifies the explicit death caller.
 ; Reset and new-life cancellation must not preserve a former label lease.
 tsx
 lda $0105,x
 cmp #<(VvDeathHudCancelled-1)
 jne Cancel
 lda $0106,x
 cmp #>(VvDeathHudCancelled-1)
 jne Cancel
 lda VvVariant
 cmp #1
 jcc Cancel
 cmp #4
 jcs Cancel
 asl
 ora #1
 cmp InvHudActive
 jne Cancel
 lda VvVariant
 clc
 adc #.lobyte(395)
 cmp InvHudPhysical
 jne Cancel
 lda X5HudChrUpper
 and #3
 cmp #1
 jeq Restore ; committed labels keep their exact font through native death
Cancel:
 lda X5HudChrUpper
 jpl Invalidate
 lda InvHudActive
 beq Full
 ; Pending attribute ownership encodes its original offset0..31 in Upper.
 lda X5HudChrUpper
 and #$7c
 lsr
 lsr
 tay
 tax
 lda VRAM_Buffer1,x
 cmp #$23
 jne Invalidate
 lda VRAM_Buffer1+1,x
 cmp #$c0
 jne Invalidate
 lda VRAM_Buffer1+2,x
 cmp #8
 jne Invalidate
 txa
 clc
 adc #11
 tax
 jmp Extent
Full:
 lda InvHudPhysical
 jne Invalidate
 lda VRAM_Buffer1
 cmp #$20
 jne Invalidate
 lda VRAM_Buffer1+1
 cmp #$22
 jne Invalidate
 lda VRAM_Buffer1+2
 cmp #28
 jne Invalidate
 lda VRAM_Buffer1+31
 cmp #$23
 jne Invalidate
 lda VRAM_Buffer1+32
 cmp #$c0
 jne Invalidate
 lda VRAM_Buffer1+33
 cmp #8
 jne Invalidate
 ldy #0
 ldx #42
Extent:
 cpx VRAM_Buffer1_Offset
 bcc Copy
 bne Invalidate
Copy:
 lda VRAM_Buffer1,x
 sta VRAM_Buffer1,y
 cpx VRAM_Buffer1_Offset
 beq Copied
 inx
 iny
 bne Copy
Copied:
 sty VRAM_Buffer1_Offset
 lda #1
 sta VvHudDirty
Invalidate:
 lda #0
 sta InvHudActive
 lda X5HudChrUpper
 and #3
 sta X5HudChrUpper
Restore:
 pla
 tay
 pla
 tax
 plp
 pla ; original C bank; restore code is safely in the unchanged A window
 jmp PnHudCancelRestore
.endproc
.popseg
'''


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--parent',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--compiler',type=Path,default=ROOT/'tools/Windows/cc65/bin/cl65.exe');a=p.parse_args()
 assert sha(a.parent/'candidate.nes')==SHA and not a.output.resolve().is_relative_to(ROOT)
 a.output.mkdir(parents=True,exist_ok=False);src=a.output/'source';shutil.copytree(a.parent/'source',src)
 changed={};f=src/'src/parodius_hud_queue.s';text=f.read_text();old='''.proc PnHudCancelLife
 ; Original callers have A=0. Keep A/XY/C/V and original store's NZ.
 sta InvHudActive
 lda X5HudChrUpper
 and #3
 sta X5HudChrUpper
 lda #0
 rts
.endproc'''
 new='''.proc PnHudCancelLife
 jmp PnHudCancelGateway
::PnHudCancelRestore:
 sta CurrentBankC
 sta MMC5_PRG_BANK_C
 lda #0
 rts
 .byte $ea,$ea
.endproc
.assert *-PnHudCancelLife=14,error,"Keep every old entry PC"'''
 assert text.count(old)==1;f.write_text(text.replace(old,new)+TAIL,encoding='utf-8');changed['src/parodius_hud_queue.s']=sha(f)
 f=src/'src/vic_adapter.s';text=f.read_text();old='''.proc VvDeathStart
 lda #0
 sta VvAlive
 sta VvDeathAge
.if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5
 jsr PnHudCancelLife''';assert text.count(old)==1;f.write_text(text.replace(old,old+'\n::VvDeathHudCancelled:'),encoding='utf-8');changed['src/vic_adapter.s']=sha(f)
 f=src/'smb1base-mmc5-expanded.cfg';text=f.read_text();text=text.replace('    PN_HUD_GATE:load=X5_NEW_4D,type=ro;','    PN_HUD_GATE:load=X5_NEW_4D,type=ro;\n    PN_HUD_LIFE_GATE:load=X5_NEW_4D,type=ro;');text=text.replace('    NMI_VRAM_SCROLL:load=X5_NEW_74,type=ro;','    NMI_VRAM_SCROLL:load=X5_NEW_74,type=ro;\n    PN_HUD_LIFE:load=X5_NEW_74,type=ro;');f.write_text(text,encoding='utf-8');changed['smb1base-mmc5-expanded.cfg']=sha(f)
 r=subprocess.run([sys.executable,'-B',str(src/'tools/build_mmc5_expanded.py'),'--workspace',str(src),'--compiler',str(a.compiler),'--output',str(a.output/'candidate.nes')],capture_output=True,text=True);(a.output/'build-host.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout+r.stderr
 b=scoped_load(a.parent/'candidate.nes');n=scoped_load(a.output/'candidate.nes');hook=location(b,'PnHudCancelLife')
 for name,s in b['syms'].items():assert name in n['syms']and s['val']==n['syms'][name]['val'],name
 ranges=[(hook,hook+14)]
 for name,bank in [('PnHudCancelGateway',77),('PnHudCancelWork',116)]:
  at=location(n,name);size=int(n['syms'][name]['size'],0);assert(at-16)//8192==bank and b['raw'][at:at+size]==b'\xff'*size;ranges.append((at,at+size))
 diff=[i for i,(x,y)in enumerate(zip(b['raw'],n['raw']))if x!=y];assert all(any(lo<=i<hi for lo,hi in ranges)for i in diff)
 assert b['raw'][16+1048576:]==n['raw'][16+1048576:]
 patch=''.join(''.join(difflib.unified_diff((a.parent/'source'/name).read_text().splitlines(keepends=True),(src/name).read_text().splitlines(keepends=True),fromfile='a/'+name,tofile='b/'+name))for name in changed);(a.output/'sourcepatch.patch').write_text(patch)
 q=dict(prepared=True,native_run=False,adopted=False,CPU_passed=False,parent_ROM_sha256=SHA,candidate_ROM_sha256=sha(a.output/'candidate.nes'),
        all_parent_symbols_exact=len(b['syms']),CHR_exact=True,delta_bytes=len(diff),delta_banks=dict(collections.Counter((i-16)//8192 for i in diff)),
        changed_source=changed,ranges=ranges,new_death_return_label=address(n,'VvDeathHudCancelled'),tool_sha256=sha(Path(__file__)),patch_sha256=sha(a.output/'sourcepatch.patch'),
        limits='PRIVATE source build only. Foreground A=0 actual-three-caller contract, exact fullcallers/queue removal/PPU/Buffer2/real NMI+IRQ interference/budget and all build flags require qualification. Original5354 negatives and qualified menu remain historical; no native/adoption grant.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
