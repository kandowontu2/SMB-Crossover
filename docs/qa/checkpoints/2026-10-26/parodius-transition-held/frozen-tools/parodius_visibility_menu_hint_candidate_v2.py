"""Private render-off initial ship hint publication; no native/installation."""
from pathlib import Path
import argparse,collections,difflib,hashlib,json,shutil,subprocess,sys
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
TAIL='''

.if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5
.pushseg
.segment "PN_MENU_HINT"
; BuildScreen owns direct PPUDATA while display is off and GameLoop's
; NmiDisable is negative. Lag NMI skips PPU work with DisableScreenFlag!=0.
; Mask IRQ only around the paired address/data transaction; retain NMI/audio.
.proc PnMenuInitialHintDispatch
 lda SelectedCharacter
 cmp #18
 bne Native
 lda CrossoverMenuState
 cmp #2
 bne Native
 lda DisableScreenFlag
 beq Native
 lda Mirror_PPUMASK
 and #$18
 bne Native
 lda NmiDisable
 bpl Native
 php
 sei
 lda Mirror_PPUCTRL
 and #$fb
 sta PPUCTRL
 bit PPUSTATUS
 lda #$23
 sta PPUADDR
 lda #$46
 sta PPUADDR
 ldy #0
Copy:
 lda QueueVariantHint::ProtoHint,y
 sta PPUDATA
 iny
 cpy #20
 bne Copy
 lda Mirror_PPUCTRL
 sta PPUCTRL
 plp
 rts
Native:
 lda CrossoverMenuPressed
 jmp PnMenuVariantHintGate+3
.endproc
.popseg
.endif
'''


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--parent',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--compiler',type=Path,default=ROOT/'tools/Windows/cc65/bin/cl65.exe');a=p.parse_args();assert sha(a.parent/'candidate.nes')=='636f2b7e2cf296f5b893fd448c8e4a47b3024fbf955980e80f134bfa33262707';assert not a.output.resolve().is_relative_to(ROOT)
 a.output.mkdir(parents=True,exist_ok=False);src=a.output/'source';shutil.copytree(a.parent/'source',src);f=src/'src/character_select.s';text=f.read_text();old='.proc PnMenuVariantHintGate\n lda CrossoverMenuPressed\n';assert text.count(old)==1;f.write_text(text.replace(old,'.proc PnMenuVariantHintGate\n jmp PnMenuInitialHintDispatch\n')+TAIL,encoding='utf-8')
 r=subprocess.run([sys.executable,'-B',str(src/'tools/build_mmc5_expanded.py'),'--workspace',str(src),'--compiler',str(a.compiler),'--output',str(a.output/'candidate.nes')],capture_output=True,text=True);(a.output/'build-host.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout+r.stderr
 b=scoped_load(a.parent/'candidate.nes');n=scoped_load(a.output/'candidate.nes');hook=location(b,'PnMenuVariantHintGate');start=location(n,'PnMenuInitialHintDispatch');s=n['syms']['PnMenuInitialHintDispatch'];size=int(s['size'],0);assert b['raw'][start:start+size]==b'\xff'*size
 for name,s in b['syms'].items():assert name in n['syms']and s['val']==n['syms'][name]['val'],name
 diff=[i for i,(x,y)in enumerate(zip(b['raw'],n['raw']))if x!=y];assert all(hook<=i<hook+3 or start<=i<start+size for i in diff);assert all((i-16)//8192==66 for i in diff)
 assert b['raw'][16+1048576:]==n['raw'][16+1048576:]
 patch=''.join(difflib.unified_diff((a.parent/'source/src/character_select.s').read_text().splitlines(keepends=True),f.read_text().splitlines(keepends=True),fromfile='a/src/character_select.s',tofile='b/src/character_select.s'));(a.output/'sourcepatch.patch').write_text(patch)
 q=dict(prepared=True,native_run=False,adopted=False,CPU_passed=False,parent_ROM_sha256=sha(a.parent/'candidate.nes'),candidate_ROM_sha256=sha(a.output/'candidate.nes'),all_parent_symbols_exact=len(b['syms']),CHR_exact=True,delta_bytes=len(diff),delta_banks=dict(collections.Counter((i-16)//8192 for i in diff)),hook=dict(offset=hook,before=b['raw'][hook:hook+3].hex(),after=n['raw'][hook:hook+3].hex()),helper=dict(bank=66,address=address(n,'PnMenuInitialHintDispatch'),offset=start,bytes=size,old_FF=True),changed_source={'src/character_select.s':sha(f)},tool_sha256=sha(Path(__file__)),patch_sha256=sha(a.output/'sourcepatch.patch'),limits='Private source-only initial publication extension. Actual exclusive render-off/NmiDisable guard, full PPU latch/control/scroll/queue continuation and interrupt boundaries require proof. Live636f gate/fallback code retained; no native grant/adoption.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
