"""Private canonical/ordinary targets and explicit new storage/old symbol contract."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,traceback
from check_tmnt_audio_fallback_oc import qualified
from check_tmnt_render_oa import address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load

R=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for n in['parent','candidate','source','output']:ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    try:
        manifest=json.loads((a.source.parent/'source-manifest.json').read_text())
        for rel,h in manifest.items():assert sha(a.source/rel)==h,(rel,h)
        rows=[]
        for target,expected in [('expanded',sha(a.candidate)),('mmc3','d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),('mmc5','f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]:
            out=a.output/(target+'.nes')
            cmd=[sys.executable,'-B',str(a.source/'tools/build_mmc5_expanded.py'),'--workspace',str(a.source),'--compiler',str(R/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out)]
            if target!='expanded':cmd+=['--flag-off',target]
            z=subprocess.run(cmd,cwd=a.source,capture_output=True,text=True)
            row=dict(target=target,command=cmd,exit=z.returncode,stdout=z.stdout,stderr=z.stderr)
            rows.append(row);(a.output/'launches.json').write_text(json.dumps(rows,indent=2)+'\n')
            assert z.returncode==0,z.stdout+z.stderr
            assert sha(out)==expected,(target,sha(out),expected)
            row['SHA256']=sha(out)
        for rel,h in manifest.items():assert sha(a.source/rel)==h,('Build mutated source',rel)
        old,new=[scoped_load(p)for p in[a.parent,a.candidate]]
        oldq,newq=[qualified(p)for p in[a.parent,a.candidate]]
        moves=[dict(symbol=list(n),old=v,new=newq.get(n))for n,v in oldq.items()if newq.get(n)!=v]
        RAM=[dict(name=list(n),old=v,new=newq.get(n))for n,v in oldq.items()if v<0x8000 and n!=('_FARCALL_COUNT',) and newq.get(n)!=v]
        assert not RAM,RAM
        assert newq[("_FARCALL_COUNT",)]==oldq[("_FARCALL_COUNT",)]+1
        raw,after=old['raw'],new['raw']
        assert raw[:16]==after[:16]and raw[16+128*8192:]==after[16+128*8192:]
        delta={i:sum(x!=y for x,y in zip(raw[16+i*8192:16+(i+1)*8192],after[16+i*8192:16+(i+1)*8192]))for i in range(128)}
        delta={i:n for i,n in delta.items()if n};assert delta=={4:542,66:185},delta
        extents={}
        for name in['MM_BODY_PRIORITY_GATE','MM_PUBLICATION_COLD']:
            seg=[s for s in new['segs'].values()if s['name'].strip('"')==name];assert len(seg)==1;seg=seg[0]
            pos,size,start=[int(seg[k],0)for k in['ooffs','size','start']]
            assert raw[pos:pos+size]==bytes([255])*size,(name,pos,size)
            extents[name]=dict(bank=(pos-16)//8192,start=start,size=size,end=start+size,original_fill255=True)
        assert address(new,'MmPublicationState')==0x5ff8
        assert address(old,'WorldFirebarAdmissionDone')==address(new,'WorldFirebarAdmissionDone')
        for symbol in['NonMaskableInterrupt','OAMandReadJoypad','NmiBankCRestore','NmiBankCRestoreDone','AudioUpdate','ProtoNmiAudioCore','ProtoMenuPrepare','MoveAllSpritesOffscreen','OAMClear','DrawMetasprite','MetaspriteRenderLoop']:
            assert oldq[(symbol,)]==newq[(symbol,)],symbol
        (a.output/'genuine-symbol-moves.json').write_text(json.dumps(moves,indent=2)+'\n')
        proof=dict(passed=True,source_only=True,native_run=False,installed=False,parent_ROM_sha256=sha(a.parent),candidate_ROM_sha256=sha(a.candidate),canonical_build_exact=True,ordinary_targets_exact=True,
                   ordinary_hashes={r['target']:r['SHA256']for r in rows if r['target']!='expanded'},source_manifest_unchanged=True,
                   changed_PRG_bytes=delta,all_other_PRG_CHR_header_exact=True,old_RAM_symbols_exact=True,assembler_only_FARCALL_COUNT_delta=1,new_lifecycle_byte=0x5ff8,declared_new_code_extents=extents,
                   genuine_symbol_moves=moves,removed_private_core_labels='Only real Original/Restore private branches moved with actual Proto core into MmPublicationAudioCore; no fake aliases. Other DrawAll private movement is explicitly catalogued.',
                   limits='Build/source/control evidence only. Positive owned render/NMI and common reset costs require native timing/actual visibility qualification.',tool_sha256=sha(__file__))
        (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
    except BaseException as e:
        (a.output/'failure.json').write_text(json.dumps(dict(passed=False,error=repr(e),traceback=traceback.format_exc()),indent=2)+'\n');(a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes());raise

if __name__=='__main__':main()
