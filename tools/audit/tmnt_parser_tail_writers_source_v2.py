"""Remove only six real source STA adapter call/return pairs in declared FF."""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import subprocess
import sys
from check_tmnt_render_oa import load,address,location
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT,sha,source_data

PARENT='5057b9e78a54d247914bfc506be4462b4a4d4a1fb9f5f598687bcd8268c17f39'
SITES=[(0xac1d,'TnSourceSTA02X',2,True,4),(0xac09,'TnSourceSTA03X',3,True,2),
       (0xaadd,'TnSourceSTA08',8,False,1),(0xb16c,'TnSourceSTA00X',0,True,1),
       (0xb171,'TnSourceSTA01X',1,True,1),(0xaa96,'TnSourceSTA00X',0,True,1)]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in['parent','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();assert sha(a.parent/'candidate.nes')==PARENT
    assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT)
    old=load(a.parent/'candidate.nes');base=16+63*8192
    assert old['raw'][base+0x29e:base+0x300]==bytes([255])*98
    _,memory,cpu,dis,seen,words=source_data();closure=[]
    for pc,helper,offset,indexed,count in SITES:
        origin=pc-0x2000;assert origin in seen
        refs=[]
        for at in seen:
            width,_=dis.instruction_at(at);op,mode=cpu.disassemble[memory[at]];targets=[]
            if mode=='rel':
                rel=memory[at+1];targets=[at+width,at+width+(rel-256 if rel>=128 else rel)]
            elif op in['JSR','JMP']and mode=='abs':targets=[memory[at+1]+256*memory[at+2]]
            elif op not in['RTS','RTI','JMP','BRK']:targets=[at+width]
            refs.extend([at,to]for to in targets if origin<=to<origin+3)
        roots=[at for at in words if origin<=memory[at]+256*memory[at+1]<origin+3]
        assert all(to==origin for at,to in refs)
        assert all(memory[at]+256*memory[at+1]==origin for at in roots)
        leaf=old['raw'][location(old,helper):location(old,helper)+9]
        expected=bytes([0x9d if indexed else 0x8d,(address(old,'GuestNativeApu')+offset)&255,(address(old,'GuestNativeApu')+offset)>>8,0x08,
            0xfe if indexed else 0xee,(address(old,'GuestNativeDirty')+offset)&255,(address(old,'GuestNativeDirty')+offset)>>8,0x28,0x60])
        assert leaf==expected
        assert old['raw'][base+pc-0xa000:base+pc-0xa000+3]==bytes([0x20,address(old,helper)&255,address(old,helper)>>8])
        closure.append(dict(runtime_PC=pc,original_PC=origin,helper=helper,original_leaf_hex=leaf.hex(),
            original_entry_refs=refs,original_pointer_roots=roots,actual_source_tick533_requests=count))
    a.output.mkdir(parents=True);s=a.output/'source';shutil.copytree(a.parent/'source',s,ignore=shutil.ignore_patterns('__pycache__'))
    inc=s/'src/tmnt-native.inc';text=inc.read_text();body=['; Exact original STA replacement body; only adapter JSR/RTS removed.',
        '.pushseg','.segment "TMNT_DURATION_HELPER"']
    for pc,helper,offset,indexed,count in SITES:
        name=f'TnTail{pc:04X}';anchor=f'  .assert *=${pc:04x},lderror,"Original instruction offset {pc-0x2000:04x}"'
        start=text.index(anchor);end=text.index('.endif',start)
        block=text[start:end];oldcall=f'jsr ::{helper}';assert block.count(oldcall)==1
        text=text[:start]+block.replace(oldcall,f'JMP ::{name}')+text[end:]
        suffix=',x'if indexed else''
        body+=['.proc '+name,f' sta a:GuestNativeApu+{offset}{suffix}',' php',f' inc a:GuestNativeDirty+{offset}{suffix}',
            ' plp',f' jmp ${pc+3:04x}','.endproc','.export '+name]
    inc.write_text(text);body+=['.assert TnTailAC1D=$a29e,lderror,"Append only original declared FF"',
        '.assert *<=$a300,lderror,"Keep all original products and stream bytes"','.popseg','']
    (s/'src/tmnt_parser_tail_writers.s').write_text('\n'.join(body))
    p=s/'src/tmnt_audio.s';text=p.read_text();anchor='.include "tmnt_parser_unrolled.s"\n';assert text.count(anchor)==1
    p.write_text(text.replace(anchor,anchor+'.include "tmnt_parser_tail_writers.s"\n'))
    cmd=[sys.executable,'-B',str(s/'tools/build_mmc5_expanded.py'),'--workspace',str(s),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')]
    r=subprocess.run(cmd,cwd=s,capture_output=True,text=True);(a.output/'build.log').write_text(r.stdout+r.stderr)
    assert r.returncode==0,(r.stdout+r.stderr)[-4000:]
    new=load(a.output/'candidate.nes');before=old['raw'];after=new['raw'];bank=lambda raw,n:raw[16+n*8192:16+(n+1)*8192]
    changes={n:sum(x!=y for x,y in zip(bank(before,n),bank(after,n)))for n in range(128)};changes={n:v for n,v in changes.items()if v}
    assert set(changes)=={63}and before[:16]==after[:16]and before[1048592:]==after[1048592:]
    assert qualified(a.parent/'candidate.nes').items()<=qualified(a.output/'candidate.nes').items()
    for i,(pc,helper,offset,indexed,count)in enumerate(SITES):
        name=f'TnTail{pc:04X}';assert address(new,name)==0xa29e+11*i
        leaf=before[location(old,helper):location(old,helper)+8]
        assert after[location(new,name):location(new,name)+11]==leaf+bytes([0x4c,(pc+3)&255,(pc+3)>>8])
        assert after[base+pc-0xa000:base+pc-0xa000+3]==bytes([0x4c,address(new,name)&255,address(new,name)>>8])
    prep=json.loads((a.parent/'preparation.json').read_text());prep['candidate_ROM_sha256']=sha(a.output/'candidate.nes')
    (a.output/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n');manifest={};patch=''
    for n in['src/tmnt-native.inc','src/tmnt_audio.s','src/tmnt_parser_tail_writers.s']:
        p=a.parent/'source'/n;q=s/n;manifest[n]=dict(before_sha256=sha(p)if p.exists()else None,after_sha256=sha(q))
        patch+=''.join(difflib.unified_diff(p.read_text().splitlines(True)if p.exists()else[],q.read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n))
    (a.output/'review.patch').write_text(patch)
    proof=dict(prepared=True,source_only=True,native_run=False,accepted=False,parent_ROM_sha256=PARENT,candidate_ROM_sha256=sha(a.output/'candidate.nes'),
        changed_PRG_bytes=changes,verified_original_declared_FF=[0xa29e,0xa300],new_bytes=66,all_old_qualified_symbols_exact=True,
        source_endpoint_PCs_retained=True,original_STA_raw_mode_unchanged=True,site_closure=closure,source_changes=manifest,checker_sha256=sha(Path(__file__)))
    (a.output/'tail-preparation.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))


if __name__=='__main__':main()

