"""Private bounded same-ship variant hint reuse; no native or installation."""
from pathlib import Path
from collections import Counter
import argparse,difflib,hashlib,json,shutil,subprocess,sys
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
HELPER='''

.if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5
; Only an already-live ship Select-only toggle can reuse the published hint.
; Initial/rebuilt pages keep DisableScreenFlag set through QueueSelection;
; navigation with any direction retains the original complete hint writer.
; All four ship variants have the identical native ProtoHint20 cells.
.pushseg
.segment "PN_MENU_HINT"
.proc PnMenuVariantHintGate
 lda CrossoverMenuPressed
 cmp #Select_Button
 bne Original
 lda SelectedCharacter
 cmp #18
 bne Original
 lda CrossoverMenuState
 cmp #2
 bne Original
 lda DisableScreenFlag
 bne Original
 rts
Original:
 ldx VRAM_Buffer1_Offset
 jmp QueueVariantHint+3
.endproc
.popseg
.endif
'''


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--parent',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--compiler',type=Path,default=ROOT/'tools/Windows/cc65/bin/cl65.exe');a=p.parse_args();assert sha(a.parent/'candidate.nes')=='df5154bc035ba2c392bb8d34068897a2bccf7a78a6f4554bd6790d31a586c357';assert not a.output.resolve().is_relative_to(ROOT)
 a.output.mkdir(parents=True,exist_ok=False);src=a.output/'source';shutil.copytree(a.parent/'source',src)
 f=src/'src/character_select.s';text=f.read_text();old='.proc QueueVariantHint\n  ldx VRAM_Buffer1_Offset\n';assert text.count(old)==1
 text=text.replace(old,'.proc QueueVariantHint\n.if ::ENABLE_MMC5_EXPANDED && ::MAPPER_MMC5\n  jmp PnMenuVariantHintGate\n.else\n  ldx VRAM_Buffer1_Offset\n.endif\n');f.write_text(text+HELPER,encoding='utf-8')
 f=src/'smb1base-mmc5-expanded.cfg';text=f.read_text();old='    INVENTORY_ITEM_RETURN: load=X5_NEW_42,type=ro,optional=yes;';assert text.count(old)==1;text=text.replace(old,old+'\n    PN_MENU_HINT: load=X5_NEW_42,type=ro,optional=yes;');f.write_text(text,encoding='utf-8')
 cmd=[sys.executable,'-B',str(src/'tools/build_mmc5_expanded.py'),'--workspace',str(src),'--source-overlay',str(src),'--compiler',str(a.compiler),'--output',str(a.output/'candidate.nes')];r=subprocess.run(cmd,capture_output=True,text=True);(a.output/'build-host.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout+r.stderr
 b=scoped_load(a.parent/'candidate.nes');n=scoped_load(a.output/'candidate.nes');hook=location(b,'QueueVariantHint');start=location(n,'PnMenuVariantHintGate');seg=next(g for g in n['segs'].values()if g['name']=='"PN_MENU_HINT"');size=int(seg['size'],0)
 assert b['raw'][hook]==0xae and n['raw'][hook]==0x4c and b['raw'][start:start+size]==b'\xff'*size
 assert(start-16)//8192==(hook-16)//8192==66
 for name,s in b['syms'].items():
  if s.get('type')=='lab':assert name in n['syms']and address(b,name)==address(n,name),name
 diff=[i for i,(x,y)in enumerate(zip(b['raw'],n['raw']))if x!=y];assert all(hook<=i<hook+3 or start<=i<start+size for i in diff)
 assert b['raw'][16+1048576:]==n['raw'][16+1048576:]
 patch=[]
 for rel in ['src/character_select.s','smb1base-mmc5-expanded.cfg']:patch+=list(difflib.unified_diff((a.parent/'source'/rel).read_text().splitlines(keepends=True),(src/rel).read_text().splitlines(keepends=True),fromfile='a/'+rel,tofile='b/'+rel))
 (a.output/'sourcepatch.patch').write_text(''.join(patch))
 q=dict(prepared=True,native_run=False,adopted=False,CPU_passed=False,parent_ROM_sha256=sha(a.parent/'candidate.nes'),candidate_ROM_sha256=sha(a.output/'candidate.nes'),old_symbols_exact=len(b['syms']),CHR_exact=True,delta_bytes=len(diff),delta_banks=dict(Counter((i-16)//8192 for i in diff)),hook=dict(offset=hook,bytes=3,before=b['raw'][hook:hook+3].hex(),after=n['raw'][hook:hook+3].hex()),helper=dict(bank=66,address=address(n,'PnMenuVariantHintGate'),offset=start,bytes=size,old_FF=True),changed_source={rel:sha(src/rel)for rel in ['src/character_select.s','smb1base-mmc5-expanded.cfg']},tool_sha256=sha(Path(__file__)),patch_sha256=sha(a.output/'sourcepatch.patch'),limits='Private proposal only. Reuses identical already-published20-cell ship hint solely on Select-only menuState2/render-on toggles. Full caller/initialization, final nametable/palette/cursor, queue and NMI budget proofs pending; no native clearance, global timing or adoption.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
