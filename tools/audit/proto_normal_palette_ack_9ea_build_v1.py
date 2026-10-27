"""One private three-byte normal Proto palette-cache experiment; no native."""
from pathlib import Path
import configparser,difflib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];B=R/'build';sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from current_mega_arsenal_prepare_v1 import EXPECTED,sha
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare

def main():
    base=B/'bill_early_cache.nes';assert sha(base)==EXPECTED;old=scoped_load(base)
    source=R/'src/proto_palette_ack.s';text=source.read_text()
    needle=' lda #1\n sta SsLastPalette\nRestore:\n';assert text.count(needle)==1
    changed=text.replace(needle,' lda #1\n sta SsLastPalette\n sta MmLastPalette             ; Same successfully queued normal body colors.\nRestore:\n')
    name='proto_normal_palette_ack_9ea';overlay=B/(name+'_source.s');ep=B/(name+'_entrypoint.s');mainc=B/(name+'_main.c');out=B/(name+'.nes')
    assert not any(p.exists() for p in [overlay,ep,mainc,out])
    at=location(old,'ProtoFixAndAcknowledgePalette');size=int(old['syms']['ProtoFixAndAcknowledgePalette']['size'],0)
    assert (at-16)//8192==66 and address(old,'ProtoFixAndAcknowledgePalette')==0xbe40
    assert size+3<=192 and old['raw'][at+size:at+size+3]==b'\xff'*3
    overlay.write_text(changed,newline='\n')
    raw=(R/'src/entrypoint.s').read_bytes();token=b'.include "proto_palette_ack.s"';assert raw.count(token)==1
    ep.write_bytes(raw.replace(token,b'.include "'+overlay.name.encode()+b'"'));mainc.write_bytes((R/'src/main.c').read_bytes())
    config=configparser.ConfigParser();config.optionxform=str;config.read(R/'build_options.ini');defs={k:v for s in config.values() for k,v in s.items()}
    defs.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
    cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(R/'smb1base-mmc5-expanded.cfg'),'--ld-args','--dbgfile,'+str(out.with_suffix('.dbg')),'--include-dir',str(R),'--asm-include-dir',str(B),'--asm-include-dir',str(R/'src'),'--asm-include-dir',str(R),'--bin-include-dir',str(R),'-m',str(out.with_suffix('.map')),'-Ln',str(out.with_suffix('.lbl')),'-o',str(out)]
    for k,v in defs.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
    cmd +=[str(mainc),str(ep)];run=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
    out.with_suffix('.build.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stdout+run.stderr
    prepare(R,out);new=scoped_load(out);diff=[i for i,(x,y) in enumerate(zip(old['raw'],new['raw'])) if x!=y]
    assert diff and all(at<=i<at+size+3 for i in diff)
    assert new['raw'][:at]==old['raw'][:at] and new['raw'][at+size+3:]==old['raw'][at+size+3:]
    moved={n:[x.get('val'),new['syms'].get(n,{}).get('val')] for n,x in old['syms'].items() if x.get('val')!=new['syms'].get(n,{}).get('val')}
    genuine={n:v for n,v in moved.items() if not n.split('::')[-1].startswith('LOCAL-MACRO_SYMBOL-')}
    assert set(genuine)=={'ProtoFixAndAcknowledgePalette::Restore'} and address(new,'ProtoFixAndAcknowledgePalette::Restore')==address(old,'ProtoFixAndAcknowledgePalette::Restore')+3,genuine
    patch=B/(name+'.patch');patch.write_text(''.join(difflib.unified_diff(text.splitlines(True),changed.splitlines(True),fromfile='current9ea/src/proto_palette_ack.s',tofile='private/src/proto_palette_ack.s')),newline='\n')
    receipt=dict(source_only=True,native_run=False,passed=True,parent_sha256=EXPECTED,candidate_sha256=sha(out),candidate=str(out),
        changed_bytes=len(diff),changed_bank=66,changed_span=[at,at+size+3],old_helper_bytes=size,new_helper_bytes=size+3,
        declared_allocation='Existing66:BE40..BEFF192B; next3bytes verifiedFF, no cfg allocation/newRAM/sharedNMI work.',
        genuine_private_label_moves=genuine,all_other_qualified_addresses_exact=True,header_CHR_all_other_ROM_bytes_exact=True,
        intentional='On existing proven successful full normal Proto palette only, also acknowledge existing MmLastPalette1. Caller AXYP restored by unchanged suffix; new STA adds4foregroundCPU cycles.',
        source_overlay=str(overlay),patch=str(patch),command=cmd,
        bindings={str(p):sha(p) for p in [Path(__file__),base,base.with_suffix('.dbg'),source,R/'src/entrypoint.s',R/'src/main.c',R/'smb1base-mmc5-expanded.cfg',R/'build_options.ini',overlay,ep,mainc,patch]})
    proof=B/(name+'_build.json');proof.write_text(json.dumps(receipt,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(candidate_sha256=sha(out),changed_bytes=len(diff),helper_size=[size,size+3],proof=str(proof),proof_sha256=sha(proof))))

if __name__=='__main__':main()
