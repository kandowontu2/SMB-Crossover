"""Freeze finite private3cee asset relocation source/CPU/readiness packet."""
from pathlib import Path
import ast,difflib,hashlib,json,shutil,sys,zipfile
from py65.devices import mpu6502

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P=D/'smb3-assets-current3cee-v2';BASE=D/'root-chip-hud-composed-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ready=P/'ready-v2';ready.mkdir(exist_ok=False);(ready/'tools').mkdir()
    parent='3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'
    candidate='b86bfa95032a54837fbd1802d60659aaca9dfa8c55a713cc8a58a58ef0a594f6'
    assert sha(BASE/'candidate.nes')==parent and sha(P/'candidate.nes')==candidate
    source=json.loads((P/'source-manifest.json').read_text());old=json.loads((BASE/'source-manifest.json').read_text())
    assert source.keys()==old.keys()
    for n,h in source.items():assert sha(P/'source'/n)==h,n
    changes=[n for n in source if source[n]!=old[n]];assert changes==['smb1base-mmc5-expanded.cfg']
    noninputs=[n for n in old if n in ['candidate.nes','candidate.dbg','candidate.lbl','candidate.map'] or '__pycache__' in Path(n).parts]
    assert len(noninputs)==5,noninputs
    live=[n for n,h in old.items()if n not in noninputs and (not(R/n).is_file()or sha(R/n)!=h)]
    assert not live,('ROOT no longer matches frozen production source',live)
    with zipfile.ZipFile(ready/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n in sorted(source):z.write(P/'source'/n,n)
    with zipfile.ZipFile(ready/'source.zip')as z:
        assert len(z.namelist())==len(source)
        for n,h in source.items():assert hashlib.sha256(z.read(n)).hexdigest()==h,n
    patch=''
    for n in changes:
        before=(BASE/'source'/n).read_bytes().decode().splitlines(keepends=True)
        after=(P/'source'/n).read_bytes().decode().splitlines(keepends=True)
        patch+=''.join(difflib.unified_diff(before,after,fromfile='a/'+n,tofile='b/'+n))
    (ready/'review.patch').write_bytes(patch.encode())
    report=R/'docs/qa/smb3-asset-relocation-2026-10-26.txt'
    shutil.copyfile(report,ready/report.name)
    own=sorted((R/'tools/audit').glob('smb3_asset_relocation_*'))
    own=[q for q in own if q.is_file()and not q.name.endswith('.pyc')]
    for q in own:shutil.copyfile(q,ready/'tools'/q.name)
    # Direct/imported local Python dependencies, including actual CPU model.
    deps=set(own);pending=[q for q in own if q.suffix=='.py']
    while pending:
        path=pending.pop()
        tree=ast.parse(path.read_text())
        names=[]
        for q in ast.walk(tree):
            if isinstance(q,ast.ImportFrom)and q.module:names.append(q.module)
            elif isinstance(q,ast.Import):names.extend(x.name for x in q.names)
        for n in names:
            for local in [R/'tools/audit'/(n+'.py'),R/'tools'/(n+'.py')]:
                if local.is_file()and local not in deps:deps.add(local);pending.append(local)
    deps.update([R/'tools/build_mmc5_expanded.py',R/'tools/prepare_cv3_dmc_mirror.py',Path(sys.executable),Path(mpu6502.__file__),report,BASE/'candidate.nes',BASE/'candidate.dbg',BASE/'candidate.lbl',BASE/'candidate.map',BASE/'source-manifest.json'])
    # Bind the actual assembler/linker toolchain and all packaged runtime libs.
    deps.update(q for q in (R/'tools/Windows/cc65').rglob('*')if q.is_file())
    for n in ['root-chip-native-adapter-v6','chip-hot-control-v5']:
        deps.update([D/n/'candidate.nes',D/n/'candidate.dbg',D/n/'candidate.map',D/n/'source/smb1base-mmc5-expanded.cfg'])
    proofs=['proof.json','cpu-full-v4/proof.json','irq-lifts-v1/proof.json','reference-bytes-v1/proof.json','build-controls-v1/proof.json']
    for n in proofs:
        q=json.loads((P/n).read_text());assert q['passed'] is True,n
        if'candidate_ROM_sha256'in q:assert q['candidate_ROM_sha256']==candidate
    negatives=dict(
        packet_v1=dict(kind='Metadata checker compared copied non-input candidate artifacts and Python cache against liveROOT; correct source input identity excludes exactly those five named files. No game source mismatch.'),
        prepare_v1=dict(kind='Real linker segment-order failure; no successful candidate',directory=str(D/'smb3-assets-current3cee-v1'),original_output=str(D/'smb3-assets-current3cee-v1/build-command.json')),
        cpu_v1=dict(kind='Parse only; zero executed cases',retained_source='tools/smb3_asset_relocation_cpu_v1.py.failed.txt',original_terminal_output_saved=False),
        cpu_v2=dict(kind='Checker omitted genuine HpNativeDrawLo[0]/Hi[0] snapshot translation',source='tools/smb3_asset_relocation_cpu_v2.py',original_terminal_output_saved=False,
                    observed_difference=dict(HpNativeDrawLo0=[0,64],HpNativeDrawHi0=[192,195]),
                    native_source_owner='src/native_platform16_v2.s::HpPrepareNativePointers',
                    assertion_preserved='Full pointer identity compared after explicit genuine data relocation, not omitted'),
        cpu_v3=dict(kind='406 successful pilot cases, no IRQ called; unused draft IRQ branch restored cells',replacement='v4 removes restoration before real IRQ tests; separate IRQ-v1 executes no restoration'))
    (ready/'negative-classification.json').write_text(json.dumps(negatives,indent=2)+'\n')
    commands=dict(
        prepare=[sys.executable,str(R/'tools/audit/smb3_asset_relocation_prepare_v2.py'),'--output','<new external output>'],
        cpu=[sys.executable,str(R/'tools/audit/smb3_asset_relocation_cpu_v4.py'),'--parent',str(BASE/'candidate.nes'),'--candidate',str(P/'candidate.nes'),'--output','<new external CPU output>'],
        irq=[sys.executable,str(R/'tools/audit/smb3_asset_relocation_irq_v1.py'),'--parent',str(BASE/'candidate.nes'),'--candidate',str(P/'candidate.nes'),'--output','<new external IRQ output>'],
        references=[sys.executable,str(R/'tools/audit/smb3_asset_relocation_references_v1.py'),'--parent',str(BASE/'candidate.nes'),'--candidate',str(P/'candidate.nes'),'--output','<new external reference output>'],
        controls=[sys.executable,str(R/'tools/audit/smb3_asset_relocation_controls_v1.py'),'--packet','<new prepared packet directory>'])
    (ready/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    (ready/'dependencies.json').write_text(json.dumps({str(q):sha(q)for q in sorted(deps)},indent=2)+'\n')
    # Every actual receipt, launch record and compact case file is cataloged;
    # no huge build objects, ROM or NSF is copied into Git/workspace here.
    catalog={str(q):sha(q)for q in P.rglob('*')if q.is_file()and q.parent!=ready and'candidate-objects'not in q.parts and not any(p.endswith('-objects')for p in q.parts)}
    catalog.update({str(q):sha(q)for q in ready.rglob('*')if q.is_file()})
    for q,h in catalog.items():assert sha(q)==h,q
    (ready/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
    proof=dict(passed=True,private=True,native_run=False,adopted=False,active_SMB3_driver=False,
               parent_ROM_sha256=parent,candidate_ROM_sha256=candidate,changed_source=changes,
               source_members=len(source),source_archive_sha256=sha(ready/'source.zip'),catalog_files=len(catalog),catalog_sha256=sha(ready/'catalog.json'),
               dependency_files=len(deps),dependencies_sha256=sha(ready/'dependencies.json'),owned_tools=len(own),
               fresh_proofs={n:sha(P/n)for n in proofs},ROOT_production_inputs_exact_parent=True,non_input_copied_artifacts=noninputs,
               commands_sha256=sha(ready/'commands.json'),negative_classification_sha256=sha(ready/'negative-classification.json'),
               report_sha256=sha(report),review_patch_sha256=sha(ready/'review.patch'),
               scope='Config-only three-asset relocation. Source/CPU readiness, not native performance/adoption. Full authentic SMB3 driver, samples and cadence remain future work. Positive indexed-read costs retained.')
    (ready/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
