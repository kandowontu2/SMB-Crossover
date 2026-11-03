"""Compact current69..71 measurements, including rejected SEC lead; no ROM."""
import hashlib,json,zipfile
from pathlib import Path
import build_storage_guard_v1 as G
R=Path(__file__).resolve().parents[2];O=R/'build/bub-menu-candidate-1102-v2'
sha=lambda data:hashlib.sha256(data).hexdigest()


def main():
    G.preflight(private_root=O,reserved_bytes=300000,reserved_files=3,fresh=True)
    scripts=[R/'tools/audit'/name for name in['profile_bub_current_bridge_1103_v69.py',
        'measure_bub_constant_reject_1103_v70.py','measure_bub_native_side_transport_1103_v71.py',Path(__file__).name]]
    proofs=[O/name for name in['current-bridge-profile-v69.json','constant-reject-v70-negative.json','native-side-v71-measurement.json']]
    data=[json.loads(f.read_text())for f in proofs]
    assert data[0]['passed']and data[1]['proposal_rejected']and data[2]['passed']
    assert not data[1]['passed']and not data[2]['CPU_qualified']and not data[2]['candidate_allowed']
    assert data[1]['actual_target_B57C']=='3860'
    for proof in data:
        for path,digest in proof['bindings'].items():assert sha((R/path).read_bytes())==digest,path
    files=scripts+proofs
    for stem in['constant-reject-v70-reproduce','constant-reject-v70-compact','constant-reject-v70-final',
                 'native-side-v71-reproduce','native-side-v71-compact','native-side-v71-final']:
        files.extend(O/(stem+suffix)for suffix in['.s','.cfg','.bin','.lbl'])
    commit=O/'transport-source-commit-files-v72.txt'
    commit.write_text('\n'.join(f.relative_to(R).as_posix()for f in scripts)+'\n')
    files.append(commit);assert all(f.exists()for f in files)
    members={f.relative_to(R).as_posix():f.read_bytes()for f in files}
    assert all(not name.endswith(('.nes','.dbg','.o','.png','.zip'))for name in members)
    archive=O/'transport-proposals-v72.zip';assert not archive.exists()
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for name,blob in members.items():z.writestr(name,blob)
    with zipfile.ZipFile(archive)as z:
        assert set(z.namelist())==set(members)
        assert all(z.read(name)==blob for name,blob in members.items())
    result=dict(passed=True,checkpoint_only=True,private_candidate_allowed=False,ROM_written=False,native=False,
        base_ROM_SHA256=data[2]['base_ROM_SHA256'],archive=dict(path=archive.relative_to(R).as_posix(),
            SHA256=sha(archive.read_bytes()),bytes=archive.stat().st_size,members=len(members)),
        source_commit_files=[f.relative_to(R).as_posix()for f in scripts],
        current_empty_idle_CPU=[row['mean_CPU']for row in data[0]['cases']if row['phase']=='idle'],
        current_empty_walk_CPU=[row['mean_CPU']for row in data[0]['cases']if row['phase']=='walk'],
        full_auth_checks_per_Main=13,full_auth_CPU_per_Main=10088,
        measured_native_side_saving_CPU=1939,cache_used=False,new_RAM_used=False,
        retained_negative='Rows9/34 literal SEC/RTS need valid headers; pre-auth reject shortcut is invalid.70 is intentionally negative, not a candidate.',
        scope='Currentcf7 profile and full-auth Side transport CPU-only proposal.4percent does not establish a video-frame budget crossing. No resident/native sweep or ROM approved. Old49/50 source funding is not assumed reusable with pending Prince130/DK79 common manager. Larger grouped/lifetime auth requires complete legal writer/constructor/cold/retire/IRQ closure.',
        members={name:dict(bytes=len(blob),SHA256=sha(blob))for name,blob in members.items()},
        external_read_only_inputs={str(f.relative_to(R)).replace('\\','/'):sha(f.read_bytes())for f in[
            R/'tools/audit/measure_bub_resident_compaction_1102_v49.py',
            R/'build/bub-initial-tier-1103-v87/proposal.json',R/'build/bub-initial-tier-1103-v87/private-image.bin',
            O/'head-source-v59.json',R/'docs/qa/checkpoints/2026-11-03/bub-head-source-v59/receipt.json']if f.exists()})
    receipt=O/'transport-proposals-v72.json';assert not receipt.exists();receipt.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,archive=result['archive'],receipt_SHA256=sha(receipt.read_bytes()),
        source_commit_list=commit.relative_to(R).as_posix(),task_storage=G.inventory(O,G.TASK_BYTES,G.TASK_FILES))))


if __name__=='__main__':main()
