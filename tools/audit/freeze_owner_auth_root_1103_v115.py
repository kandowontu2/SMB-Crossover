"""Verify and retain completed DK entrance/combined and complete-auth packets."""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'build/owner-auth-root-freeze-1103-v115'
PACKETS = (
    ('build/dkjr-native-source-1102-v2/native-entrance-ready-v100.json','dkjr-entrance-ready-v100'),
    ('build/dkjr-native-source-1102-v2/native-combined-fit-v109.json','dkjr-combined-fit-v109'),
    ('build/bub-menu-candidate-1102-v2/complete-auth-source-v81.json','bub-complete-auth-v81'),
    ('build/bub-menu-candidate-1102-v2/combined-auth-source-v89.json','bub-combined-auth-v89'),
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(exist_ok=False)
    stage = [Path(__file__).relative_to(ROOT).as_posix()]
    results = []
    for relative,name in PACKETS:
        manifest = ROOT/relative
        q = json.loads(manifest.read_text())
        assert q['passed'] and not q['ROM_written'] and not q['installed']
        if isinstance(q['archive'],dict):
            a = q['archive'];archive = ROOT/a['path'];expected_hash=a['SHA256'];expected_bytes=a['bytes']
            members = [dict(path=p,**v) for p,v in q['members'].items()]
            sources = q['source_commit_files']
            assert not q['candidate_allowed'] and not q['cache_used'] and not q['new_RAM_used']
        else:
            archive = ROOT/q['archive'];expected_hash=q['archive_SHA256'];expected_bytes=q['archive_bytes']
            members = q['members'];sources = [r['path'] for r in q['source_files']]
            assert not q['qualified'] and not q['native_owner_admitted'] and not q['menu_grant']
        assert archive.stat().st_size == expected_bytes and sha(archive.read_bytes()) == expected_hash
        with ZipFile(archive) as z:
            assert len(z.namelist()) == len(members)
            for row in members:
                relative = row['path'].replace('\\','/')
                blob = z.read(relative)
                assert len(blob) == row['bytes'] and sha(blob) == row['SHA256'],relative
                assert (ROOT/relative).read_bytes() == blob,relative
        dest = ROOT/'docs/qa/checkpoints/2026-11-03'/name
        dest.mkdir(parents=True,exist_ok=False)
        (dest/'inputs.zip').write_bytes(archive.read_bytes())
        (dest/'helper-manifest.json').write_bytes(manifest.read_bytes())
        result = dict(passed=True,source_CPU_only=True,installed=False,ROM_produced=False,
            checkpoint=dest.relative_to(ROOT).as_posix(),archive_bytes=expected_bytes,
            archive_SHA256=expected_hash,members=len(members),source_files=sources,
            limits='Completed source/CPU packet preserved byte-exact; no root approval of shared placement, no native stage/helper crossing or installation inferred. Full goal remains active.')
        if name == 'bub-complete-auth-v81':
            result['field_erratum'] = 'source_proposal_memory_SHA256 is a funding-receipt SHA256, not a ROM/memory hash. Original81 is immutable; corrected82/89 semantics retained.'
        (dest/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
        stage += [*sources,*(f.relative_to(ROOT).as_posix() for f in
            (dest/'inputs.zip',dest/'helper-manifest.json',dest/'receipt.json'))]
        results.append(result)
    handoff = ROOT/'docs/qa/continuation-current.json'
    current = json.loads(handoff.read_text())
    current['dkjr_current_source_1102'].update(
        entrance_anchor_checkpoint=results[0]['checkpoint'],
        entrance_anchor_status='READY1_TO2_ORIGINAL_ENTRANCE_PIPE_LIFECYCLE_AND_ISR_PASS_NO_NATIVE',
        current159_combined_checkpoint=results[1]['checkpoint'],
        current159_combined_status='FOUR_OWNER_SOURCE_FIT_COLD_FOREIGN_HOT_ISR_PASS_NO_PLACEMENT_GRANT')
    current['bub_performance_current_1102'].update(
        complete_auth_checkpoint=results[2]['checkpoint'],
        combined_auth_checkpoint=results[3]['checkpoint'],
        combined_auth_status='SOURCE_CPU_4251CYCLES_PER_MAIN_SAVING_NO_CACHE_NO_ROM',
        combined_auth_scope='Exact531/97/176/73 source83 overcombinedDK101/Prince159;13completechecks retained, realIRQ/FF/nested/source lifecycle pass. Roottypedimport/spanreview and actualnativevalidation remain. No installed lag/frame-rate claim.')
    handoff.write_text(json.dumps(current,indent=2)+'\n')
    stage.append(handoff.relative_to(ROOT).as_posix())
    (OUT/'stage-files.txt').write_text('\n'.join(dict.fromkeys(stage))+'\n')
    (OUT/'receipt.json').write_text(json.dumps(dict(passed=True,packets=results),indent=2)+'\n')
    print(json.dumps(dict(passed=True,packets=[{k:v for k,v in r.items() if k not in ('source_files','limits')} for r in results]),indent=2))


if __name__=='__main__':
    main()
