"""Freeze exact finite unused SMB3 core source/CPU packet; no deployment."""
from pathlib import Path
import ast,difflib,hashlib,json,shutil,sys,zipfile
import py65

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P=D/'smb3-native-core-v5';BASE=D/'smb3-assets-current3cee-v2';LIVE=D/'root-chip-hud-composed-v1'
T=D/'smb3-original-music-closure-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ready=P/'ready-v1';ready.mkdir(exist_ok=False);(ready/'tools').mkdir()
    assert sha(P/'candidate.nes')=='a4be8e02de0f8c0c43e5a7c94e4719e8b62c2ae80c1b1769978b06e73f2cac98'
    old=json.loads((BASE/'source-manifest.json').read_text())
    files={q.relative_to(P/'source').as_posix():sha(q)for q in(P/'source').rglob('*')if q.is_file()}
    for n,h in old.items():assert sha(BASE/'source'/n)==h,n
    changed=[n for n in old if files[n]!=old[n]];assert set(changed)=={'smb1base-mmc5-expanded.cfg','src/entrypoint.s'}
    added=sorted(set(files)-set(old));assert added==['audio/smb3-native/clone70.bin','audio/smb3-native/clone97.bin','audio/smb3-native/source-payload.bin','src/smb3_native_payload.s','src/smb3_native_standalone.s'],added
    (ready/'source-bindings.json').write_text(json.dumps(files,indent=2)+'\n')
    with zipfile.ZipFile(ready/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n in sorted(files):z.write(P/'source'/n,n)
    with zipfile.ZipFile(ready/'source.zip')as z:
        assert len(z.namelist())==len(files)
        for n,h in files.items():assert hashlib.sha256(z.read(n)).hexdigest()==h,n
    patch=''
    for n in changed+[q for q in added if q.endswith('.s')]:
        before=(BASE/'source'/n).read_bytes().decode().splitlines(keepends=True)if n in old else[]
        after=(P/'source'/n).read_bytes().decode().splitlines(keepends=True)
        patch+=''.join(difflib.unified_diff(before,after,fromfile='a/'+n if n in old else'/dev/null',tofile='b/'+n))
    (ready/'review.patch').write_bytes(patch.encode())
    proof=json.loads((P/'cpu-full-v3/proof.json').read_text());assert proof['passed']and proof['calls']==216012 and proof['ordered_original_APU_stores']==957715
    controls=json.loads((P/'controls-v1/proof.json').read_text());assert controls['passed']
    samples={};union=set();requested=0
    for row in proof['roles']:
        requested+=row['physical_DMC_sample_checks']
        for s in row['samples']:
            k=(s['source_first'],s['bytes']);samples[k]=s['sha256'];union.update(range(k[0],sum(k)))
    expected=json.loads((T/'dynamic-closure.json').read_text());wanted={i for lo,hi in expected['DPCM_ranges_inclusive']for i in range(lo,hi+1)}
    assert union==wanted and len(union)==3780 and len(samples)==7 and requested==5007
    (ready/'sample-union.json').write_text(json.dumps(dict(passed=True,actual_translated_sample_requests=requested,original_sample_union_bytes=len(union),seven_exact_profiles=[dict(source_first=k[0],bytes=k[1],sha256=v)for k,v in sorted(samples.items())],derivation='Union of actual assembled physical sample checks logged by role. Each source event/maps/length/control is separately exact against the complete golden stream.'),indent=2)+'\n')
    live=json.loads((LIVE/'source-manifest.json').read_text());noninputs=[n for n in live if n in ['candidate.nes','candidate.dbg','candidate.lbl','candidate.map']or'__pycache__'in Path(n).parts]
    for n,h in live.items():
        if n not in noninputs:assert sha(R/n)==h,('ROOT production changed',n)
    report=R/'docs/qa/smb3-native-core-2026-10-26.txt';shutil.copyfile(report,ready/report.name)
    own=sorted(q for q in(R/'tools/audit').glob('smb3_native_core_*')if q.is_file())
    for q in own:shutil.copyfile(q,ready/'tools'/q.name)
    deps=set(own);pending=[q for q in own if q.suffix=='.py']
    while pending:
        q=pending.pop();tree=ast.parse(q.read_text());names=[]
        for n in ast.walk(tree):
            if isinstance(n,ast.ImportFrom)and n.module:names.append(n.module)
            elif isinstance(n,ast.Import):names.extend(v.name for v in n.names)
        for name in names:
            for local in [R/'tools/audit'/(name+'.py'),R/'tools'/(name+'.py')]:
                if local.is_file()and local not in deps:deps.add(local);pending.append(local)
    deps.update([report,R/'tools/build_mmc5_expanded.py',R/'tools/prepare_cv3_dmc_mirror.py',Path(sys.executable),BASE/'candidate.nes',BASE/'candidate.dbg',BASE/'source-manifest.json',BASE/'ready-v3/receipt.json',LIVE/'source-manifest.json',T/'proof.json',T/'dynamic-closure.json',R/'reference/new-roster-audio/mario3/crossover-named.nsf'])
    for folder in [R/'tools/Windows/cc65',Path(py65.__file__).parent]:deps.update(q for q in folder.rglob('*')if q.is_file()and'__pycache__'not in q.parts)
    deps.update(q for q in T.glob('*/*')if q.is_file()and q.name in ['calls.jsonl.gz','footprint.json'])
    (ready/'dependencies.json').write_text(json.dumps({str(q):sha(q)for q in sorted(deps)},indent=2)+'\n')
    negative=dict(
        prepare_v1='Bound check rejected E851 outside previous conservative span; no build.',
        prepare_v2='Exploratory direct CFG misclassified unreachable pitch-table fallthroughE83A; no build/static closure.',
        prepare_v3='Exploratory classifier similarly rejected adjacent dataA70D; no build/static closure.',
        prepare_v4='Assembles4029B, but actual4012 request clobbered by PHX/PHY macro; a4be v5 stores/reloads originalA before macros.',
        CPU_v1='Raw py65 B differs after PHP/PLP; v2 compares all physical NV-DIZC flags withCF, retaining ABI/source assertions.',
        CPU_v2='Projection mistakenly assumed CurrentBank outside excluded source stack; actual145 is already outside original RAM hash.',
        CPU_v3_on_v4='Retained first actual request trap, normaltick1, PCDB4B. No source-output assertion weakened.',
        preserved_artifacts=[str(D/'smb3-native-core-v4/cpu-pilot-v1/failure.json'),str(D/'smb3-native-core-v4/cpu-pilot-v2/failure.json'),str(D/'smb3-native-core-v4/cpu-pilot-v3/failure.json')],
        early_producer_terminal_failures_not_written_as_original_log=True)
    (ready/'negative-classification.json').write_text(json.dumps(negative,indent=2)+'\n')
    commands=dict(prepare=[sys.executable,str(R/'tools/audit/smb3_native_core_prepare_v5.py'),'--output','<new external packet>'],
                  CPU=[sys.executable,str(R/'tools/audit/smb3_native_core_cpu_v3.py'),'--rom',str(P/'candidate.nes'),'--output','<new external CPU output>'],
                  controls=[sys.executable,str(R/'tools/audit/smb3_native_core_controls_v1.py'),'--packet','<new external prepared packet>'])
    (ready/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    catalog={str(q):sha(q)for q in P.rglob('*')if q.is_file()and not any(x.endswith('-objects')for x in q.parts)}
    catalog.update({str(q):sha(q)for q in ready.rglob('*')if q.is_file()})
    catalog.update({str(q):sha(q)for v in [1,2,3,4]for q in(D/f'smb3-native-core-v{v}').glob('cpu-*/*.json')if q.is_file()})
    for path,h in catalog.items():assert sha(path)==h,path
    (ready/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
    result=dict(passed=True,source_only=True,native_run=False,installed=False,host_integration=False,
                ROM_sha256=sha(P/'candidate.nes'),asset_parent_ROM_sha256=sha(BASE/'candidate.nes'),adopted_grandparent_ROM_sha256=sha(LIVE/'candidate.nes'),
                source_members=len(files),changed_existing_source=changed,added_source_and_assets=added,
                source_bindings_sha256=sha(ready/'source-bindings.json'),source_archive_sha256=sha(ready/'source.zip'),
                owned_tools=len(own),dependencies=len(deps),dependencies_sha256=sha(ready/'dependencies.json'),catalog_files=len(catalog),catalog_sha256=sha(ready/'catalog.json'),
                ready_proofs={str(q.relative_to(P)):sha(q)for q in[P/'proof.json',P/'cpu-full-v3/proof.json',P/'controls-v1/proof.json',ready/'sample-union.json']},
                report_sha256=sha(report),review_patch_sha256=sha(ready/'review.patch'),commands_sha256=sha(ready/'commands.json'),ROOT_actual_production_inputs_unchanged=True,
                limits='Storage fits and fixed12 cold source/CPU/sample fidelity only. High measured reader cost, host borrowing/shared ownership/preemption/lifecycle/native deadlines and71-song reachability remain unqualified. No adoption or further scope implied.')
    (ready/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
