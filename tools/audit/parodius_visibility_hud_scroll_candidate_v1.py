"""Build an additive private capture-scroll successor without moving v11 PCs."""
from pathlib import Path
import argparse,difflib,hashlib,json,shutil,subprocess,sys
from parodius_visibility_hud_candidate_v1 import edit
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
SHA='64f454a248785ff4c53bd0d52158fd2cf5389de38e5c35a888c3e6a6ed982362'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--parent',type=Path,required=True);p.add_argument('--compiler',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert sha(a.parent/'candidate.nes')==SHA;a.output.mkdir(parents=True,exist_ok=False);source=a.output/'source';shutil.copytree(a.parent/'source',source);shutil.copy2(Path(__file__),a.output/Path(__file__).name)
 edit(source/'src/nmi_vram_fast.s',' ldx #32\n cpx #32\n jmp PnPaletteScreenUpdate::Copy+11 ; after the unchanged old BNE',' jmp FastNmiPaletteScrollRestore\n .res 4,$ea ; retain every existing private entry PC')
 f=source/'src/nmi_vram_fast.s';f.write_bytes(f.read_bytes()+b'''\n; Capture necessarily changes t with PPUADDR3F00. Restore the native\n; UpdateScreen coarse/fine scroll0. The following old MirrorPPUCTRL store\n; restores its nametable bits; the regular NMI later applies its HUD AND#FC.\n.pushseg\n.segment "NMI_VRAM_SCROLL"\n.proc FastNmiPaletteScrollRestore\n ldx #0\n stx PPUSCROLL\n stx PPUSCROLL\n ldx #32\n cpx #32\n jmp PnPaletteScreenUpdate::Copy+11\n.endproc\n.popseg\n''')
 edit(source/'smb1base-mmc5-expanded.cfg','    PN_HUD_QUEUE:load=X5_NEW_74,type=ro;','    PN_HUD_QUEUE:load=X5_NEW_74,type=ro;\n    NMI_VRAM_SCROLL:load=X5_NEW_74,type=ro;')
 cmd=[sys.executable,'-B',str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),'--source-overlay',str(source),'--compiler',str(a.compiler),'--output',str(a.output/'candidate.nes')];r=subprocess.run(cmd,capture_output=True,text=True);(a.output/'host-build.log').write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stdout+r.stderr
 old=scoped_load(a.parent/'candidate.nes');new=scoped_load(a.output/'candidate.nes');assert all(n in new['syms']and address(old,n)==address(new,n)for n in old['syms'])
 at=location(old,'FastNmiPaletteCapture')+192;g=next(v for v in new['segs'].values()if v['name']=='"NMI_VRAM_SCROLL"');tail=int(g['ooffs'],0);size=int(g['size'],0);assert size==15 and old['raw'][tail:tail+size]==bytes([255])*size;diff=[i for i,(u,v)in enumerate(zip(old['raw'],new['raw']))if u!=v];assert all(at<=i<at+7 or tail<=i<tail+15 for i in diff)and all((i-16)//8192==116 for i in diff);assert old['raw'][1048592:]==new['raw'][1048592:]
 patch=[]
 for rel in ['src/nmi_vram_fast.s','smb1base-mmc5-expanded.cfg']:
  patch+=difflib.unified_diff((a.parent/'source'/rel).read_text().splitlines(keepends=True),(source/rel).read_text().splitlines(keepends=True),fromfile='a/'+rel,tofile='b/'+rel)
 (a.output/'sourcepatch.patch').write_text(''.join(patch),encoding='utf-8');q=dict(prepared=True,CPU_passed=False,native_run=False,adopted=False,goal_complete=False,parent_ROM_sha256=SHA,candidate_ROM_sha256=sha(a.output/'candidate.nes'),all_v11_symbols_exact=True,v11_symbols=len(old['syms']),CHR_exact=True,ROM_delta_bytes=len(diff),delta_bank=116,replaced_tail=dict(offset=at,bytes=7,before=old['raw'][at:at+7].hex(),after=new['raw'][at:at+7].hex()),new_tail=dict(offset=tail,bytes=size),capture_only_extra_cycles=13,changed_source={n:sha(source/n)for n in ['src/nmi_vram_fast.s','smb1base-mmc5-expanded.cfg']},patch_sha256=sha(a.output/'sourcepatch.patch'),tool_sha256=sha(Path(__file__)),limits='Private additive scroll restoration only. Intended two PPUSCROLL0 writes change capture I/O and t/fineX state; all old exact-I/O receipts remain historical. Native qualification remains required.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(q,indent=2))
if __name__=='__main__':main()
