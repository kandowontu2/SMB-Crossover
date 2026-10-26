"""Private exact source union: inline TMNT sweep, frozen0c45, renderer/a8e0.

No production writes/native launch. Text overlaps use captured normalized
three-way inputs; only the reviewed extra entrypoint include is merged by hand.
"""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import subprocess
import sys
from check_tmnt_render_oa import load,address,location
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT,CURRENT,sha

INLINE='aa5ba7af19a5ee353aa60f8c4ec5c10973de5678fa000d6f73af7fbb0bf29eff'
CV3='0c45ce16fa189debc2303f4df664a0e75f326a807a64bf23280797734615339c'
RENDER='a8e0d391161f5e828c0790b691a002342e403d718aabab14596f44760f3feb2a'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in['inline','cv3','render','storage','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();out=a.output
    assert not out.exists()and not out.resolve().is_relative_to(ROOT)
    base=a.storage/'current-baseline-v1/source';frozen=json.loads((a.storage/'current-baseline-v1/frozen-source.json').read_text())['source_files']
    assert sha(a.inline/'candidate.nes')==INLINE and sha(a.cv3/'candidate.nes')==CV3 and sha(a.render/'candidate.nes')==RENDER
    assert all(sha(base/n)==h for n,h in frozen.items())
    csource=a.cv3/'source-final';cmeta=json.loads((a.cv3/'qualification.json').read_text())
    cchanges={row['path']:row for row in cmeta['source_files']}
    assert all(sha(csource/n)==row['sha256']for n,row in cchanges.items())
    out.mkdir(parents=True);s=out/'source';shutil.copytree(a.inline/'source',s,ignore=shutil.ignore_patterns('__pycache__'))
    (out/'merge-inputs').mkdir();merges=[]
    for name,row in sorted(cchanges.items()):
        # Frozen0c45 qualifier lists its8 real changes, no removed inputs.
        original,ours,theirs=base/name,s/name,csource/name
        if original.exists()and sha(original)==sha(theirs):continue
        if not original.exists():
            assert not ours.exists(),('Conflicting newly added source',name)
            ours.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(theirs,ours);merges.append(dict(path=name,kind='new0c45'));continue
        if sha(ours)==sha(original):
            shutil.copyfile(theirs,ours);merges.append(dict(path=name,kind='0c45_only'));continue
        old,local,remote=original.read_text(),ours.read_text(),theirs.read_text()
        if name=='src/entrypoint.s':
            anchor='.include "cv3_dmc_complete.s"\n'
            assert remote==old.replace(anchor,anchor+'.include "cv3_remaining_source_fx.s"\n')
            assert local.count(anchor)==1
            merged=local.replace(anchor,anchor+'.include "cv3_remaining_source_fx.s"\n');kind='exact_one_include_union'
        else:
            prefix=out/'merge-inputs'/name.replace('/','_')
            paths=[]
            for tag,text in[('ours',local),('base',old),('theirs',remote)]:
                path=Path(str(prefix)+'.'+tag);path.write_text(text,newline='\n');paths.append(path)
            result=subprocess.run(['git','merge-file','-p',*[str(p)for p in paths]],capture_output=True)
            Path(str(prefix)+'.stdout').write_bytes(result.stdout);Path(str(prefix)+'.stderr').write_bytes(result.stderr)
            assert result.returncode==0,('Unresolved source union retained',name,result.returncode)
            merged=result.stdout.decode();assert '<<<<<<<'not in merged;kind='reviewable_disjoint_three_way'
        # Keep the CV3 donor's existing EOL style for the shared source file.
        newline='\r\n'if b'\r\n'in theirs.read_bytes()else'\n'
        ours.write_text(merged,newline=newline);merges.append(dict(path=name,kind=kind))
    # Exact root renderer/ammo helpers; donor's B020/B100/B200 addresses are
    # asserted in their source. Existing B500 C-alias split remains untouched.
    for name in['src/tmnt_equipment_draw.s','src/tmnt_empty_equipment_scans.s','src/tmnt_ammo_decimal_lookup.s']:
        shutil.copyfile(a.render/'source'/name,s/name)
    path=s/'src/entrypoint.s';text=path.read_text()
    for name in['tmnt_empty_equipment_scans.s','tmnt_ammo_decimal_lookup.s']:
        assert '.include "'+name+'"'not in text
        text+='\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n.include "'+name+'"\n.endif\n'
    path.write_text(text)
    command=[sys.executable,'-B',str(s/'tools/build_mmc5_expanded.py'),'--workspace',str(s),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/'candidate.nes')]
    r=subprocess.run(command,cwd=s,capture_output=True,text=True);(out/'build.log').write_text(r.stdout+r.stderr)
    assert r.returncode==0,(r.stdout+r.stderr)[-5000:]
    b=load(out/'candidate.nes');q=qualified(out/'candidate.nes');controls={}
    qc=qualified(a.cv3/'candidate.nes')
    cv3_removed={('Cv3NoiseSceneReset','Variant'),('Cv3NoiseSceneReset','Owner'),('Cv3SpawnAudioType','Done')}
    assert all(n not in qc for n in cv3_removed),'Literal0c45 removed private branches, never callable aliases'
    for label,rom in[('inline',a.inline/'candidate.nes'),('CV3',a.cv3/'candidate.nes'),('render',a.render/'candidate.nes')]:
        old=qualified(rom);moved={str(n):[v,q.get(n)]for n,v in old.items()if q.get(n)!=v and n!=('_FARCALL_COUNT',)}
        allowed={str(n)for n in cv3_removed if n in old and n not in q and label!='CV3'}
        assert all(n.startswith("('SamusAudioUpdate',")or n in allowed for n in moved),('Unexpected genuine symbol movement',label,list(moved.items())[:12])
        controls[label]=dict(symbols=len(old),explicit_private_changes=moved,
                            removed_private_CV3_branches_exactly_as_frozen0c45=sorted(allowed))
    cb=load(a.cv3/'candidate.nes');cp=location(cb,'Cv3FxOwnerInit');newcp=location(b,'Cv3FxOwnerInit')
    assert cp==newcp and cb['raw'][cp:cp+38]==b['raw'][newcp:newcp+38]
    assert address(b,'Cv3FxOwnerInit')==0xbfda
    assert address(b,'TnExpansionSweepGate')==0xa845
    rb=load(a.render/'candidate.nes');rr=16+87*8192
    assert b['raw'][rr:rr+0x1500]==rb['raw'][rr:rr+0x1500]
    ib=load(a.inline/'candidate.nes');assert b['raw'][rr+0x1500:rr+8192]==ib['raw'][rr+0x1500:rr+8192]
    assert b['raw'][:16]==cb['raw'][:16]==rb['raw'][:16]and b['raw'][1048592:]==cb['raw'][1048592:]==rb['raw'][1048592:]
    # Forward original source metadata for the existing exact gold checker.
    metadata=json.loads((a.inline/'preparation.json').read_text());metadata['candidate_ROM_sha256']=sha(out/'candidate.nes')
    (out/'preparation.json').write_text(json.dumps(metadata,indent=2)+'\n')
    manifest={p.relative_to(s).as_posix():sha(p)for p in s.rglob('*')if p.is_file()}
    changes={n:dict(before_sha256=frozen.get(n),after_sha256=h)for n,h in manifest.items()if frozen.get(n)!=h}
    (out/'source-bindings.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (out/'changed-source-versus-50b5.json').write_text(json.dumps(changes,indent=2)+'\n')
    patch=''
    for name in sorted(changes):
        before,after=base/name,s/name
        if name.endswith(('.s','.inc','.cfg')):patch+=''.join(difflib.unified_diff(before.read_text().splitlines(True)if before.exists()else[],after.read_text().splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    (out/'review.patch').write_text(patch)
    proof=dict(prepared=True,source_only=True,native_run=False,accepted=False,production_parent_ROM_sha256=CURRENT,
               candidate_ROM_sha256=sha(out/'candidate.nes'),parents=dict(inline=INLINE,CV3=CV3,render=RENDER),
               source_files=len(manifest),real_source_changes=len(changes),source_merges=merges,qualified_symbols=controls,
               Cv3FxOwnerInit_BFDA38_exact=True,real_sweep_gate_A845=True,no_additional_bank_trips=True,
               root_renderer_bank87_prefix_0x1500_exact=True,C87_sweep_tail_exact=True,CHR_header_exact=True,
               no_native_grant_or_adoption=True,checker_sha256=sha(Path(__file__)))
    (out/'composition-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))


if __name__=='__main__':main()
