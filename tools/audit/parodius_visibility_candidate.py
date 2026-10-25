"""Prepare/build the ROOT-reviewed private NMI copy optimization on frozen50b5."""
from pathlib import Path
import argparse, difflib, hashlib, json, shutil, subprocess, sys
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
SHA='50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
HELPER='''; NMI-only: bank116 is already owned by SamusFreezeUpdateScreen.
; Retain the native packet/data order, pointer/Y wrap, registers and flags.
; No new RAM, foreground scratch, SMC, JSR or stack frame.
.pushseg
.segment "NMI_VRAM_FAST"
.proc FastNmiVramCopy
 bcs Repeat
 ; X=0 has the native meaning256, not an empty packet.
 cpx #0
 beq Chunk
 cpx #8
 bcc Tail
Chunk:
 .repeat 8
  iny
  lda (NmiR0),y
  sta PPUDATA
  dex
 .endrepeat
 cpx #8
 bcs Chunk
Tail:
 cpx #0
 beq LiteralDone
LiteralTail:
 iny
 lda (NmiR0),y
 sta PPUDATA
 dex
 bne LiteralTail
LiteralDone:
 clc
 jmp OutputToVRAM+11 ; native SEC and pointer/next-command continuation
Repeat:
 lda (NmiR0),y
RepeatLoop:
 sta PPUDATA
 dex
 bne RepeatLoop
 sec
 jmp OutputToVRAM+11
.endproc
.proc FastNmiPaletteCapture
 .repeat 32,I
  lda PPUDATA
  sta PnBombPaletteShadow+I
 .endrepeat
 ldx #32
 cpx #32
 jmp PnPaletteScreenUpdate::Copy+11 ; after the unchanged old BNE
.endproc
.popseg
'''
def replace(p,old,new):
 text=p.read_bytes();assert text.count(old)==1,(str(p),text.count(old));p.write_bytes(text.replace(old,new))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--compiler',type=Path,required=True);a=p.parse_args();assert sha(a.base/'baseline-rebuild-v2/candidate.nes')==SHA;a.output.mkdir(parents=True,exist_ok=False);source=a.output/'source';shutil.copytree(a.base/'baseline-source-v2',source)
 reset=source/'src/reset.s';raw=reset.read_bytes();nl=b'\r\n'if b'\r\n'in raw else b'\n';replace(reset,nl.join([b'OutputToVRAM:',b'  bcs RepeatByte            ;if carry set, repeat loading the same byte',b'    iny                       ;otherwise increment Y to load next byte']),nl.join([b'OutputToVRAM:',b'.if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5',b'  jmp FastNmiVramCopy',b'.else',b'  bcs RepeatByte            ;if carry set, repeat loading the same byte',b'    iny                       ;otherwise increment Y to load next byte',b'.endif']))
 bells=source/'src/parodius_bells.s';replace(bells,b'Copy:\n lda PPUDATA\n',b'Copy:\n.if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5\n jmp FastNmiPaletteCapture\n.else\n lda PPUDATA\n.endif\n')
 cfg=source/'smb1base-mmc5-expanded.cfg';raw=cfg.read_bytes();nl=b'\r\n'if b'\r\n'in raw else b'\n';replace(cfg,b'    PARODIUS_EXTRA_ART:load=X5_NEW_74,type=ro;'+nl,b'    PARODIUS_EXTRA_ART:load=X5_NEW_74,type=ro;'+nl+b'    NMI_VRAM_FAST:load=X5_NEW_74,type=ro;'+nl)
 entry=source/'src/entrypoint.s';with_bytes=entry.read_bytes();nl=b'\r\n'if b'\r\n'in with_bytes else b'\n';entry.write_bytes(with_bytes+nl+b'.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5'+nl+b'.include "nmi_vram_fast.s"'+nl+b'.endif'+nl);(source/'src/nmi_vram_fast.s').write_text(HELPER,encoding='utf-8')
 changed=['src/reset.s','src/parodius_bells.s','src/entrypoint.s','src/nmi_vram_fast.s','smb1base-mmc5-expanded.cfg'];patch=[]
 for n in changed:
  original=a.base/'baseline-source-v2'/n;old=original.read_text(encoding='utf-8').splitlines(keepends=True)if original.exists()else[];new=(source/n).read_text(encoding='utf-8').splitlines(keepends=True);patch.extend(difflib.unified_diff(old,new,fromfile='a/'+n,tofile='b/'+n))
 (a.output/'sourcepatch.patch').write_text(''.join(patch),encoding='utf-8');rom=a.output/'candidate.nes';cmd=[sys.executable,'-B',str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),'--source-overlay',str(source),'--compiler',str(a.compiler),'--output',str(rom)];r=subprocess.run(cmd,capture_output=True,text=True);(a.output/'host-build.log').write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stdout+r.stderr
 old=scoped_load(a.base/'baseline-rebuild-v2/candidate.nes');new=scoped_load(rom);raw=rom.read_bytes();baseline=old['raw'];hooks=[(location(old,'OutputToVRAM'),3),(location(old,'PnPaletteScreenUpdate::Copy'),3)];helper=new['segs'][new['syms']['FastNmiVramCopy']['seg']];start=int(helper['ooffs'],0);size=int(helper['size'],0);assert(start-16)//8192==116
 for n in old['syms']:
  assert n in new['syms']and address(old,n)==address(new,n),('old public/link symbol shifted',n)
 allowed=[*hooks,(start,size)];diff=[i for i,(x,y)in enumerate(zip(baseline,raw))if x!=y];assert len(raw)==len(baseline)and all(any(lo<=i<lo+n for lo,n in allowed)for i in diff);assert all(v==255 for v in baseline[start:start+size]);assert location(old,'RepeatByte')==location(new,'RepeatByte');assert raw[location(new,'OutputToVRAM')+11]==0x38
 for at,n in hooks:assert raw[at]==0x4c
 q=dict(prepared=True,goal_complete=False,native_passed=False,ROM_before_sha256=SHA,ROM_after_sha256=sha(rom),script_sha256=sha(Path(__file__)),compiler_sha256=sha(a.compiler),sourcepatch_sha256=sha(a.output/'sourcepatch.patch'),changed_source={n:sha(source/n)for n in changed},all_old_symbol_addresses_exact=True,old_symbol_count=len(old['syms']),RAM_CHR_addresses_exact=True,CHR_bytes_exact=baseline[16+1048576:]==raw[16+1048576:],hooks=[dict(offset=at,before=baseline[at:at+n].hex(),after=raw[at:at+n].hex())for at,n in hooks],new_tail=dict(bank=116,offset=start,length=size,address=address(new,'FastNmiVramCopy'),before_all_FF=True),differing_bytes=len(diff),differing_banks=sorted({(i-16)//8192 for i in diff}),build_command=cmd,scope='Only two3-byte JMP hooks plus appended bank116 NMI helpers; all old labels/RAM/CHR and remaining bytes exact. Ordinaryflagoff not yet compiled. Source optimization only; native timing and exact CPU continuation tests required before acceptance.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(q,indent=2))
if __name__=='__main__':main()
