"""Freeze the source-only Bill HUD component and exact build/control inputs."""
from pathlib import Path
import argparse,ast,json,shutil
from final_bill_lance_hard_gallery_source_v1 import D,ROOT,SHA,PARENT,sha,put


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--public',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);a.public=a.public.resolve();a.public.mkdir(parents=True,exist_ok=False)
    c=a.packet/'controls-v4/controls.json';z=json.loads(c.read_text());layout=json.loads((a.packet/'layout.json').read_text());build=a.packet/'canonical-build-v1/proof.json'
    target='9d296d337fc24e9b09b17043babec911c3134f60256636a7a285b39d56afd6e3'
    assert z['passed']and z['ROM_sha256']==target and json.loads(build.read_text())['passed']
    assert z['actual_Bill_full_RemainingDraw_calls']==640 and z['foreign_full_calls']==140 and z['helper_ABI_cases']==96 and z['genuine_IRQ_boundary_cases']==66
    files={Path(__file__),PARENT/'candidate.nes',PARENT/'candidate.dbg',PARENT/'source-manifest.json'}
    manifest=json.loads((a.packet/'source-manifest.json').read_text())
    for n,h in manifest.items():assert sha(a.packet/'source'/n)==h,n;files.add(a.packet/'source'/n)
    files.update(f for f in a.packet.iterdir()if f.is_file())
    for sub in ['controls-v1','controls-v2','controls-v3','controls-v4','canonical-build-v1']:
        files.update(f for f in(a.packet/sub).iterdir()if f.is_file()and f.suffix in ['.json','.log'])
    negative=D/'bill-capsule-hud-preparer-syntax-negative-v1';files.update(negative.iterdir())
    report=ROOT/'docs/qa/bill-lance-capsule-hud-source-2026-10-26.txt';files.add(report)
    roots=[ROOT/'tools/audit'/('bill_capsule_hud_'+s)for s in ['prepare_v1.py','controls_v1.py','controls_v2.py','controls_v3.py','controls_v4.py','freeze_v1.py']];seen=set()
    while roots:
        f=roots.pop()
        if f in seen:continue
        seen.add(f);files.add(f)
        for node in ast.walk(ast.parse(f.read_text(encoding='utf-8-sig'))):
            names=[node.module]if isinstance(node,ast.ImportFrom)else[v.name for v in node.names]if isinstance(node,ast.Import)else[]
            for name in names:
                if name:
                    other=ROOT/'tools/audit'/(name.split('.')[0]+'.py')
                    if other.is_file():roots.append(other)
    put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),sha256=sha(f),bytes=f.stat().st_size)for f in sorted(files)]))
    put(a.output/'proof.json',dict(prepared=True,source_only=True,native_run=False,ROM_sha256=target,parent_ROM_sha256=SHA,
        ROM=str(a.packet/'candidate.nes'),source=str(a.packet/'source'),source_files=len(manifest),changed_source=layout['changes'],changed_banks=layout['changed_banks'],
        source_controls_sha256=sha(c),fresh_build_proof_sha256=sha(build),helper_capacity_and_old_symbols=layout,
        exact_full_calls=640,foreign_full_calls=140,helper_ABI_cases=96,actual_IRQ_cases=66,
        extra_Bill_HUD_cycles=30,extra_foreign_HUD_cycles=29,no_current_native_or_composed_union_claim=True,
        controls_negative_packets=['controls-v1','controls-v2','controls-v3'],syntax_negative=str(negative),
        report_sha256=sha(report),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files)))
    payload={'source-only-proof.json':a.output/'proof.json','external-bindings.json':a.output/'manifest.json','implementation.patch':a.packet/'implementation.patch','layout.json':a.packet/'layout.json',
        'actual-CPU-controls.json':c,'fresh-build-proof.json':build,'report.txt':report}
    for name in ['src/remaining_weapons.s','src/entrypoint.s','src/bill_hud_anchor.s']:payload['source-overlay/'+name]=a.packet/'source'/name
    for sub in ['controls-v1','controls-v2','controls-v3']:payload['retained-negatives/'+sub+'.json']=a.packet/sub/'failure.json'
    payload['retained-negatives/initial-parser.json']=negative/'failure.json'
    rows=[]
    for name,f in payload.items():
        targetfile=a.public/name;targetfile.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,targetfile);rows.append(dict(path=name,source=str(f),sha256=sha(f),bytes=f.stat().st_size))
    owned=[ROOT/'tools/audit'/('bill_capsule_hud_'+s)for s in ['prepare_v1.py','controls_v1.py','controls_v2.py','controls_v3.py','controls_v4.py','freeze_v1.py']]+[report]
    (a.public/'OWNED-FILES.txt').write_text('\n'.join(str(f.relative_to(ROOT)).replace('\\','/')for f in owned)+'\n'+str(a.public.relative_to(ROOT)).replace('\\','/')+'/\n',encoding='utf-8')
    (a.public/'README.txt').write_text('SOURCE ONLY exact3b→9d Bill/Lance capsule relocation.34ROMbytes bank61; three source files, noRAM/CHR/oldPC changes.640Bill+140foreign full calls/96ABI/66IRQ and freshcanonical+ordinary hashes pass. Capsule x100..123/OAMy1..16 away headers. Extra30Bill/29foreign HUD cycles disclosed. Retained control-oracle/parser negatives are explicit; no native/union-result transfer or install. Public source overlay contains authored assembly only, no ROM/NSF/graphics/audio/settings/lossless payload.\n',encoding='utf-8')
    put(a.public/'manifest.json',dict(payloads=rows,stable_owned_files=[dict(path=str(f.relative_to(ROOT)).replace('\\','/'),sha256=sha(f),bytes=f.stat().st_size)for f in owned],source_readiness_sha256=sha(a.output/'proof.json')))
    print(json.dumps(dict(prepared=True,native_run=False,proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),public_manifest_sha256=sha(a.public/'manifest.json'),public_bytes=sum(f.stat().st_size for f in a.public.rglob('*')if f.is_file()))))


if __name__=='__main__':main()
