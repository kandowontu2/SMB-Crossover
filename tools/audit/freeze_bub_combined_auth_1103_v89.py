"""Compact exact82..88 combined full-auth proposal, never a ROM."""
import hashlib,json,zipfile
from pathlib import Path
import build_storage_guard_v1 as G

R=Path(__file__).resolve().parents[2]
O=R/'build/bub-menu-candidate-1102-v2'
sha=lambda data:hashlib.sha256(data).hexdigest()


def main():
    G.preflight(private_root=O,reserved_bytes=2_000_000,reserved_files=3,fresh=True)
    names=['check_bub_complete_auth_ingress_1103_v82.py','measure_bub_combined_auth_1103_v83.py',
        'check_bub_combined_auth_contracts_1103_v84.py','check_bub_combined_auth_lifecycle_1103_v85.py',
        'check_bub_combined_auth_interrupts_1103_v86.py','check_bub_combined_auth_nested_1103_v87.py',
        'audit_bub_combined_auth_references_1103_v88.py',Path(__file__).name]
    scripts=[R/'tools/audit'/name for name in names]
    proofs=[O/name for name in ['complete-auth-v82-ingress.json','combined-auth-v83-measurement.json',
        'combined-auth-v84-contracts.json','combined-auth-v85-lifecycle.json','combined-auth-v86-ISR.json',
        'combined-auth-v87-nested.json','combined-auth-v88-references.json']]
    data=[json.loads(path.read_text())for path in proofs]
    assert all(q['passed']and not q['candidate_allowed']for q in data)
    external={}
    for q in data:
        for rel,digest in q['bindings'].items():
            assert sha((R/rel).read_bytes())==digest,rel
            assert rel not in external or external[rel]==digest,rel
            external[rel]=digest
    assert data[4]['actual_ISR_counts']==dict(IRQ=8968,FF=10142)
    assert data[5]['replayed_nested_IRQs']==10099 and data[5]['reconstructed_FF_contexts']==140
    assert data[5]['minimum_ISR_SP']==126
    generated=[O/('combined-auth-v83'+suffix)for suffix in ['.s','.cfg','.bin','.lbl','-extra.bin','-Sh.bin']]
    generated.extend(O/('combined-auth-v83-selector'+suffix)for suffix in ['.s','.cfg','.bin','.lbl'])
    archive=O/'combined-auth-source-v89.zip';receipt=O/'combined-auth-source-v89.json'
    commit=O/'combined-auth-source-commit-files-v89.txt'
    assert not any(path.exists()for path in [archive,receipt,commit])
    commit.write_text('\n'.join(path.relative_to(R).as_posix()for path in scripts)+'\n')
    files=scripts+proofs+generated+[commit]
    members={path.relative_to(R).as_posix():path.read_bytes()for path in files}
    assert len(members)==len(files)
    assert not any(name.endswith(('.nes','.dbg','.o','.png','.zip'))for name in members)
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for name,blob in members.items():z.writestr(name,blob)
    with zipfile.ZipFile(archive)as z:
        assert set(z.namelist())==set(members)
        assert all(z.read(name)==blob for name,blob in members.items())
    previous=[O/'complete-auth-source-v81.json',O/'transport-proposals-v72.json']
    result=dict(passed=True,checkpoint_only=True,source_and_CPU_only=True,candidate_allowed=False,
        ROM_written=False,native_tested=False,installed=False,cache_used=False,new_RAM_used=False,
        canonical_source='DKcombined101 Prince159/DK90/currentBubcf7; source-only, no pending old149 positive assumption',
        source_proposal_receipt_SHA256=sha(proofs[1].read_bytes()),
        corrected81_field='81 source_proposal_memory_SHA256 denotes the76 funding receipt hash, not a memory image; retained immutable and explicitly corrected by82.',
        source_extents=dict(manager=[0xae00,0xb013],extra=[0xab72,0xabd3],selector=[0xa740,0xa7f0],Sh_check=[0xa800,0xa849]),
        fixed_external_entries=data[6]['preserved_external_manager_entries'],
        cookies_unchanged=True,selector_unchanged=True,complete_auth_checks_per_Main=13,
        measured_Main_cases=data[2]['Main_cases'],
        actual_IRQ_FF=data[4]['actual_ISR_counts'],nested_actual_IRQs=10099,
        reconstructed_deepest_FF_contexts=140,minimum_nested_SP=126,
        source_funding=data[1]['source_funding'],
        archive=dict(path=archive.relative_to(R).as_posix(),bytes=archive.stat().st_size,
            members=len(members),SHA256=sha(archive.read_bytes())),
        source_commit_files=[path.relative_to(R).as_posix()for path in scripts],
        earlier_exact_checkpoint_receipts={path.relative_to(R).as_posix():sha(path.read_bytes())for path in previous},
        remaining=['Root review/typed import boundary acceptance and exact shared-span private candidate grant. No global arbitrary indirect-pointer or legal-writer/auth-cache claim.',
            'No emulator/video-frame timing/native gameplay or delivery has been performed for this optimization. A4251CPU saving does not establish crossing a video-frame budget.',
            'Any newer canonical Prince/DK payload/shared manager changes require exact preimage/cookie/reconstruction rebind before candidate composition.'],
        members={name:dict(bytes=len(blob),SHA256=sha(blob))for name,blob in members.items()},
        external_read_only_inputs={rel:digest for rel,digest in sorted(external.items())if rel not in members})
    receipt.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,archive=result['archive'],receipt=receipt.relative_to(R).as_posix(),
        receipt_SHA256=sha(receipt.read_bytes()),source_commit_list=commit.relative_to(R).as_posix(),
        task_storage=G.inventory(O,G.TASK_BYTES,G.TASK_FILES))))


if __name__=='__main__':main()
