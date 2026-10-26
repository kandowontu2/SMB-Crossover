"""Exact unused-core/source ownership/storage/canonical/ordinary controls."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE=D/'smb3-assets-current3cee-v2'
TRACE=D/'smb3-original-music-closure-v3'
NSF=R/'reference/new-roster-audio/mario3/crossover-named.nsf'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--packet',type=Path,required=True);a=p.parse_args();out=a.packet/'controls-v1';out.mkdir(exist_ok=False)
    old,new=scoped_load(BASE/'candidate.nes'),scoped_load(a.packet/'candidate.nes')
    assert sha(BASE/'candidate.nes')=='b86bfa95032a54837fbd1802d60659aaca9dfa8c55a713cc8a58a58ef0a594f6'
    assert sha(a.packet/'candidate.nes')=='a4be8e02de0f8c0c43e5a7c94e4719e8b62c2ae80c1b1769978b06e73f2cac98'
    retained=0
    for n,s in old['syms'].items():
        assert n in new['syms']and new['syms'][n]['val']==s['val'],('Old symbol changed',n,s,new['syms'].get(n));retained+=1
    allowed={38:[(0xbe8,0xbe8+address(new,'B3CoreEnd')-address(new,'B3CoreStart'))],86:[(0x800,0x800+address(new,'B3ColdEnd')-address(new,'B3ColdStart'))],70:[(0,8192)],97:[(0,8192)]}
    pagebanks=[78,86,90,93,95,96,98,118,119]
    for bank in pagebanks:allowed.setdefault(bank,[]).append((4096,8192))
    changes={}
    for bank in range(128):
        at=16+bank*8192;diff=[i for i in range(8192)if old['raw'][at+i]!=new['raw'][at+i]]
        if diff:
            assert all(any(lo<=i<hi for lo,hi in allowed.get(bank,[]))for i in diff),('Unexpected ROM difference',bank)
            changes[bank]=len(diff)
    for bank,rr in allowed.items():
        for lo,hi in rr:
            assert old['raw'][16+bank*8192+lo:16+bank*8192+hi]==bytes([255])*(hi-lo),(bank,lo,hi)
    image=NSF.read_bytes()[128:];recovered=b''.join(new['raw'][16+bank*8192+4096:16+(bank+1)*8192]for bank in pagebanks)
    assert image==recovered and len(image)==36864
    reserved=[62,63,94,99,123,124,125,126,127]
    for bank in reserved:assert old['raw'][16+bank*8192:16+(bank+1)*8192]==new['raw'][16+bank*8192:16+(bank+1)*8192],bank
    assert new['raw'][16+128*8192:]==old['raw'][16+128*8192:]
    assert new['raw'][16+78*8192:16+78*8192+4096]==old['raw'][16+78*8192:16+78*8192+4096]
    fixed=old['raw'][16+127*8192:16+128*8192];clones=[]
    for bank in [70,97]:
        clone=new['raw'][16+bank*8192:16+(bank+1)*8192]
        assert all(x==y or 0x1140<=i<0x1fc1 for i,(x,y)in enumerate(zip(fixed,clone))),bank
        clones.append(dict(bank=bank,bytes=8192,sha256=hashlib.sha256(clone).hexdigest(),all_fixed_code_vectors_exact=True))
    closure=json.loads((TRACE/'dynamic-closure.json').read_text())
    sourcecells={i for key in ['RAM_reads','RAM_writes']for lo,hi in closure[key]for i in range(lo,hi+1)}
    work=set(range(address(new,'B3VirtualMaps'),address(new,'B3WorkEnd')))
    assert not work&sourcecells and not{3,4,address(new,'CurrentBank'),address(new,'CurrentBankC')}&sourcecells
    # No runtime hook points at the new standalone entries: every existing
    # occupied code byte remains identical. The only source edits are cfg and
    # appended definitions/includes, with no initializer or active call added.
    parentmanifest=json.loads((BASE/'source-manifest.json').read_text());changed=[]
    for n,h in parentmanifest.items():
        if sha(a.packet/'source'/n)!=h:changed.append(n)
    assert set(changed)=={'src/entrypoint.s','smb1base-mmc5-expanded.cfg'},changed
    builds=[]
    for mode in ['canonical','mmc3','mmc5']:
        rom=out/(mode+'.nes');cmd=[sys.executable,str(R/'tools/build_mmc5_expanded.py'),'--source-overlay',str(a.packet/'source'),'--output',str(rom)]
        if mode!='canonical':cmd+=['--flag-off',mode]
        run=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(out/(mode+'.launch.json')).write_text(json.dumps(dict(command=cmd,returncode=run.returncode,stdout=run.stdout,stderr=run.stderr),indent=2)+'\n')
        assert run.returncode==0,(mode,run.stdout,run.stderr)
        expected=sha(a.packet/'candidate.nes')if mode=='canonical'else{'mmc3':'d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb','mmc5':'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'}[mode]
        assert sha(rom)==expected,(mode,sha(rom),expected)
        builds.append(dict(mode=mode,ROM_sha256=sha(rom),exact=True))
    result=dict(passed=True,source_only=True,native_run=False,active_host_driver=False,ROM_sha256=sha(a.packet/'candidate.nes'),parent_ROM_sha256=sha(BASE/'candidate.nes'),
                retained_old_qualified_symbols=retained,exact_code_changes_only_in_genuine_previously_free_extents=True,changed_PRG_bytes=changes,
                complete_original_payload_bytes=36864,payload_sha256=hashlib.sha256(recovered).hexdigest(),physical_source_page_banks=pagebanks,
                reserved_banks_exact=reserved,held_Chip_A78_prefix_and_adapter_span_exact=True,work_range=[min(work),max(work)+1],original_observed_source_RAM_disjoint_from_work=True,
                borrowed_pointer_cells=[3,4],cold_pool_current_parent_unallocated_and_FF=True,fixed_E_clones=clones,CHR_exact=True,
                existing_source_changes=changed,builds=builds,checker_sha256=sha(__file__),
                limits='Exact source/storage/build accounting and fixed12 source RAM separation. CPU call qualification separate; no runtime host-state ownership, AudioUpdate, native cadence, DMC hardware clocks or all71 songs claim.')
    (out/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
