"""Same-span private SMB3 injury-clock owner repair; never installs or runs Mesen."""
from pathlib import Path
import configparser,difflib,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];B=R/'build';sys.path.insert(0,str(R/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
PARENT=B/'kirby-mike-polish-production.nes'
EXPECTED='5a0a37a97e95ce3c1086f91f6000ad0157bb477f923027d39f0342d9389e6db2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n',newline='\n')

def main():
    assert sha(PARENT)==EXPECTED
    leaf=R/'src/smb3_mario_dispatch.s';old=leaf.read_text()
    a=' lda #0\n sta GuestHurtKind\n sta GuestHurtTicks\n sta TimerControl\n sta PlayerChangeSizeFlag\n sta M3PaletteValid\n'
    z=''' ; A genuine nonzero owner admits GuestInjuryTick on subsequent Main calls.
 ; M3ClearSuitState above already invalidated M3PaletteValid. Reuse that
 ; redundant store's space; the same17-byte tail still takes22 CPU cycles.
 lda #17
 sta GuestHurtKind
 lda #0
 sta GuestHurtTicks
 sta TimerControl
 sta PlayerChangeSizeFlag
 nop
'''
    assert old.count(a)==1
    changed=B/'current_smb3_timer_dispatch.s';changed.write_text(old.replace(a,z),newline='\n')
    original=(R/'src/entrypoint.s').read_text();needle='.include "smb3_mario_dispatch.s"';assert original.count(needle)==1
    ep=B/'current_smb3_timer_entrypoint.s';ep.write_text(original.replace(needle,'.include "'+changed.name+'"'),newline='\n')
    control_ep=B/'current_smb3_timer_control_entrypoint.s';control_ep.write_text(original,newline='\n')
    c=B/'current_smb3_timer_main.c';c.write_bytes((R/'src/main.c').read_bytes())
    def build(mapper=None,control=False):
        cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read(R/'build_options.ini')
        defs={k:v for s in cfg.values()for k,v in s.items()};defs.update(MAPPER_MMC3=str(int(mapper=='mmc3')),MAPPER_MMC5=str(int(mapper!='mmc3')),ENABLE_CROSSOVER='1')
        if mapper:defs.pop('ENABLE_MMC5_EXPANDED',None)
        else:defs['ENABLE_MMC5_EXPANDED']='1'
        out=B/('current_smb3_timer'+('_'+mapper if mapper else'')+('_control'if control else'')+'.nes')
        cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(R/('smb1base.cfg'if mapper else'smb1base-mmc5-expanded.cfg')),
            '--ld-args','--dbgfile,'+str(out.with_suffix('.dbg')),'--include-dir',str(R),'--asm-include-dir',str(B),'--asm-include-dir',str(R/'src'),'--asm-include-dir',str(R),'--bin-include-dir',str(R),'-m',str(out.with_suffix('.map')),'-Ln',str(out.with_suffix('.lbl')),'-o',str(out)]
        for k,v in defs.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
        cmd +=[str(c),str(control_ep if control else ep)]
        r=subprocess.run(cmd,cwd=R,capture_output=True,text=True);out.with_suffix('.build.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout+r.stderr
        if not mapper:
            sys.path.insert(0,str(R/'tools'));from prepare_cv3_dmc_mirror import prepare;prepare(R,out)
        return out,cmd
    fresh,_=build(control=True);assert sha(fresh)==EXPECTED,'Current source must reproduce the explicit frozen5a parent'
    out,cmd=build();b=scoped_load(PARENT);nb=scoped_load(out);raw=out.read_bytes()
    diffs=[i for i,(x,y)in enumerate(zip(b['raw'],raw))if x!=y];assert diffs
    bank=(location(b,'M3Injury')-16)//8192
    assert all((i-16)//8192==bank for i in diffs)
    at=location(b,'M3Injury');end=at+int(b['syms']['M3Injury']['size'],0)
    assert all(at<=i<end for i in diffs)
    moved=[]
    for n in b['syms']:
        if n in nb['syms']and'seg'in b['syms'][n]and'seg'in nb['syms'][n]:
            if address(b,n)!=address(nb,n):moved.append(n)
            elif'ooffs'in b['segs'][b['syms'][n]['seg']]and'ooffs'in nb['segs'][nb['syms'][n]['seg']]and location(b,n)!=location(nb,n):moved.append(n)
    assert not moved,moved
    assert raw[:16]==b['raw'][:16]and raw[16+128*8192:]==b['raw'][16+128*8192:]
    ordinary={}
    for mapper in ('mmc3','mmc5'):
        p,_=build(mapper);q,_=build(mapper,True);assert p.read_bytes()==q.read_bytes();ordinary[mapper]=dict(sha256=sha(p),fresh_control_sha256=sha(q),byte_exact=True)
    patch=B/'current_smb3_timer.patch';patch.write_text(''.join(difflib.unified_diff(old.splitlines(True),changed.read_text().splitlines(True),fromfile='5a/src/smb3_mario_dispatch.s',tofile='private/src/smb3_mario_dispatch.s')),newline='\n')
    put(B/'current_smb3_timer_build.json',dict(passed=True,native_run=False,parent_sha256=EXPECTED,candidate_sha256=sha(out),ROM=str(out),source_leaf=str(changed),source_leaf_sha256=sha(changed),patch_sha256=sha(patch),command=cmd,
        changed_bank=bank,changed_bytes=len(diffs),changed_physical_offsets=[i-16 for i in diffs],all_old_labels_retained=True,CHR_RAM_header_other_banks_exact=True,ordinary=ordinary,
        same_span='17 bytes/22 CPU cycles; redundant PaletteValid0 already performed by M3ClearSuitState is replaced with owned17+zero reload and1NOP. All old executable entry addresses retained. Additional actual shared injury-tick work is intentional and must be measured natively.'))
    print(json.dumps(dict(candidate_sha256=sha(out),changed_bytes=len(diffs),bank=bank,ordinary=ordinary)))

if __name__=='__main__':main()
