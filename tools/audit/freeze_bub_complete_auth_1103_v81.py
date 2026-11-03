"""Freeze complete-auth source-only transport proposal and its bounded proofs."""
import hashlib
import json
import zipfile
from pathlib import Path
import build_storage_guard_v1 as G

R = Path(__file__).resolve().parents[2]
O = R / 'build/bub-menu-candidate-1102-v2'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    G.preflight(private_root=O, reserved_bytes=2_000_000, reserved_files=3, fresh=True)
    script_names = [
        'measure_bub_full_auth_helper_1103_v73.py',
        'measure_bub_complete_auth_transport_1103_v74.py',
        'measure_bub_direct_primitives_1103_v75.py',
        'measure_bub_shared_auth_funding_1103_v76.py',
        'check_bub_shared_auth_contracts_1103_v77.py',
        'check_bub_shared_auth_lifecycle_1103_v78.py',
        'check_bub_shared_auth_interrupts_1103_v79.py',
        'check_bub_shared_auth_nested_1103_v80.py',
        Path(__file__).name,
    ]
    scripts = [R / 'tools/audit' / name for name in script_names]
    proof_names = [
        'full-auth-v73-measurement.json',
        'complete-auth-v74-measurement.json',
        'direct-primitives-v75-measurement.json',
        'shared-auth-v76-funding.json',
        'shared-auth-v77-contracts.json',
        'shared-auth-v78-lifecycle.json',
        'shared-auth-v79-ISR.json',
        'shared-auth-v80-nested.json',
        'shared-auth-v79-initial-state-negative.json',
    ]
    proofs = [O / name for name in proof_names]
    data = [json.loads(path.read_text()) for path in proofs]
    assert all(q['passed'] and not q['candidate_allowed'] for q in data[:-1])
    assert not data[-1]['passed']
    external = {}
    for q in data[:-1]:
        for rel, expected in q['bindings'].items():
            path = R / rel
            assert path.is_file() and digest(path.read_bytes()) == expected, rel
            assert rel not in external or external[rel] == expected, rel
            external[rel] = expected
    assert data[6]['actual_ISR_counts'] == {'IRQ': 8127, 'FF': 9287}
    assert data[7]['replayed_nested_IRQs'] == 8607
    assert data[7]['reconstructed_FF_contexts'] == 134
    assert data[7]['minimum_ISR_SP'] == 126
    generated = []
    for stem in [
        'full-auth-v73-reproduce', 'full-auth-v73-final',
        'complete-auth-v74-kernel', 'direct-primitives-v75-kernel',
        'shared-auth-v76-Sh-reproduce', 'shared-auth-v76',
    ]:
        generated.extend(O / (stem + suffix) for suffix in ['.s', '.cfg', '.bin', '.lbl'])
    generated.extend(O / name for name in [
        'full-auth-v73-reproduce-extra.bin', 'full-auth-v73-final-extra.bin',
        'shared-auth-v76-Sh.bin', 'shared-auth-v76-extra.bin',
    ])
    commit = O / 'complete-auth-source-commit-files-v81.txt'
    archive = O / 'complete-auth-source-v81.zip'
    receipt = O / 'complete-auth-source-v81.json'
    assert all(not path.exists() for path in [commit, archive, receipt])
    commit.write_text('\n'.join(path.relative_to(R).as_posix() for path in scripts) + '\n')
    files = scripts + proofs + generated + [commit]
    assert all(path.is_file() for path in files)
    members = {path.relative_to(R).as_posix(): path.read_bytes() for path in files}
    assert len(members) == len(files)
    assert all(not name.endswith(('.nes', '.dbg', '.o', '.png', '.zip')) for name in members)
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, blob in members.items():
            z.writestr(name, blob)
    with zipfile.ZipFile(archive) as z:
        assert set(z.namelist()) == set(members)
        assert all(z.read(name) == blob for name, blob in members.items())
    previous = O / 'transport-proposals-v72.json'
    assert previous.is_file()
    result = dict(
        passed=True, checkpoint_only=True, CPU_only=True,
        candidate_allowed=False, ROM_written=False, installed=False,
        cache_used=False, new_RAM_used=False,
        installed_reference_SHA256='cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd',
        source_proposal_memory_SHA256=data[4]['current_source_proposal'],
        archive=dict(path=archive.relative_to(R).as_posix(), SHA256=digest(archive.read_bytes()),
                     bytes=archive.stat().st_size, members=len(members)),
        source_commit_files=[path.relative_to(R).as_posix() for path in scripts],
        unchanged_complete_auth_checks_per_Main=13,
        measured_Main_cases=data[4]['Main_cases'],
        actual_ISR_counts=data[6]['actual_ISR_counts'],
        nested_IRQs=data[7]['replayed_nested_IRQs'],
        nested_reconstructed_foreground_contexts=data[7]['reconstructed_FF_contexts'],
        minimum_nested_SP=data[7]['minimum_ISR_SP'],
        fixed_source_extents=data[3]['extents'],
        cookies_and_existing_15B_end_pad_unchanged=True,
        retained_negative=dict(path=proofs[-1].relative_to(R).as_posix(),
            scope='Initial oracle wrongly required native PPU latch preservation during setup IRQ. '
                  'Final79 instead compares every native PPU/CHR/audio result to the unchanged '
                  'handler executed from the identical interrupted state; CPU/source/native '
                  'RAM/scratch/SMC/live stack remain strict. No PPU normalization.'),
        earlier_checkpoint=dict(path=previous.relative_to(R).as_posix(), SHA256=digest(previous.read_bytes()),
            scope='69..71 current profile, retained rejected SEC lead and independent full-auth Side measurement; not rehydrated.'),
        remaining=[
            'Bind the complete actual external caller/reference closure, including outer FarCallCommon flag semantics, moved private auth entry, cookies and SMC references.',
            'Rebind and fund against the canonical combined Prince159/DK101 successor. Structural funding is not additive:101 already spends part of the76 savings. No footer padding is leased by this checkpoint.',
            'Root must approve a final exact private candidate before ROM placement or native validation. No video-frame rate improvement is claimed from CPU measurements.',
        ],
        members={name: dict(bytes=len(blob), SHA256=digest(blob)) for name, blob in members.items()},
        external_read_only_inputs={rel: expected for rel, expected in sorted(external.items()) if rel not in members},
    )
    receipt.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(passed=True, archive=result['archive'], receipt=receipt.relative_to(R).as_posix(),
        receipt_SHA256=digest(receipt.read_bytes()), source_commit_list=commit.relative_to(R).as_posix(),
        task_storage=G.inventory(O, G.TASK_BYTES, G.TASK_FILES))))


if __name__ == '__main__':
    main()
