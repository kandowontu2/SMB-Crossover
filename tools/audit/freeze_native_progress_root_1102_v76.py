"""Compact exact direct-source checkpoints and an explicit Git stage list."""
import hashlib,json,re,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
import build_storage_guard_v1 as S
O=R/'build/native-progress-root-1102-v76';D=R/'docs/qa/checkpoints/2026-11-02'

def copy_packet(directory,manifest,archive,expected):
    assert sha(archive)==expected;dest=D/directory;dest.mkdir(exist_ok=True)
    q=json.loads(manifest.read_text());assert q['passed']
    mapping=q['members'];members={r['path']:r for r in mapping} if isinstance(mapping,list) else mapping
    with zipfile.ZipFile(archive) as z:
        assert set(z.namelist())==set(members)
        for name,row in members.items():
            data=z.read(name);assert hashlib.sha256(data).hexdigest()==row.get('SHA256',row.get('sha256')),name
            live=R/name
            if live.is_file():
                actual=live.read_bytes()
                if name.endswith('/performance-source-commit-files-v52.txt'):
                    assert data==actual.replace(b'\r\n',b'\n'),name
                else:assert data==actual,name
            else:assert name.startswith('inherited-source/'),name
    for source,name in [(archive,'inputs.zip'),(manifest,'receipt.json')]:
        if (dest/name).exists():assert sha(dest/name)==sha(source)
        else:(dest/name).write_bytes(source.read_bytes())
    return dest

def main():
    O.mkdir(exist_ok=True);storage=S.preflight(private_root=O,reserved_bytes=2_000_000,reserved_files=10,fresh=True)
    dk=R/'build/dkjr-native-source-1102-v2';perf=R/'build/bub-menu-candidate-1102-v2';destinations=[]
    for folder,manifest,archive,digest in [
        ('dkjr-native-ingress-v28',dk/'native-ingress-v28.json',dk/'native-ingress-v28-inputs.zip','e9ff4c904101a93dfd592f4873d1b599b61951b87e18b853c4707f94b9f79979'),
        ('dkjr-native-lifecycle-v35',dk/'native-lifecycle-v35.json',dk/'native-lifecycle-v35-inputs.zip','3e411f47eeb50f55992f9bf10eb7107651a623b8d138c26d1fe875bfec3aae5e'),
        ('bub-performance-v52',perf/'performance-source-v52.json',perf/'performance-source-v52.zip','796491e71d364568f27e6de53e5f3f68dcf6ecc747911ac4a2657acc533902ed')]:
        destinations.append(copy_packet(folder,manifest,archive,digest))
    names=['measure_bub_source_branches_1102_v47','prepare_bub_original_upgrades_1102_v48','check_bub_original_upgrades_1102_v49','trace_bub_branch_relocation_1102_v50','prepare_bub_original_upgrades_1102_v51','check_bub_original_upgrades_1102_v52','check_bub_powerup_ingress_1102_v53','prepare_bub_joint_rare_gate_1102_v54','check_bub_joint_powerup_ingress_1102_v55','prepare_bub_collecting_upgrades_1102_v56','compose_bub_collecting_gate_1102_v57','check_bub_collecting_powerups_1102_v58','check_bub_collecting_interrupts_1102_v59','check_bub_upgrade_lifecycle_1102_v60','prepare_bub_powerup_update_1102_v61','compose_bub_powerup_update_1102_v62','check_bub_upgrade_lifecycle_1102_v63','check_bub_nested_lag_1102_v64','prepare_bub_tail_gateways_1102_v65','compose_bub_tail_gateways_1102_v66','check_bub_tail_lifecycle_1102_v67','check_bub_tail_nested_lag_1102_v68','check_bub_tail_interrupts_1102_v69','check_bub_tail_cold_1102_v71','prepare_bub_upgrade_candidate_1102_v72','prepare_bub_upgrade_route_1102_v73','prepare_bub_earned_mushroom_1102_v74','prepare_bub_upgrade_pipe_1102_v75']
    root_scripts=[R/'tools/audit'/(name+'.py') for name in names]
    root_scripts += [Path(__file__),R/'tools/audit/grant_native_successors_root_1102_v70.py',R/'tools/audit/grant_dkjr_private_resources_root_1102_v20.py']
    files=list(root_scripts)+[R/'docs/qa/bub-original-upgrades-1102.md']
    for directory in (R/'build').iterdir():
        if directory.is_dir() and directory.name.startswith('bub-upgrades-root-'):
            for path in directory.rglob('*'):
                if path.is_file() and path.suffix in ['.json','.s','.cfg','.lbl','.bin','.lua'] and path.name!='capture-budget.json':files.append(path)
    files=list(dict.fromkeys(files));assert len(files)<700 and sum(p.stat().st_size for p in files)<8_000_000
    dest=D/'bub-original-upgrades-v76';assert not dest.exists();dest.mkdir();archive=dest/'inputs.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for path in sorted(files):z.writestr(path.relative_to(R).as_posix(),path.read_bytes())
    with zipfile.ZipFile(archive) as z:
        for path in files:assert z.read(path.relative_to(R).as_posix())==path.read_bytes()
    receipt=dict(passed=True,source_checkpoint_only=True,installed=False,installed_ROM_SHA256=sha(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')),private_candidate_SHA256='b7e2a161ea2781a8346b126b9c759f7c60f2583e2a18e58f8ca888d041c0bd53',archive_SHA256=sha(archive),archive_bytes=archive.stat().st_size,members=len(files),files={p.relative_to(R).as_posix():sha(p) for p in files},scope='Exact private root source, small compiled components and retained CPU/native negatives. No ROM/DBG/O/PNG/movie copies. b7e2 is NOT native-ready: actual earned-block bridge and full1-1 replay remain open;9cf stays installed. Helper frozen checkpoints are separate, not recursively expanded.')
    (dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');destinations.append(dest)
    stage={str(p.relative_to(R)).replace('\\','/') for p in root_scripts}|{'docs/qa/bub-original-upgrades-1102.md','docs/qa/continuation-current.json','docs/qa/allocations/dkjr-private-resources-1102-v20.json','docs/qa/allocations/joint-native-rare-gate-1102-v70.json','docs/qa/allocations/prince-post-return-lifetime-1102-v70.json'}
    manifests=[D/'dkjr-native-body-v10/manifest.json',dk/'admission-proposal-v20.json',dk/'native-ingress-v28.json',dk/'native-lifecycle-v35.json']
    for manifest in manifests:
        for row in json.loads(manifest.read_text())['source_files']:
            name=row['path'] if isinstance(row,dict) else row
            if isinstance(row,dict):assert sha(R/name)==row['SHA256'],name
            stage.add(name)
    stage.update(json.loads((perf/'performance-source-v52.json').read_text())['source_commit_files'])
    stage.update(json.loads((R/'build/prince-actor-1101-v1/post-return-checkpoint-v95.json').read_text())['explicit_source_commit_files'])
    for folder in destinations+[D/'dkjr-native-body-v10',D/'dkjr-admission-proposal-v20',D/'prince-post-return-v95']:
        stage.update(p.relative_to(R).as_posix() for p in folder.iterdir() if p.is_file())
    assert 'docs/qa/current-roster-progress-2026-10-27.json' not in stage
    (O/'stage-files.txt').write_text('\n'.join(sorted(stage))+'\n')
    out=dict(passed=True,checkpoint=dest.relative_to(R).as_posix(),root_members=len(files),root_archive_bytes=archive.stat().st_size,stage_files=len(stage),storage=storage,installed_ROM_SHA256=receipt['installed_ROM_SHA256']);(O/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
