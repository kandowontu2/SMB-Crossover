"""Sparse private source-equivalent robot palette queue folding on frozen3e7."""
from pathlib import Path
import difflib,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];B=R/'build';P=B/'mm_body_current.nes'
SHA='3e7c53d82eb949b8527d837861d95ed6051966056ca3f336fafd66e514e055ea'
sys.path.insert(0,str(R/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
HELPER='''; Foreground-only, after this source owner's complete3F11/3 append.
; The12-byte fastcase is two whole commands. General parsing is rare>=48.
; No NMI work/newRAM. Unknown formats or intervening overlaps decline folding.
.proc CompactMegaManPaletteTail
 cpx #12
 beq TwoCommands
 cpx #48
 bcs Scan
Done:
 lda #0
 clc
 rts
TwoCommands:
 lda VRAM_Buffer1
 cmp #$3f
 bne Done
 lda VRAM_Buffer1+1
 cmp #$11
 bne Done
 lda VRAM_Buffer1+2
 cmp #3
 bne Done
 lda VRAM_Buffer1+9
 sta VRAM_Buffer1+3
 lda VRAM_Buffer1+10
 sta VRAM_Buffer1+4
 lda VRAM_Buffer1+11
 sta VRAM_Buffer1+5
 lda #6
 sta VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1+6
 clc
 rts
Scan:
 php
 phx
 phy
 lda R0
 pha
 lda R1
 pha
 lda R2
 pha
 txa
 sec
 sbc #6
 sta R1                      ; End of old commands/current append's beginning.
 lda #$ff
 sta R0                      ; Last eligible complete3F11/3 command.
 ldx #0
Loop:
 cpx R1
 jeq Scanned
 jcs Restore
 lda VRAM_Buffer1,x
 jeq Restore                 ; Premature terminator/incomplete prefix.
 lda VRAM_Buffer1+2,x
 jeq Restore                 ; Native0=256; unknown long transfer declines.
 cmp #64
 jcs Restore                 ; RLE/vertical, including every alias: unchanged.
 clc
 adc #3
 sta R2
 txa
 adc R2
 jcs Restore
 cmp R1
 beq Bounded
 jcs Restore
Bounded:
 sta R2                      ; Next complete command, never a payload pattern.
 lda VRAM_Buffer1,x
 cmp #$40
 jcs Restore                 ; High address aliases decline, never guessed.
 cmp #$3f
 beq Palette
 cmp #$3e
 bne Advance
 lda VRAM_Buffer1+1,x
 clc
 adc VRAM_Buffer1+2,x
 bcs Restore                 ; Could enter palette RAM at3F00.
 jmp Advance
Palette:
 lda VRAM_Buffer1+1,x
 cmp #$11
 bne OtherPalette
 lda VRAM_Buffer1+2,x
 cmp #3
 bne OtherPalette
 stx R0
 jmp Advance
OtherPalette:
 lda VRAM_Buffer1+1,x
 and #31
 ldy VRAM_Buffer1+2,x
Overlap:
 cmp #$11
 bcc NextAddress
 cmp #$14
 bcs NextAddress
 lda #$ff
 sta R0                      ; Partial/full/mirrored writes break eligibility.
 jmp Advance
NextAddress:
 clc
 adc #1
 and #31
 dey
 bne Overlap
Advance:
 ldx R2
 jmp Loop
Scanned:
 ldy R0
 cpy #$ff
 beq Restore
 ; Remove the earlier complete6B command, retaining newest3F11 last.
 ; This also preserves the genuine pose parser's finalA/SafereturnA SMC.
 ; Forward memmove is safe: every source index is destination+6.
 tya
 clc
 adc #6
 tax
Move:
 lda VRAM_Buffer1,x
 sta VRAM_Buffer1,y
 inx
 iny
 cpx VRAM_Buffer1_Offset
 bcc Move
 lda #0
 sta VRAM_Buffer1,y
 sty VRAM_Buffer1_Offset
Restore:
 pla
 sta R2
 pla
 sta R1
 pla
 sta R0
 ply
 plx
 plp
 lda #0
 clc
 rts
.endproc
'''
def main():
 assert sha(P)==SHA
 b=scoped_load(P);raw=b['raw'];proof=json.loads((B/'mm_body_current_result.json').read_text());assert proof['candidate_sha256']==SHA
 for v in proof['reused_sparse_leaves'].values():assert sha(v['path'])==v['sha256']
 # Retain the declared6KiB Cheats owner and the independent BF00 HUD reserve.
 at=16+63*8192+0x1800;assert raw[at:16+63*8192+0x1f00]==bytes([255])*0x700
 for g in b['segs'].values():
  if'ooffs'in g:
   p,n=int(g['ooffs'],0),int(g['size'],0);assert not(n and p<at+0x700 and at<p+n)
 palette=(R/'src/megaman_palette.s').read_bytes().decode().replace('\r\n','\n')
 assert palette.count('.proc MegaManPaletteState')==1
 clone=palette.replace('.segment "INVENTORY"','.segment "PALETTE_COALESCE"').replace('.proc MegaManPaletteState','.proc CompactMegaManPaletteState')
 entry='''
 ; Death's early Graphics return has no later pose farcall to replace the SMC
 ; target latch. Invoke the genuine old routine there to preserve every latch.
 ; EOR changes neither carry nor overflow; original code reloads A/NZ.
 lda GameEngineSubroutine
 eor #$0b
 bne Authentic
 lda SafecallA_SMC+1
 farcall MegaManPaletteState,tail
Authentic:
'''
 clone=clone.replace('.proc CompactMegaManPaletteState\n','.proc CompactMegaManPaletteState\n'+entry)
 token='  sta VRAM_Buffer1,x\nDone:\n  rts';assert clone.count(token)==1
 clone=clone.replace(token,'  sta VRAM_Buffer1,x\n  jsr CompactMegaManPaletteTail\nDone:\n  rts')
 clone+='\n.pushseg\n.segment "PALETTE_COALESCE"\n'+HELPER+'\n.assert * <= $bf00,error,"Declared B800..BEFF cold owner"\n.popseg\n'
 hf=B/'proto_palette_coalesce.s';hf.write_text(clone,newline='\n')
 old=(R/'src/characters.s').read_bytes();nl=b'\r\n'if b'\r\n'in old else b'\n';token=b'  farcall MegaManPaletteState';assert old.count(token)==1
 new=old.replace(token,nl.join([b'.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5',b'  farcall CompactMegaManPaletteState',b'.else',token,b'.endif']))
 cp=B/'proto_palette_coalesce_characters.s';cp.write_bytes(new)
 ep=B/'proto_palette_coalesce_entrypoint.s';old_ep=(B/'mm_body_current_entrypoint.s').read_bytes();nl=b'\r\n'if b'\r\n'in old_ep else b'\n'
 epdata=old_ep.replace(b'.include "characters.s"',b'.include "proto_palette_coalesce_characters.s"')+nl+nl.join([b'.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5',b'.include "proto_palette_coalesce.s"',b'.endif',b'']);ep.write_bytes(epdata)
 oldcfg=(B/'mm_body_current.cfg').read_bytes();nl=b'\r\n'if b'\r\n'in oldcfg else b'\n';i=oldcfg.index(nl+b'}'+nl+b'SYMBOLS')
 cfg=B/'proto_palette_coalesce.cfg';cfgdata=oldcfg[:i]+nl+b'    PALETTE_COALESCE:load=X5_NEW_3F,type=ro,start=$b800;'+oldcfg[i:];cfg.write_bytes(cfgdata)
 out=B/'proto_palette_coalesce.nes';cmd=proof['command'][:]
 for i,v in enumerate(cmd):
  if v==str(B/'mm_body_current.cfg'):cmd[i]=str(cfg)
  elif v==str(B/'mm_body_current_entrypoint.s'):cmd[i]=str(ep)
  else:cmd[i]=v.replace('mm_body_current.dbg','proto_palette_coalesce.dbg').replace('mm_body_current.nes','proto_palette_coalesce.nes').replace('mm_body_current.map','proto_palette_coalesce.map').replace('mm_body_current.lbl','proto_palette_coalesce.lbl')
 z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);out.with_suffix('.build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,z.stdout+z.stderr
 sys.path.insert(0,str(R/'tools'));from prepare_cv3_dmc_mirror import prepare;prepare(R,out)
 n=scoped_load(out);after=n['raw'];assert raw[:16]==after[:16]and raw[16+128*8192:]==after[16+128*8192:]
 diff={bank:sum(a!=c for a,c in zip(raw[16+bank*8192:16+(bank+1)*8192],after[16+bank*8192:16+(bank+1)*8192]))for bank in range(128)};diff={k:v for k,v in diff.items()if v};assert set(diff)=={1,63}
 assert address(n,'_FARCALL_COUNT')==address(b,'_FARCALL_COUNT')+2
 for k,v in b['syms'].items():
  if k=='_FARCALL_COUNT':continue # Genuine assembler counter, not a PC/alias.
  assert n['syms'].get(k,{}).get('val')==v.get('val'),('Old qualified value moved',k)
  if 'seg'in v and'ooffs'in b['segs'][v['seg']]:assert location(b,k)==location(n,k),('Old physical PC/data moved',k)
 canonical_ep=(R/'src/entrypoint.s').read_bytes();nl=b'\r\n'if b'\r\n'in canonical_ep else b'\n';canonical_new_ep=canonical_ep+nl+nl.join([b'.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5',b'.include "proto_palette_coalesce.s"',b'.endif',b''])
 canonical_cfg=(R/'smb1base-mmc5-expanded.cfg').read_bytes();nl=b'\r\n'if b'\r\n'in canonical_cfg else b'\n';i=canonical_cfg.index(nl+b'}'+nl+b'SYMBOLS');canonical_new_cfg=canonical_cfg[:i]+nl+b'    PALETTE_COALESCE:load=X5_NEW_3F,type=ro,start=$b800;'+canonical_cfg[i:]
 patch=[]
 for name,a,c in [('src/characters.s',old,new),('src/proto_palette_coalesce.s',b'',clone.encode()),('src/entrypoint.s',canonical_ep,canonical_new_ep),('smb1base-mmc5-expanded.cfg',canonical_cfg,canonical_new_cfg)]:patch+=difflib.unified_diff(a.decode().splitlines(True),c.decode().splitlines(True),fromfile='a/'+name,tofile='b/'+name)
 pp=B/'proto_palette_coalesce.patch';pp.write_bytes(''.join(patch).encode())
 receipt=dict(source_only=True,native_run=False,installed=False,parent_sha256=SHA,candidate_sha256=sha(out),changed_banks=diff,all_header_CHR_other_banks_exact=True,old_symbol_values_exact=len(b['syms'])-1,assembler_counter_exception={'name':'_FARCALL_COUNT','old':address(b,'_FARCALL_COUNT'),'new':address(n,'_FARCALL_COUNT'),'reason':'Two genuine added farcall macro expansions; this is an assembler count, not an executable PC or alias.'},all_old_mapped_PC_data_locations_exact=True,new_RAM_bytes=0,new_NMI_work=0,allocation='Decimal63/$3F B800..BEFF, outside declared Cheats A000..B7FF and BfutureBF00..BFFF',module_bytes=int(next(g for g in n['segs'].values()if g['name']=='"PALETTE_COALESCE"')['size'],0),original_palette_and_tables_untouched=True,command=cmd,patch_sha256=sha(pp),bindings=[dict(path=str(f),bytes=f.stat().st_size,sha256=sha(f))for f in [Path(__file__),P,P.with_suffix('.dbg'),hf,cp,ep,cfg,pp,B/'mm_body_current_result.json']+[Path(v['path'])for v in proof['reused_sparse_leaves'].values()]],limits='Private source build only. CPU/fullGraphics/queue/overlap/IRQ/cost controls required; no native/lag/adoption claim. Ordinary append adds quickreject/death-admission cost; all measured rather than free-call claim.')
 put(B/'proto_palette_coalesce_build.json',receipt);print(json.dumps({k:receipt[k]for k in ['source_only','candidate_sha256','changed_banks','module_bytes','old_symbol_values_exact']}))
if __name__=='__main__':main()
